import os
import json
from typing import Optional
from dotenv import load_dotenv
from crewai.tools import tool
import weaviate
from weaviate.classes.query import Filter
from weaviate.classes.init import Auth

# Load env vars
load_dotenv()
WEAVIATE_URL = os.getenv("WEAVIATE_URL")
WEAVIATE_API_KEY = os.getenv("WEAVIATE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# === Vector Search Tool ===
@tool("Search sales records using vector similarity")
def weaviate_vector_search(query: str, filter_by: Optional[str] = None, filter_value: Optional[str] = None) -> str:
    """
    Searches a Weaviate vector DB for similar documents based on query and optional filters.
    """
    try:
        # Optional filters
        filters = None
        if filter_by and filter_value:
            filters = Filter.by_property(filter_by).equal(filter_value)
            print(f"Applying filter: {filter_by} = {filter_value}")

        # Connect to Weaviate cloud
        client = weaviate.connect_to_weaviate_cloud(
            cluster_url=WEAVIATE_URL,
            auth_credentials=Auth.api_key(WEAVIATE_API_KEY),
            headers={"X-OpenAI-Api-Key": OPENAI_API_KEY},
        )

        collection = client.collections.get("sales_rag_docs")

        # Debug: Print schema for return_status
        schema = collection.config.get()
        return_status_schema = next((prop for prop in schema.properties if prop.name == "return_status"), None)
        # print(f"Schema for return_status: {return_status_schema}")

        # Perform the vector search
        results = collection.query.near_text(
            query=query,
            limit=5,
            filters=filters,
            # return_properties=["description", "unit_price", "return_status"]
        )

        # Debug: Log raw results
        raw_results = [obj.properties for obj in results.objects]
        # print(f"Raw results: {raw_results}")

        client.close()

        return json.dumps(raw_results, indent=2)

    except Exception as e:
        return f"❌ Error during vector search: {str(e)}"