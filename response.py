import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)

def calculate_square(nbr: int):
    return nbr * nbr

available_functions = {
    "calculate_square": calculate_square
}

tools = [{
"type" : "function",
"function": {
"name": "calculate_square",
"description": "Use this function to calculate_square",
            "parameters": {
                "type": "object",
                "properties": {
                    "nbr": {
                        "type": "integer",
                        "description": "Calculates the square of a given integer number (multiplies the number by itself).",
                    }
                },
                "required": ["nbr"],
            },
}
}]

# Function to process messages and handle function calls
def get_completion_from_messages(messages, model="gpt-4o"):
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        tools=tools,  # Custom tools
        tool_choice="auto",
    )

    response_message = response.choices[0].message
    print("First response:", response_message)

    if response_message.tool_calls:
        # Find the tool call content
        tool_call = response_message.tool_calls[0]

        # Extract tool name and arguments
        function_name = tool_call.function.name
        function_args = json.loads(tool_call.function.arguments)
        tool_id = tool_call.id

        messages.append(
            {
                "role": "assistant",
                "tool_calls": [
                    {
                        "id": tool_id,
                        "type": "function",
                        "function": {
                            "name": function_name,
                            "arguments": json.dumps(function_args),
                        },
                    }
                ],
            }
        )

        # Call the function
        function_to_call = available_functions[function_name]
        function_response = function_to_call(**function_args)

        print(function_response)

        messages.append(
            {
                "role": "tool",
                "tool_call_id": tool_id,
                "name": function_name,
                "content": json.dumps(function_response),
            }
        )

        # Second call to get final response based on function output
        second_response = client.chat.completions.create(
            model=model, messages=messages, tools=tools, tool_choice="auto"
        )
        final_answer = second_response.choices[0].message

        print("Second response:", final_answer)
        return final_answer

    return "No relevant function call found."


messages = [
    {"role": "system", "content": "You are a helpful AI assistant."},
    {"role": "user", "content": "How much is square of 5? Calculate square"},
]

response = get_completion_from_messages(messages)
print("--- Full response: ---")
print(response)
print("--- Response text: ---")
print(response.content)