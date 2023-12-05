#!/bin/python

import os
from openai import OpenAI

client = OpenAI(api_key=get_api_key(api_key_file_path))
import argparse

def get_api_key(file_path):
    """Read the API key from the specified file."""
    with open(file_path, 'r') as file:
        return file.readline().strip()

def scan_and_read_python_files(directory):
    """Scan and read all Python files in the specified directory."""
    all_files_content = ""
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    all_files_content += f"\n\n# File: {file_path}\n"
                    all_files_content += f.read()
    return all_files_content

def split_into_chunks(text, chunk_size):
    """Split the text into specified size chunks."""
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

def analyze_code_with_chatgpt_in_session(code_chunks):
    """Analyze code with ChatGPT in a single session and return the session ID."""
    messages = [{"role": "system", "content": "Analyze the following Python code."}]
    for chunk in code_chunks:
        messages.append({"role": "user", "content": chunk})
        messages.append({"role": "assistant", "content": ""})  # Placeholder for response

    response = client.chat.completions.create(model="gpt-4.0-chat",
    messages=messages)

    session_id = response['choices'][0]['session_id']
    analysis_result = response.choices[0].message['content']
    return analysis_result, session_id

def resume_session_with_new_message(session_id, new_message):
    """Resume the session with a new message."""
    response = client.chat.completions.create(model="gpt-4.0-chat",
    session_id=session_id,
    messages=[{"role": "user", "content": new_message}, {"role": "assistant", "content": ""}])

    return response.choices[0].message['content']

def interactive_chat(session_id):
    """Interactive chat with the ChatGPT session."""
    print("\nYou can now start interacting with ChatGPT about the code. Type 'exit' to end the session.\n")
    while True:
        user_input = input("Ask ChatGPT: ")
        if user_input.lower() == 'exit':
            break
        response = resume_session_with_new_message(session_id, user_input)
        print("ChatGPT:", response)

def main():
    """Main function to run the script."""

    # Setup argument parser
    parser = argparse.ArgumentParser(description='Analyze a Python project with ChatGPT.')
    parser.add_argument('project_directory', type=str, help='Path to the Python project directory.')
    args = parser.parse_args()

    # Construct the path to the .openai file in the user's home directory
    api_key_file_path = os.path.expanduser('~/.openai')

    project_code = scan_and_read_python_files(args.project_directory)
    code_chunks = split_into_chunks(project_code, 2000)

    analysis_result, session_id = analyze_code_with_chatgpt_in_session(code_chunks)
    print("Analysis Result:\n", analysis_result)

    interactive_chat(session_id)

if __name__ == "__main__":
    main()
