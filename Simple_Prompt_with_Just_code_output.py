"""Run this model in Python

> pip install azure-ai-inference
"""
import os
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import AssistantMessage, SystemMessage, UserMessage
from azure.ai.inference.models import ImageContentItem, ImageUrl, TextContentItem
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv

load_dotenv()

# To authenticate with the model you will need to generate a personal access token (PAT) in your GitHub settings.
# Create your PAT token by following instructions here: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens
client = ChatCompletionsClient(
    endpoint = "https://models.inference.ai.azure.com",
    credential = AzureKeyCredential(os.environ["GITHUB_TOKEN"]),
)

response = client.complete(
    messages = [
        SystemMessage(content = "# Provide Code Without Explanation\n\nYour task is to generate code based on the user's request without including any explanations, comments, or additional descriptions. The output should be concise and strictly limited to the code itself.\n\n## Additional Details\n\n- Ensure that the code is syntactically correct and functional.\n- Do not include any comments or annotations within the code.\n- Avoid adding any introductory or concluding statements.\n\n## Output Format\n\n- The output should be a single block of code.\n- Ensure the code is properly formatted for readability.\n\n# Examples\n\n### Example 1\n\n**Input:**  \nWrite a Python function to calculate the factorial of a number.\n\n**Output:**  \n```python\ndef factorial(n):\n    if n == 0:\n        return 1\n    else:\n        return n * factorial(n-1)\n```\n\n### Example 2\n\n**Input:**  \nCreate a JavaScript function to check if a string is a palindrome.\n\n**Output:**  \n```javascript\nfunction isPalindrome(str) {\n    return str === str.split('').reverse().join('');\n}\n```\n\n### Example 3\n\n**Input:**  \nGenerate a SQL query to select all records from a table named `users`.\n\n**Output:**  \n```sql\nSELECT * FROM users;\n```\n\n# Notes\n\n- Ensure that the code is relevant to the user's request.\n- If the request is ambiguous, seek clarification before providing the code.\n- Avoid using any language-specific libraries or frameworks unless specified by the user."),
        UserMessage(content = [
            TextContentItem(text = "Create a python script to get a secret from an azure key vault."),
        ]),
    ],
    model = "Phi-4",
    max_tokens = 2048,
    temperature = 0.8,
    top_p = 0.1,
)

print(response.choices[0].message.content)