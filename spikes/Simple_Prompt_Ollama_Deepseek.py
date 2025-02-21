"""Run this model in Python

> pip install openai
"""
from openai import OpenAI

client = OpenAI(
    base_url = "http://localhost:11434/v1",
    api_key = "unused", # required for the API but not used
)

response = client.chat.completions.create(
    messages = [
        {
            "role": "system",
            "content": "You're a software engineer",
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Create a python script to print hello world",
                },
            ],
        },
    ],
    model = "deepseek-r1:8b",
    max_tokens = 4096,
    temperature = 1,
    top_p = 1,
)

print(response.choices[0].message.content)