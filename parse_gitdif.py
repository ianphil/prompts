import tiktoken
from azure.identity import DefaultAzureCredential
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
from azure.ai.openai import AzureOpenAIClient

def send_to_azure_openai(prompt: str, endpoint: str, deployment_name: str = "gpt-4") -> str:
    """
    Send a prompt to Azure OpenAI using default credentials.
    
    Args:
        prompt (str): The prompt to send
        endpoint (str): Azure OpenAI endpoint URL
        deployment_name (str): Name of the deployment to use
        
    Returns:
        str: The response from Azure OpenAI
    """
    try:
        # Initialize the Azure OpenAI client with default credentials
        credential = DefaultAzureCredential()
        client = AzureOpenAIClient(
            endpoint=endpoint,
            credential=credential,
        )

        # Send the completion request
        response = client.get_completions(
            deployment_name=deployment_name,
            prompt=prompt,
            max_tokens=1000,
            temperature=0.7,
            top_p=0.95,
            stop=None
        )

        return response.choices[0].text.strip()
    except Exception as e:
        print(f"Error calling Azure OpenAI: {str(e)}")
        return ""

def count_tokens(text: str) -> int:
    """
    Count the number of tokens in a string using GPT-4's tokenizer.
    
    Args:
        text (str): The input text to tokenize
        
    Returns:
        int: Number of tokens in the text
    """
    # Use the GPT-4 encoder
    encoder = tiktoken.encoding_for_model("gpt-4")
    
    # Encode the text and return the token count
    tokens = encoder.encode(text)
    return len(tokens)

def parse_git_diff(diff_text: str) -> dict:
    """
    Parse a git diff output into a dictionary of files and their changes.
    
    Args:
        diff_text (str): Git diff output text
        
    Returns:
        dict: Dictionary with filenames as keys and their changes as values
    """
    files = {}
    current_file = None
    current_content = []
    
    for line in diff_text.split('\n'):
        if line.startswith('diff --git'):
            # Save previous file content if exists
            if current_file:
                files[current_file] = '\n'.join(current_content)
                current_content = []
            
            # Extract new filename
            current_file = line.split(' b/')[-1]
            
        elif current_file:
            current_content.append(line)
            
    # Add the last file
    if current_file and current_content:
        files[current_file] = '\n'.join(current_content)
        
    return files

# Example usage:
if __name__ == "__main__":
    endpoint = "https://your-resource.openai.azure.com/"
    prompt = "Analyze this code change:"
    deployment_name = "gpt-4"

    with open('main.diff', 'r') as file:
        diff_content = file.read()
    
    parsed_files = parse_git_diff(diff_content)
    
    # Print results
    for filename, content in parsed_files.items():
        print(f"\nFile: {filename}")
        print(f"Changes length: {len(content)} characters")

        full_prompt = f"{prompt}\n\n{content}"

        token_count = count_tokens(content)
        print(f"Token count: {token_count}")