"""Run this model in Python

> pip install azure-ai-inference
"""
import os
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import AssistantMessage, SystemMessage, UserMessage
from azure.ai.inference.models import ImageContentItem, ImageUrl, TextContentItem
from azure.core.credentials import AzureKeyCredential

# To authenticate with the model you will need to generate a personal access token (PAT) in your GitHub settings.
# Create your PAT token by following instructions here: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens
# client = ChatCompletionsClient(
#     endpoint = "https://models.inference.ai.azure.com",
#     credential = AzureKeyCredential(os.environ["GITHUB_TOKEN"]),
#     api_version = "2024-08-01-preview",
# )

client = ChatCompletionsClient(
    endpoint = "https://infrencedev6563022612.openai.azure.com",
    credential = AzureKeyCredential("4mDx3XxhhXueSExJYwt0jVPB4LhsgFdgRNeDlfaM6LxPBokPMJDKJQQJ99BBACLArgHXJ3w3AAAAACOGdiGX"),
    api_version = "2024-08-01-preview",
)

response = client.complete(
    messages = [
        SystemMessage(content = "You are a software engineer."),
        UserMessage(content = [
            TextContentItem(text = "Write a test using xunit that asserts false"),
        ]),
        AssistantMessage(content = "First, ensure you have the xUnit library installed in your project. You can install it via NuGet with the following command:\n\n```\nInstall-Package xunit\n```\n\nHere is a basic example of a test class with a test method that asserts true:\n\n```csharp\nusing Xunit;\n\npublic class SampleTests\n{\n    [Fact]\n    public void AssertTrueTest()\n    {\n        // Arrange\n        bool condition = true;\n\n        // Act & Assert\n        Assert.True(condition, \"The condition should be true.\");\n    }\n}\n```\n\n### How to Run the Test\nYou can run this test using the test explorer in Visual Studio or from the command line using the .NET CLI:\n\n```\ndotnet test\n```\n\nThis command will run all tests in the project, including the one we just created. If everything is set up correctly, the test should pass successfully since the condition is indeed true."),
    ],
    model = "gpt-4o",
    response_format = "text",
    max_tokens = 4096,
    temperature = 1,
    top_p = 1,
)

print(response.choices[0].message.content)