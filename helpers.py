import subprocess
import ast


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


FORBIDDEN_MODULES = {"os", "sys", "subprocess", "shutil", "socket"}
def validate_code_ast(code_string: str) -> dict:
    """
        Parses the code to check for forbidden imports before execution.
        This is a crucial security measure to prevent the AI from executing potentially harmful code that could access the filesystem, run shell commands, or perform network operations. By analyzing the abstract syntax tree (AST) of the code, we can detect any import statements and block those that reference dangerous modules."""
    try:
        tree = ast.parse(code_string)
    except SyntaxError as e:
        return {"valid": False, "error": f"SyntaxError during AST parsing: {e}"}

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                base_module = alias.name.split('.')[0]
                if base_module in FORBIDDEN_MODULES:
                    return {"valid": False, "error": f"Security Error: Importing '{base_module}' is strictly forbidden for security reasons."}
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                base_module = node.module.split('.')[0]
                if base_module in FORBIDDEN_MODULES:
                    return {"valid": False, "error": f"Security Error: Importing from '{base_module}' is strictly forbidden for security reasons."}
    
    return {"valid": True}
