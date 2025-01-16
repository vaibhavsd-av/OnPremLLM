from qdrant_client import QdrantClient, models

qdrant_client = QdrantClient(url="http://localhost:6333")

collection_name = "onprem_llm_collection"


def search_img_id(multivector_query):
    search_result = qdrant_client.query_points(
    collection_name=collection_name,
    query=multivector_query,
    limit=3,
    timeout=100,
    search_params=models.SearchParams(
        quantization=models.QuantizationSearchParams(
            ignore=False,
            rescore=True,
            oversampling=2.0,
            )
        )
    )

    img_id = search_result.points[0].id
    print(img_id)
    return img_id