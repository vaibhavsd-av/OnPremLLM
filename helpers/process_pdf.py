from qdrant_client import QdrantClient, models
from pdf2image import convert_from_path
import stamina
import torch
from colpali_engine.models import ColQwen2, ColQwen2Processor
import numpy as np

pdf_path = "docs/Agivant - Azure Optimization & Acceleration Framework.pdf"

pdf_images = convert_from_path(pdf_path)[0:1]


qdrant_client = QdrantClient(url="http://localhost:6333")


collection_name = "onprem_llm_collection"


colqwen_model = ColQwen2.from_pretrained(
    "vidore/colqwen2-v1.0",
    torch_dtype=torch.bfloat16,
    device_map="cpu",
).eval()


colqwen_proc = ColQwen2Processor.from_pretrained("vidore/colqwen2-v1.0")
if qdrant_client.collection_exists(collection_name):
    qdrant_client.delete_collection(collection_name)

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


from tqdm import tqdm
import numpy as np
import hashlib
from qdrant_client.models import PointStruct
import uuid

pbar = tqdm(enumerate(pdf_images), total=len(pdf_images))
points = []
for i, image in pbar:

  image_bytes = np.asarray(image).tobytes()
  image_hash = hashlib.sha256(image_bytes).hexdigest()
  with torch.no_grad():
    processed_images = colqwen_proc.process_images([image]).to(colqwen_model.device)
    image_embeddings = colqwen_model(**processed_images)
    multivector_embeddings = image_embeddings.cpu().float().numpy().tolist()
    
    vector = multivector_embeddings[0]
    point_struct = PointStruct(
      id=str(uuid.uuid4()),
      vector=vector,
      payload={"image_hash": image_hash},

    )

    points.append(point_struct)

    # Save the image if needed
    processed_images[i].save(f"images/{id[i]}.jpg")


upsesrt_to_qdrant(points)