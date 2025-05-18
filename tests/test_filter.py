import weaviate
import os
from dotenv import load_dotenv
from weaviate.classes.query import Filter

load_dotenv()
client = weaviate.connect_to_weaviate_cloud(
    cluster_url=os.getenv("WEAVIATE_URL"),
    auth_credentials=weaviate.classes.init.Auth.api_key(os.getenv("WEAVIATE_API_KEY")),
    headers={"X-OpenAI-Api-Key": os.getenv("OPENAI_API_KEY")}
)
collection = client.collections.get("sales_rag_docs")
filters = Filter.by_property("return_status").equal("Returned")
results = collection.query.fetch_objects(
    limit=5,
    filters=filters,
    return_properties=["description", "unit_price", "return_status"]
)
print("Filter-only results:")
for obj in results.objects:
    print(obj.properties)
client.close()