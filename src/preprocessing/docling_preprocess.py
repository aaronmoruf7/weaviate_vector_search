import os
from pathlib import Path
import json 

import weaviate
from weaviate.classes.init import Auth
from weaviate.classes.config import Configure

from docling.document_converter import DocumentConverter
from docling.chunking import HybridChunker

from dotenv import load_dotenv

# === Load environment variables ===
load_dotenv()
WEAVIATE_URL = os.getenv("WEAVIATE_URL")
WEAVIATE_API_KEY = os.getenv("WEAVIATE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# === Source file ===
SOURCE_FILE = Path("sources/online_sales_dataset.xlsx")

def generate_chunks(file_path: Path):
    converter = DocumentConverter()
    chunker = HybridChunker(tokenizer="sentence-transformers/all-MiniLM-L6-v2")

    converted = converter.convert(file_path).document
    chunks = list(chunker.chunk(converted))
    print(f"Generated {len(chunks)} chunks")

    return chunks

def transform_chunks(chunks):
    documents = []

    for i, chunk in enumerate(chunks):
        text = chunk.text.strip()
        if not text:
            continue

        try:
            # Split chunk text into individual field-value lines
            entries = text.split(". ")
            grouped = {}

            for entry in entries:
                # Ensure correct format: "id, field = value"
                if ", " not in entry or "=" not in entry:
                    continue

                id_part, value_part = entry.split(", ", 1)

                if " = " not in value_part:
                    continue

                field, value = value_part.split(" = ", 1)

                # Group all fields by their invoice ID
                row = grouped.setdefault(id_part.strip(), {})
                row[field.strip()] = value.strip()

            # Build one document per invoice row
            for invoice_id, data in grouped.items():
                documents.append({
                    "description": data.get("Description", ""),
                    "metadata": {
                        "invoice_no": invoice_id,
                        "stock_code": data.get("StockCode"),
                        "quantity": data.get("Quantity"),
                        "unit_price": data.get("UnitPrice"),
                        "invoice_date": data.get("InvoiceDate"),
                        "country": data.get("Country"),
                        "payment_method": data.get("PaymentMethod"),
                        "shipping_cost": data.get("ShippingCost"),
                        "return_status": data.get("ReturnStatus"),
                        "warehouse_location": data.get("WarehouseLocation"),
                        "order_priority": data.get("OrderPriority"),
                    }
                })

        except Exception as e:
            print(f"⚠️ Failed to parse chunk {i}: {e}")
            continue

    print(f"✅ Transformed {len(documents)} documents")
    return documents

def transform_chunks_test(chunks):
    documents = []

    for i, chunk in enumerate(chunks):
        print(f"\n🔍 Raw chunk [{i}] →\n{chunk.text}\n{'-'*60}")

        # For now, just print the first 5
        if i >= 4:
            break

    return documents

def store_in_weaviate(docs):
    client = weaviate.connect_to_weaviate_cloud(
        cluster_url=WEAVIATE_URL,
        auth_credentials=Auth.api_key(WEAVIATE_API_KEY),
        headers={"X-OpenAI-Api-Key": OPENAI_API_KEY}
    )

    print("Client connected:", client.is_ready())

    if client.is_ready():
        collection = client.collections.create(
            name="sales_rag_docs",
            vectorizer_config=Configure.Vectorizer.text2vec_openai(),
            generative_config=Configure.Generative.openai(model="gpt-4o-mini")
        )

        print(f"Uploading {min(20, len(docs))} chunks...")

        with collection.batch.dynamic() as batch:
            for i, d in enumerate(docs[:20]):  # limit to first 20
                print(f"→ [{i+1}/{min(20, len(docs))}] {d['description'][:60]}...")
                batch.add_object(
                    properties={
                        "description": d["description"],
                        **d["metadata"]
                    }
                )

        print("✅ Uploaded chunks to Weaviate")
        client.close()
    else:
        print("❌ Could not connect to Weaviate")


if __name__ == "__main__":
    chunks = generate_chunks(SOURCE_FILE)
    transform_chunks_test(chunks)
    # store_in_weaviate(docs)
