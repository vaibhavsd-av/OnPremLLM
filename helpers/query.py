import time
import torch
from colpali_engine.models import ColQwen2, ColQwen2Processor

# colqwen_model = ColQwen2.from_pretrained(
#     "vidore/colqwen2-v1.0",
#     torch_dtype=torch.bfloat16,
#     device_map="cpu",
# ).eval()


device = "cuda" if torch.cuda.is_available() else "cpu"

colqwen_model = ColQwen2.from_pretrained(
    "vidore/colqwen2-v1.0",
    torch_dtype=torch.float16 if device == "cuda" else torch.float32,
    device_map=device,
).eval()

colqwen_proc = ColQwen2Processor.from_pretrained("vidore/colqwen2-v1.0")

def process_query_to_vector(query_text):
    overall_start = time.time()

    # Step 1: Preprocessing
    batch_query = colqwen_proc.process_queries([query_text]).to(device)

    # Step 2: Inference
    with torch.no_grad():
        query_embedding = colqwen_model(**batch_query)

    # Step 3: Postprocessing
    multivector_query = query_embedding[0].to(torch.float32).cpu().numpy().tolist()

    overall_end = time.time()
    print(f"Total query processing time: {overall_end - overall_start:.4f} seconds")

    return multivector_query
