import requests


def analyze_customer_issue(issue):
    prompt = f"""
You are a customer support assistant.

Analyze this customer issue:
{issue}

Give me:
1. A polite reply to the customer.
2. Three troubleshooting steps.
3. Urgency: Low, Medium, or High.

Do not invent facts about the problem.
"""

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3.2:1b",
            "prompt": prompt,
            "stream": False
        },
        timeout=180
    )

    response.raise_for_status()
    return response.json()["response"]

if __name__ == "__main__":
    print("AI CUSTOMER SUPPORT ASSISTANT")
    print("-----------------------------")

    customer_issue = input("Enter the customer's problem: ")

    try:
        result = analyze_customer_issue(customer_issue)
        print("\nAI RESPONSE:\n")
        print(result)
    except Exception as error:
        print("\nSomething went wrong:")
        print(error)