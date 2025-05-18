import os
import json
from dotenv import load_dotenv
from crewai import Agent, Crew, Task
from tools.vector_tool import weaviate_vector_search

# Load environment variables
load_dotenv()

# === Define the Sales Query Analyzer Agent ===
query_analyzer_agent = Agent(
    role="Sales Query Analyzer",
    goal="Analyze user queries to extract a short search phrase and an optional filter for database search.",
    backstory=(
        "You are an expert in analyzing user search requests for an online sales database. "
        "Your job is to extract the key topic and, if appropriate, identify a filter field and value. "
        "Available filter fields: country, return_status, invoice_no, quantity, unit_price. "
        "Always respond in strict JSON format."
    ),
    allow_delegation=False,
    verbose=True,
    # model="gpt-4o"
)

# === Define the Search Executor Agent ===
search_executor_agent = Agent(
    role="Sales Database Searcher",
    goal="Take extracted query and filters, then search the sales database to retrieve relevant documents.",
    backstory=(
        "You are responsible for running the search queries against the sales database using the provided tool."
    ),
    allow_delegation=False,
    verbose=True,
    tools=[weaviate_vector_search],
    model="gpt-4o"
)

# === Create the Query Analyzer Task dynamically ===
def create_analyze_query_task(user_input: str):
    return Task(
        description=(
            f"You are given the user query: '{user_input}'\n\n"
            "Your job is to:\n"
            "- Extract a short and clear search phrase (1-4 words maximum).\n"
            "- Detect if a filter is mentioned.\n"
            "- Match the filter to one of these fields if possible: country, return_status, invoice_no, quantity, unit_price.\n\n"
            "You MUST respond in exactly this JSON format:\n"
            "{\n"
            "  \"query\": \"short search term\",\n"
            "  \"filter_field\": \"field name or null\",\n"
            "  \"filter_value\": \"value or null\"\n"
            "}\n\n"
            "=== EXTRA RULES ===\n"
            "- If the user mentions a country name (examples: Germany, France, Spain, United Kingdom, etc.), set filter_field to \"country\".\n"
            "- If the user mentions returned or cancelled products, set filter_field to \"return_status\".\n"
            "- Never set \"query\" to null. Always guess the best search keyword if unsure.\n"
            "- Always strictly follow JSON format.\n\n"
            "=== Examples ===\n\n"
            "Example 1:\n"
            "User input: \"Find all products in Germany\"\n"
            "Output:\n"
            "{\n"
            "  \"query\": \"products\",\n"
            "  \"filter_field\": \"country\",\n"
            "  \"filter_value\": \"Germany\"\n"
            "}\n\n"
            "Example 2:\n"
            "User input: \"What items were returned?\"\n"
            "Output:\n"
            "{\n"
            "  \"query\": \"items\",\n"
            "  \"filter_field\": \"return_status\",\n"
            "  \"filter_value\": \"Returned\"\n"
            "}"
        ),
        expected_output="A JSON object with 'query', 'filter_field', and 'filter_value'.",
        agent=query_analyzer_agent,
    )


# === Create the Search Executor Task dynamically ===
def create_search_executor_task():
    return Task(
        description=(
            "You are given extracted search parameters from the previous task (query, filter_field, filter_value).\n\n"
            "Use the 'weaviate_vector_search' tool to run the search. "
            "Pass the query as the search text, and if a filter_field and filter_value are provided (not null), pass them too.\n\n"
            "Return the matching search results as a JSON list."
        ),
        expected_output="The JSON list of search results from the database.",
        agent=search_executor_agent,
    )

# === Run the Crew ===
def run_sales_query_crew(user_input: str):
    # Step 1: Create tasks
    query_task = create_analyze_query_task(user_input)
    search_task = create_search_executor_task()

    # Step 2: Create Crew with two agents and two tasks
    crew = Crew(
        agents=[query_analyzer_agent, search_executor_agent],
        tasks=[query_task, search_task],
        verbose=True
    )

    # Step 3: Kickoff
    result = crew.kickoff(inputs={"user_input": user_input})
    return result
