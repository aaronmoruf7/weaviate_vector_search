# test_crew.py

from crew import run_sales_query_crew

if __name__ == "__main__":
    # Example user input (you can change this)
    # user_input = "Find all electronics that were returned"
    user_input = "Find all stationery from Germany"


    print(f"\n📝 User Input: {user_input}\n")

    result = run_sales_query_crew(user_input)

    print("\n🎯 Crew Output:")
    print(result)
