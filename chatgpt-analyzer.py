#!/bin/python

import os
import openai
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
    """Analyze code with ChatGPT and maintain conversation history."""
    messages = [{"role": "system", "content": "Analyze the following Python code."}]
    for chunk in code_chunks:
        messages.append({"role": "user", "content": chunk})
        # Send each chunk and get response
        response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
        messages.append({"role": "assistant", "content": response.choices[0].message['content']})

    return messages[-1]['content'], messages  # Return last response and all messages

def resume_session_with_new_message(messages, new_message):
    """Resume the conversation with a new message and existing history."""
    messages.append({"role": "user", "content": new_message})
    response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
    messages.append({"role": "assistant", "content": response.choices[0].message['content']})
    return response.choices[0].message['content']

def interactive_chat(messages):
    """Interactive chat with the ChatGPT using conversation history."""
    print("\nYou can now start interacting with ChatGPT about the code. Type 'exit' to end the session.\n")
    while True:
        user_input = input("Ask ChatGPT: ")
        if user_input.lower() == 'exit':
            break
        response = resume_session_with_new_message(messages, user_input)
        print("ChatGPT:", response)

def main():
    """Main function to run the script."""
    parser = argparse.ArgumentParser(description='Analyze a Python project with ChatGPT.')
    parser.add_argument('project_directory', type=str, help='Path to the Python project directory.')
    args = parser.parse_args()

    api_key_file_path = os.path.expanduser('~/.openai')
    openai.api_key = get_api_key(api_key_file_path)

    project_code = scan_and_read_python_files(args.project_directory)
    code_chunks = split_into_chunks(project_code, 1000)

    analysis_result, messages = analyze_code_with_chatgpt_in_session(code_chunks)
    print("Analysis Result:\n", analysis_result)

    interactive_chat(messages)

if __name__ == "__main__":
    main()
