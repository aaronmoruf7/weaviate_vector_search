This project uses CrewAI + OpenAI + Weaviate to dynamically search a sales database.

**Instructions**

```bash
git clone https://github.com/Anchor-Co-Pilot/agentic-rag-poc.git
```
```bash
pip install -r requirements.txt
```
**Create a `.env` file**

```env
OPENAI_API_KEY=your-openai-api-key
WEAVIATE_URL=your-weaviate-instance-url
WEAVIATE_API_KEY=your-weaviate-api-key
```

## Vector Database Schema (Weaviate)

Collection name: `sales_rag_docs`

| Field           | Type  |
|-----------------|-------|
| description     | text  
| invoice_no      | text  |
| quantity        | text  |
| unit_price      | text  |
| country         | text  |
| return_status   | text  |


## 🚀 How to Run

1. Run `python src/preprocessing/pandas_preprocessing.py` to upload data to the vector database and create embeddings

2. Edit `tests/test_crew.py`

Change the line:

```python
user_input = "Find all stationery in Germany"
```

to any query you want. Note that for this poc, it only allows one filter at a time

3. Run the crew:

```bash
PYTHONPATH=src python tests/test_crew.py
```
-----

## ✅ Example Output

```json
[
  {
    "description": "Headphones",
    "invoice_no": "231932",
    "return_status": "Returned",
    "unit_price": "29.11",
    "quantity": "49",
    "country": "Germany"
  },
  ...
]
```

---
