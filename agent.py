import os
import subprocess
import logging
from dotenv import load_dotenv
from pydantic import SecretStr
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

# --- Logging Setup ---
# Configure standard logging
logging.basicConfig(level = logging.INFO, format = "%(message)s")
# Silence the annoying HTTP request logs from LangChain's network libraries
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)

# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
# Rather than crashing with a KeyError later, we check for the API key upfront and raise a clear error if it's missing.
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is not set in the environment variables.")

# Initialize the Groq client with the API key and desired model parameters
groq_client = ChatGroq(
    api_key=SecretStr(GROQ_API_KEY), model = "llama-3.1-8b-instant", temperature = 0
)


def clean_code(raw_text: str) -> str:
    """
        Removes markdown backticks if the AI accidentally includes them.
        This is a common issue where the AI might wrap code in markdown formatting, which would cause syntax errors when we try to execute it."""
    cleaned = raw_text.replace("```python", "").replace("```", "").strip()

    return cleaned


def execute_code(code_string: str) -> dict:
    """
        Writes the code to a file and executes it via subprocess.
    """
    with open("generated_workspace.py", "w", encoding = "utf-8") as code_file:
        code_file.write(code_string)

    result = subprocess.run(
        ["python3", "generated_workspace.py"], capture_output = True, text = True
    )

    if result.returncode == 0:
        return {"success": True, "output": result.stdout}

    return {"success": False, "error": result.stderr}

# Configuration
MAX_RETRIES = 3
attempt = 0
logging.info("\n" + "=" * 60)
user_task = input("👨‍💻 What would you like the AI to build? \n> ")
logging.info("=" * 60 + "\n")

# We start with a system message that sets the behavior of the AI, and a human message that contains the user's task. As we loop, we will append to this messages list with the AI's generated code and the human's feedback on any errors, creating a conversation history that the AI can learn from to self-correct.
messages = [
    SystemMessage(
        content = """You are an autonomous, expert Python developer. Your only job is to write Python scripts to solve the user's request. CRITICAL INSTRUCTIONS:
- Output ONLY valid, executable Python code. 
- Do not include any explanations, greetings, or conversational text.
- Do not wrap the code in markdown formatting or backticks."""
    ),
    HumanMessage(
        content = f"Write a Python script to solve the following task: {user_task}"
    ),
]

# Main loop to allow the AI multiple attempts to self-correct
while attempt < MAX_RETRIES:
    logging.info(f"⏳ Attempt {attempt + 1} of {MAX_RETRIES} running...")
    # Invoke the Groq client with the current conversation history. The AI will generate code based on the user's task and any previous feedback.
    response = groq_client.invoke(messages)
    raw_content = response.content
    # The AI's response could be a string or a list of strings (if it tries to output code in parts). We need to handle both cases to construct the full code string that we will execute.
    if isinstance(raw_content, str):
        code_string = raw_content
    elif isinstance(raw_content, list):
        code_string = "".join(str(item) for item in raw_content)
    else:
        code_string = str(raw_content)

    # Clean the code before executing
    code_string = clean_code(code_string)

    # Execute it
    execution_result = execute_code(code_string)

    # Check the result and log appropriately. If it failed, we append the AI's code and the error message to the conversation history so that the AI can learn from its mistakes in the next iteration.
    if execution_result["success"]:
        logging.info("\n✅ SUCCESS! The code ran perfectly.")
        logging.info("-" * 40)
        # THIS IS THE FIX: Actually printing the output of the script!
        logging.info(execution_result["output"]) 
        logging.info("-" * 40)
        break
    else:
        error_msg = execution_result["error"]
        logging.error("\n❌ FAILED! The code threw an error:")
        logging.error(error_msg.strip())
        logging.info("Sending error back to the AI for self-correction...\n")
        
        # Append the AI's generated code to the history first
        messages.append(AIMessage(content=code_string))
        
        # Then append the human message with the error traceback
        messages.append(
            HumanMessage(
                content = f"Your previous code failed with this error:\n{error_msg}\nPlease provide only the corrected Python code."
            )
        )
        attempt += 1

if attempt == MAX_RETRIES:
    logging.error("\n🛑 AI failed to solve the problem after maximum attempts.")