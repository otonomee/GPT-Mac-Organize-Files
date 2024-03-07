import os
import subprocess
import requests
from functools import reduce
import time

class DirectoryProcessor:
    def __init__(self):
        self.rootdir = os.getcwd()
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.model_name = 'gpt-3.5-turbo'
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Accept": "application/json, text/plain, */*",
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            }
        )
        self.post_data_template = {
            "model": 'gpt-3.5-turbo',
            "messages": [
                {
                    "role": "system",
                    "content": """ 
                       
                    """,
                },
                {"role": "user", "content": ""},
            ],
            "temperature": 0.01,
            "max_tokens": 4000
        }

    def get_directory_structure(self):
        """
        Creates a nested dictionary that represents the folder structure of rootdir
        """
        dir = {}
        start = self.rootdir.rfind(os.sep) + 1
        for path, dirs, files in os.walk(self.rootdir):
            folders = path[start:].split(os.sep)
            subdir = dict.fromkeys(files)
            parent = reduce(dict.get, folders[:-1], dir)
            parent[folders[-1]] = subdir
        return dir

   

    def execute_commands(self, commands):
        """
        Executes shell commands
        """
        for command in commands:
            subprocess.run(command, shell=True)

    def process_directory(self):
        # Get the directory structure
        dir_structure = self.get_directory_structure()

        # Send the directory structure to the GPT API
        gpt_response = self.send_to_gpt_api(dir_structure)

        # Get the commands from the GPT API response
        commands = gpt_response.get('choices', [{}])[0].get('text', '').split('\n')

        # Execute the commands
        self.execute_commands(commands)

    

    def print_directory_structure(self):
        startpath = os.getcwd()
        structure = ''
        for root, dirs, files in os.walk(startpath):
            level = root.replace(startpath, '').count(os.sep)
            indent = ' ' * 4 * (level)
            print('{}{}/'.format(indent, os.path.basename(root)))
            subindent = ' ' * 4 * (level + 1)
            for f in files:
                structure += '{}{}'.format(subindent, f)
        return structure

    

    def get_commands(self, retries=5, delay=5):
        directory_info = self.print_directory_structure()
        post_data = self.post_data_template.copy()
        # entity = meta_info.get('og:site_name', '')  # Use the 'og:site_name' meta tag as the entity
        post_data["messages"][1]["content"] = f"""
        I need to organize my files and folders in my cwd, I'm going to give you the files/folder structure of my cwd, and you are to 
        analyze this, determine the optimal organization of the files and folders, and then provide me with the commands to execute to
        organize the files and folders. 

        ** Your output must simply be a one-line bash command or hyphenated list of bash commands sequence that organizes the files and folders as you've recommended **

        Directory files and folders: {directory_info}

        Example Output:
        "mv file.txt /path/to/new/directory"
        """
        
        for _ in range(retries):
            try:
                response = self.session.post("https://api.openai.com/v1/chat/completions", json=post_data, timeout=60)
                response.raise_for_status()
                response = response.json()
                print(response['choices'][0]['message']['content'])
                commands = response['choices'][0]['message']['content'].split(';')
                return commands
                # command = response["choices"][0]["message"]["content"].split('Bash command: ')[1]
                # return command
            except requests.HTTPError as e:
                print(f"Request failed with {e}, retrying after {delay} seconds...")
                time.sleep(delay)
            except requests.Timeout:
                print("Request to OpenAI API timed out after 60 seconds, retrying...")
                time.sleep(delay)
            except requests.exceptions.RequestException as e:
                print(f"Request failed with {e}, retrying after {delay} seconds...")
                time.sleep(delay)

    def execute_bash_command(self, command):
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        output, error = process.communicate()

        if process.returncode != 0:
            print(f"Error executing '{command}': {error.decode('utf-8')}")
        else:
            print(f"Output of '{command}': {output.decode('utf-8')}")

if __name__ == "__main__":
    processor = DirectoryProcessor()
    commands = processor.get_commands()
    for command in commands:
        command = command.strip()
        if command:            
            processor.execute_bash_command(command)
            

