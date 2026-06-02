import os
import subprocess
import logging
import re
from dotenv import load_dotenv
from pydantic import SecretStr
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from helpers import clean_code, execute_code, validate_code_ast

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

# Configuration
MAX_RETRIES = 3
attempt = 0
logging.info("\n" + "=" * 60)
user_task = input("👨‍💻 What would you like the AI to build? \n> ")
logging.info("=" * 60 + "\n")
needs_new_code = True  # Flag to determine if we need to ask the AI for new code or just retry the same code after auto-installing a package
code_string = ""  # Initialize code_string to ensure it's defined before the loop

# We start with a system message that sets the behavior of the AI, and a human message that contains the user's task. As we loop, we will append to this messages list with the AI's generated code and the human's feedback on any errors, creating a conversation history that the AI can learn from to self-correct.
messages = [
    SystemMessage(
        content = """You are an autonomous, expert Python developer. Your only job is to write Python scripts to solve the user's request. 
CRITICAL INSTRUCTIONS:
1. Output ONLY valid, executable Python code. 
2. Do not include any explanations, greetings, or markdown formatting (no ```python).
3. TEST-DRIVEN DEVELOPMENT: You MUST encapsulate your logic inside a function. At the bottom of your script, you MUST write at least 3 `assert` statements to test your function against different edge cases.
4. If an assertion fails, include a descriptive custom error message in the assert statement.
5. At the very end of your script, if all asserts pass, write a print statement saying '✅ All unit tests passed!' and print the result of the function."""
    ),
    HumanMessage(
        content = f"Write a Python script to solve the following task: {user_task}"
    ),
]

# Main loop to allow the AI multiple attempts to self-correct
while attempt < MAX_RETRIES:
    if needs_new_code:
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

    # Validate the code for security before executing. This is a critical step to prevent the execution of harmful code that could damage the system or compromise security. By parsing the code's abstract syntax tree (AST), we can detect any import statements and block those that reference forbidden modules like os, sys, subprocess, etc. If the validation fails, we log a security warning and send a message back to the AI asking it to rewrite the code without using the forbidden module, then we continue to the next iteration of the loop without executing any code.
    validation = validate_code_ast(code_string)
    if not validation["valid"]:
        logging.error(f"\n🚫 SECURITY BLOCK: {validation['error']}")
        logging.info("Sending security warning back to AI...\n")
        
        messages.append(AIMessage(content=code_string))
        messages.append(HumanMessage(
            content=f"Your code was blocked by the security linter:\n{validation['error']}\nPlease rewrite the code without using the forbidden module to accomplish the task."
        ))
        needs_new_code = True
        attempt += 1
        continue

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
        # New feature: Auto-detect missing packages and attempt to install them without needing to ask the AI for new code. This is a common issue where the AI forgets to include an import statement for a package it uses, leading to a ModuleNotFoundError. By catching this specific error, we can extract the missing package name and run pip install automatically, then immediately retry the same code.
        if "ModuleNotFoundError" in error_msg:
            # Extract the package name using Regex
            match = re.search(r"No module named '(.+?)'", error_msg)
            if match:
                package_name = match.group(1)
                logging.info(f"\n📦 Missing package detected: '{package_name}'. Auto-installing...")
                
                # Run pip install (using python3 -m pip to ensure it goes into the venv)
                pip_result = subprocess.run(
                    ["python3", "-m", "pip", "install", package_name], 
                    capture_output = True, 
                    text = True
                )
                
                if pip_result.returncode == 0:
                    logging.info(f"✅ Successfully installed '{package_name}'! Re-running the same code...\n")
                    needs_new_code = False  # Don't ask the AI for new code
                    continue                # Instantly restart the while loop to re-execute
                else:
                    logging.error(f"❌ Failed to auto-install '{package_name}'. Falling back to AI for help.")

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