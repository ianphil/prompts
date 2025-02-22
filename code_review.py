#!/usr/bin/env python3
"""
Code Review Tool
---------------

A tool for automated code review using Azure OpenAI GPT-4 model. Ensure you have checked
out the branch in the repo you want to review before running this script.

Usage:
    python code_review.py --git-dir=<path_to_git_dir> --work-tree=<path_to_work_tree>

Example:
    python code_review.py --git-dir="C:/src/project/.git" --work-tree="C:/src/project"

Requirements:
    - Python 3.8+
    - Azure OpenAI API access
    - Environment variables:
        AZUREAI_ENDPOINT: Azure OpenAI endpoint URL
        AZUREAI_KEY: Azure OpenAI API key
        AZUREAI_API_VERSION: Azure OpenAI API version

Dependencies:
    - tiktoken
    - openai
    - python-dotenv
"""

import argparse
import os
import subprocess
import tiktoken
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()


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


def get_code_review_prompt(code: str) -> str:
    endpoint = os.getenv("AZUREAI_ENDPOINT")
    key = os.getenv("AZUREAI_KEY")
    api_version = os.getenv("AZUREAI_API_VERSION")

    client = AzureOpenAI(azure_endpoint=endpoint, api_key=key, api_version=api_version)

    # Read the prompt from XML file
    with open("code_review_prompt.xml", "r", encoding="utf-8") as file:
        prompt = file.read()

    response = client.chat.completions.create(
        messages=[{"role": "user", "content": f"{prompt} {code}"}], model="gpt-4"
    )
    
    # Write review results to file
    with open("review.md", "w", encoding="utf-8") as file:
        file.write(response.choices[0].message.content)

    print(response.choices[0].message.content)


def get_git_diff(git_dir: str, work_tree: str, branch: str = "main") -> str:
    """
    Get git diff output as a string using subprocess.

    Args:
        git_dir (str): Path to .git directory
        work_tree (str): Path to working tree
        branch (str): Branch to diff against, defaults to 'main'

    Returns:
        str: Git diff output
    """
    try:
        # Get git status first and print to console
        status = subprocess.run(
            ["git", f"--git-dir={git_dir}", f"--work-tree={work_tree}", "branch"],
            capture_output=True,
            text=True,
            check=True
        )
        print(status.stdout)
        
        # The current branch will have an asterisk (*)
        current_branch = None
        for line in status.stdout.splitlines():
            if line.startswith('*'):
                current_branch = line.lstrip('* ').strip()
                break

        print(current_branch)
        
        common_ansestor = subprocess.run(
            ["git", f"--git-dir={git_dir}", f"--work-tree={work_tree}", "merge-base", current_branch, branch],
            capture_output=True,
            text=True,
            check=True
        )
        print(status.stdout)
        
        result = subprocess.run(
            ["git", f"--git-dir={git_dir}", f"--work-tree={work_tree}", "diff", common_ansestor.stdout.strip()],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error running git diff: {e}")
        return ""


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Code review tool")
    parser.add_argument(
        "--git-dir", type=str, required=True, help="Path to .git directory"
    )
    parser.add_argument(
        "--work-tree", type=str, required=True, help="Path to working tree"
    )
    args = parser.parse_args()

    git_dir = args.git_dir
    work_tree = args.work_tree

    # Get git diff output
    diff_output = get_git_diff(git_dir, work_tree)
    
    # Write git diff output to file
    with open("git.diff", "w", encoding="utf-8") as file:
        file.write(diff_output)

    # with open("main.diff", "r") as file:
    #     text = file.read()
    token_count = count_tokens(diff_output)
    print(f"Token count: {token_count}")
    get_code_review_prompt(diff_output)
