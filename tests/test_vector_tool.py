from tools.vector_tool import weaviate_vector_search

# In the terminal: PYTHONPATH=src python tests/test_vector_tool.py
#can change query to "stationery" etc.
def test_sample_vector_query():
    query = "electronics"
    filter_by = "return_status"
    filter_value = "Returned"

    result = weaviate_vector_search.run(
        query=query,
        filter_by=filter_by,
        filter_value=filter_value
    )
    print("Query: ", query)
    print("\n🔍 Vector Search Output:")
    print(result)

if __name__ == "__main__":
    test_sample_vector_query()
