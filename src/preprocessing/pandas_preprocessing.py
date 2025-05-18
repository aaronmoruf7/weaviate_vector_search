import os
from pathlib import Path
import pandas as pd
import weaviate
from weaviate.classes.init import Auth
from weaviate.classes.config import Configure, Property, DataType, Tokenization
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
WEAVIATE_URL = os.getenv("WEAVIATE_URL")
WEAVIATE_API_KEY = os.getenv("WEAVIATE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Source file
SOURCE_FILE = Path("sources/online_sales_dataset.xlsx")

def generate_documents(file_path: Path):
    # Read Excel file
    df = pd.read_excel(file_path)
    documents = []

    # Transform each row into a document with only specified fields
    for _, row in df.iterrows():
        document = {
            "description": str(row.get("Description", "")),
            "metadata": {
                "invoice_no": str(row.get("InvoiceNo", "")),
                "quantity": str(row.get("Quantity", "")),
                "unit_price": str(row.get("UnitPrice", "")),
                "country": str(row.get("Country", "")),
                "return_status": str(row.get("ReturnStatus", ""))
            }
        }
        documents.append(document)

    print(f"✅ Generated {len(documents)} documents")
    return documents

def test_documents(documents):
    # Inspect first 5 documents
    for i, doc in enumerate(documents[:5]):
        print(f"\n🔍 Document [{i}] →")
        print(f"Description: {doc['description']}")
        print(f"Metadata: {doc['metadata']}")
        # Check for missing critical fields
        if not doc["metadata"].get("return_status"):
            print(f"⚠️ Missing return_status in document {i}")
        if not doc["description"]:
            print(f"⚠️ Missing description in document {i}")

    print(f"Total documents inspected: {min(5, len(documents))}")

def store_in_weaviate(docs):
    client = weaviate.connect_to_weaviate_cloud(
        cluster_url=WEAVIATE_URL,
        auth_credentials=Auth.api_key(WEAVIATE_API_KEY),
        headers={"X-OpenAI-Api-Key": OPENAI_API_KEY}
    )

    print("Client connected:", client.is_ready())

    if client.is_ready():
        # Delete existing collection to avoid duplicates
        client.collections.delete("sales_rag_docs")
        # Create collection with only specified properties
        collection = client.collections.create(
            name="sales_rag_docs",
            vectorizer_config=Configure.Vectorizer.text2vec_openai(),
            generative_config=Configure.Generative.openai(model="gpt-4o-mini"),
            properties=[
                Property(name="description", data_type=DataType.TEXT),
                Property(name="invoice_no", data_type=DataType.TEXT),
                Property(name="quantity", data_type=DataType.TEXT),
                Property(name="unit_price", data_type=DataType.TEXT),
                Property(name="country", data_type=DataType.TEXT),
                # Tokenization of field key for filtering accuracy
                Property(name="return_status", data_type=DataType.TEXT, index_filterable=True, skip_vectorization=True, tokenization=Tokenization.FIELD)
                

            ]
        )

        print(f"Uploading {len(docs)} documents...")
        with collection.batch.dynamic() as batch:
            for i, d in enumerate(docs):
                batch.add_object(
                    properties={
                        "description": d["description"],
                        **d["metadata"]
                    }
                )

        print("✅ Uploaded documents to Weaviate")
        client.close()
    else:
        print("❌ Could not connect to Weaviate")

if __name__ == "__main__":
    documents = generate_documents(SOURCE_FILE)
    test_documents(documents)
    store_in_weaviate(documents)