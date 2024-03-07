## GPT-3 File System Organizer
This Python script uses OpenAI's GPT-3 model (or any OpenAI model you want) to 
analyze and reorganize files and directories in your current working directory (cwd) on your Mac. It generates and 
executes a series of bash commands to optimally organize your files and 
directories.

# Usage
Set your OpenAI API key as an environment variable named OPENAI_API_KEY.
Run the script with the command `python main.py`.

# Requirements
- Python 3.6 or higher
- requests module
- OpenAI API key

# Note
This script modifies your file system by moving files and directories. Always 
review the commands before executing them to ensure they won't cause any unwanted 
changes to your file system.
