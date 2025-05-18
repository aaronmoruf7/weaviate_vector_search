import os
import weaviate
from weaviate.classes.init import Auth
from dotenv import load_dotenv

load_dotenv()

WEAVIATE_URL = os.getenv("WEAVIATE_URL")
WEAVIATE_API_KEY = os.getenv("WEAVIATE_API_KEY")

def test_weaviate_connection():
    try:
        client = weaviate.connect_to_weaviate_cloud(
            cluster_url=WEAVIATE_URL,
            auth_credentials=Auth.api_key(WEAVIATE_API_KEY)
        )
        is_ready = client.is_ready()
        print("✅ Weaviate connection successful:", is_ready)
        assert is_ready is True
        client.close()

    except Exception as e:
        print("❌ Weaviate connection failed:", str(e))
        assert False

if __name__ == "__main__":
    test_weaviate_connection()
