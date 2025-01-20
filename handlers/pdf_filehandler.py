from tqdm import tqdm
import numpy as np
import hashlib
from qdrant_client.models import PointStruct
import uuid
import asyncio
import os
from pdf2image import convert_from_path
import time
from colpali_engine.models import ColQwen2, ColQwen2Processor
from qdrant_client import QdrantClient, models
from watchdog.events import FileSystemEventHandler
import stamina
import torch

# Check if GPU is available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Set the dtype based on the device
if device.type == "cuda":
    dtype = torch.bfloat16  # Recommended dtype for GPUs
else:
    dtype = torch.float32  # Default to float32 for CPU (you can use other types if needed)

# Initialize the sentence embedding model
colqwen_model = ColQwen2.from_pretrained(
    "vidore/colqwen2-v1.0",
    torch_dtype=dtype,        # Set the dtype
    device_map=device,        # Automatically select device
).eval()

colqwen_proc = ColQwen2Processor.from_pretrained("vidore/colqwen2-v1.0")

# Define the collection name for Qdrant
collection_name = "onprem_llm_collection"

# Initialize Qdrant client in server mode
qdrant_client = QdrantClient(host="qdrant", port=6333)

if not qdrant_client.collection_exists(collection_name):
  qdrant_client.create_collection(
      collection_name=collection_name,
      vectors_config=models.VectorParams(
          size=128,
          distance=models.Distance.COSINE,
          on_disk=True,
          multivector_config=models.MultiVectorConfig(
              comparator=models.MultiVectorComparator.MAX_SIM
          ),
          quantization_config=models.BinaryQuantization(
              binary=models.BinaryQuantizationConfig(
                  always_ram=True
              ),
          ),
      ),
  )

@stamina.retry(on=Exception, attempts=3)
def upsesrt_to_qdrant(batch):
    try:
        qdrant_client.upsert(
            collection_name=collection_name,
            points=batch,
            wait=True
        )
    except Exception as e:
        print(e)
        pass

if not os.path.exists("images"):
    os.mkdir("images")


limit = 100

scroll_response = qdrant_client.scroll(
    collection_name=collection_name,
    limit=limit
)
points, scroll_id = scroll_response 
images_hashes = []

for point in points:
    image_hash = point.payload.get('image_hash') 
    if image_hash:
        images_hashes.append(image_hash)

while scroll_id:
    scroll_response = qdrant_client.scroll(
        collection_name=collection_name,
        limit=limit,
        offset=scroll_id 
    )
    points, scroll_id = scroll_response 

    if not points:
        print("No more points returned. Ending scroll.")
        break

    for point in points:
        image_hash = point.payload.get('image_hash') 
        if image_hash:
            images_hashes.append(image_hash)

class PDFHandler(FileSystemEventHandler):
    """
    Handles new PDF files created in the monitored directory by:
    - Waiting for the file to be fully written to disk.
    - Storing the embeddings in the Qdrant vector database.
    """

    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith(".pdf"):
            # Skip temporary or incomplete files
            if "~BROMIUM" in event.src_path:
                print(f"Skipping temporary file: {event.src_path}")
                return

            print(f"New PDF file detected: {event.src_path}")

            # Wait until the file is fully written to disk
            self.wait_for_fileready(event.src_path)

            # Process the PDF file for embedding and indexing
            asyncio.run(self.process_pdf_for_embeddings(event.src_path))

            print(f"Processed and indexed new PDF: {event.src_path}")

    def wait_for_fileready(self, path, timeout=30):
        start_time = time.time()
        last_size = -1
        stable_count = 0

        while True:
            current_size = os.path.getsize(path)

            # Check if file size is stable
            if current_size == last_size:
                stable_count += 1
            else:
                stable_count = 0

            # File is ready if size is stable for 3 consecutive checks
            if stable_count > 2:
                return

            # Timeout reached
            if (time.time() - start_time) > timeout:
                print("Timeout reached while waiting for file to be ready.")
                return

            last_size = current_size
            time.sleep(1)

    async def process_pdf_for_embeddings(self, pdf_path):
        pdf_images = convert_from_path(pdf_path)
        pbar = tqdm(enumerate(pdf_images), total=len(pdf_images))
        points = []

        for i, image in pbar:
            # Convert the image to bytes and generate a hash
            image_bytes = np.asarray(image).tobytes()
            image_hash = hashlib.sha256(image_bytes).hexdigest()

            # Check if this image hash already exists in the Qdrant collection
            if not self.check_image_exists_in_qdrant(image_hash):
                with torch.no_grad():
                    # Process the image and get embeddings
                    processed_images = colqwen_proc.process_images([image]).to(colqwen_model.device)
                    image_embeddings = colqwen_model(**processed_images)
                    multivector_embeddings = image_embeddings.cpu().float().numpy().tolist()

                    # Generate a unique ID for the image
                    id = str(uuid.uuid4())

                    # Save the image if needed
                    image.save(f"images/{id}.jpg")

                    vector = multivector_embeddings[0]
                    point_struct = PointStruct(
                        id=id,
                        vector=vector,
                        payload={"image_hash": image_hash},
                    )
                    points.append(point_struct)

        if points:
            upsesrt_to_qdrant(points)
        print(f"Processed and indexed: {pdf_path}")

    def check_image_exists_in_qdrant(self, image_hash):
        if image_hash in images_hashes:
            return True
        return False
