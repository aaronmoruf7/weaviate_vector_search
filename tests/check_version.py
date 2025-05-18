import weaviate
import os
from dotenv import load_dotenv

load_dotenv()
client = weaviate.connect_to_weaviate_cloud(
    cluster_url=os.getenv("WEAVIATE_URL"),
    auth_credentials=weaviate.classes.init.Auth.api_key(os.getenv("WEAVIATE_API_KEY")),
    headers={"X-OpenAI-Api-Key": os.getenv("OPENAI_API_KEY")}
)
print(f"Client version: {weaviate.__version__}")
print(f"Server version: {client.get_meta()['version']}")
client.close()