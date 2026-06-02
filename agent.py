import os
import subprocess
from dotenv import load_dotenv
from pydantic import SecretStr
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage


load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is not set in the environment variables.")

groq_client = ChatGroq(api_key = SecretStr(GROQ_API_KEY), model = "llama-3.1-8b-instant", temperature = 0)


def execute_code(code_string: str) -> dict:
    with open("generated_workspace.py", "w", encoding="utf-8") as code_file:
        code_file.write(code_string)

    result = subprocess.run(["python3", "generated_workspace.py"], capture_output = True, text = True)

    if result.returncode == 0:
        return {"success": True, "output": result.stdout}
    
    return {"success": False, "error": result.stderr}


messages = [
    SystemMessage(content = "You are an expert Python developer."),
    HumanMessage(content = "Write a 2-line Python script that prints 'Hello, Team Lead'. Output only the code.")
]

response = groq_client.invoke(messages)
raw_content = response.content
if isinstance(raw_content, str):
    code_string = raw_content
elif isinstance(raw_content, list):
    code_string = "".join(str(item) for item in raw_content)
else:
    code_string = str(raw_content)

execution_result = execute_code(code_string)
print(execution_result)


