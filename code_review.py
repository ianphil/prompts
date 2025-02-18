import argparse
import subprocess
import os
import sys
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage, TextContentItem
from azure.core.credentials import AzureKeyCredential

def run_git_command(cmd, repo_path):
    """Run a git command in the specified repository path and return the output, or exit on error."""
    try:
        result = subprocess.run(
            cmd,
            cwd=repo_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {' '.join(cmd)} in {repo_path}")
        print(e.stderr)
        sys.exit(1)

def checkout_branch(repo_path, branch):
    """
    Check out the specified branch. If it doesn't exist locally, attempt to create it
    by tracking the remote branch from 'origin'.
    """
    # Check if branch exists locally.
    proc = subprocess.run(
        ["git", "rev-parse", "--verify", branch],
        cwd=repo_path,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    if proc.returncode == 0:
        # Branch exists locally, so simply check it out.
        run_git_command(["git", "checkout", branch], repo_path)
    else:
        # Branch doesn't exist locally; try checking it out from origin.
        print(f"Branch '{branch}' not found locally. Attempting to check out from origin...")
        run_git_command(["git", "checkout", "-b", branch, f"origin/{branch}"], repo_path)

def main():
    # Parse command-line arguments.
    parser = argparse.ArgumentParser(
        description="Pull a branch, diff against main, and perform a code review using Azure AI Inference."
    )
    parser.add_argument("branch", help="Name of the branch to review")
    parser.add_argument("repo_path", help="Path to the git repository")
    args = parser.parse_args()

    branch = args.branch
    repo_path = args.repo_path

    # Validate the repository path.
    if not os.path.exists(repo_path):
        print(f"Error: The repository path '{repo_path}' does not exist.")
        sys.exit(1)
    if not os.path.isdir(os.path.join(repo_path, ".git")):
        print(f"Error: '{repo_path}' is not a valid git repository.")
        sys.exit(1)

    # Check for the Azure credential (using GITHUB_TOKEN as per the guide).
    if not os.getenv("GITHUB_TOKEN"):
        print("Error: GITHUB_TOKEN environment variable not set.")
        sys.exit(1)

    # Set up the Azure ChatCompletionsClient.
    client = ChatCompletionsClient(
        endpoint="https://models.inference.ai.azure.com",
        credential=AzureKeyCredential(os.environ["GITHUB_TOKEN"]),
    )

    print(f"Switching to branch '{branch}' and pulling latest changes in repo '{repo_path}'...")
    checkout_branch(repo_path, branch)
    pull_output = run_git_command(["git", "pull", "origin", branch], repo_path)
    print(pull_output)

    print("Generating diff against the main branch...")
    diff_output = run_git_command(["git", "diff", "main", branch], repo_path)
    
    if not diff_output:
        print("No differences found between the branches.")
        sys.exit(0)

    # Construct the prompt for code review.
    review_prompt = (
        "Please review the following git diff and provide detailed code review suggestions with potential improvements:\n\n"
        + diff_output
    )

    print("Sending diff to Azure AI for code review...")
    try:
        response = client.complete(
            messages=[
                SystemMessage(content="You are a helpful code reviewer."),
                UserMessage(content=[TextContentItem(text=review_prompt)]),
            ],
            model="o1",
            max_tokens=2048,
            temperature=0.2,
            top_p=0.1,
        )
        review = response.choices[0].message.content
        print("\n--- Code Review ---")
        print(review)
    except Exception as e:
        print("An error occurred while communicating with Azure AI:")
        print(e)
        sys.exit(1)

if __name__ == "__main__":
    main()
