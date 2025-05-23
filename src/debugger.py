import re
import traceback
from typing import Optional

def parse_traceback(error_trace: str) -> dict:
    """
    Parse the Python traceback string to extract error type, message, and line number.
    """
    match = re.search(r'File ".*", line (\d+), in .*\n\s+(.*Error.*)', error_trace, re.DOTALL)
    if match:
        line_no = int(match.group(1))
        error_msg = match.group(2).strip()
    else:
        line_no = None
        error_msg = None

    last_line = error_trace.strip().split('\n')[-1]
    exc_type_msg = last_line.strip()

    return {
        "line_no": line_no,
        "error_msg": error_msg,
        "exception": exc_type_msg
    }

def fix_code(code: str, error_info: dict) -> Optional[str]:
    """
    Simple heuristic fixes based on error type.
    In real scenario, this can call an LLM API with prompt to fix code.
    """

    exception = error_info.get("exception", "")

    if "SyntaxError" in exception:
        fixed_code = re.sub(r"```", "", code)
        return fixed_code

    if "NameError" in exception:
        undefined_var_match = re.search(r"name '(\w+)' is not defined", exception)
        if undefined_var_match:
            var_name = undefined_var_match.group(1)
            fixed_code = f"{var_name} = None\n" + code
            return fixed_code


    return None

def debugger(original_code: str, error_trace: str) -> dict:
    """
    Main Debugger function.
    Takes the original code and error trace, tries to fix the code,
    and returns a dict with status and fixed code or error info.
    """
    error_info = parse_traceback(error_trace)

    fixed_code = fix_code(original_code, error_info)

    if fixed_code:
        return {
            "status": "FIXED",
            "fixed_code": fixed_code,
            "error_info": error_info
        }
    else:
        return {
            "status": "UNFIXED",
            "error_info": error_info,
            "message": "Could not automatically fix the code."
        }

if __name__ == "__main__":
    # Example usage
    original_code = '''
def add(a, b)
    return a + b
'''

    error_trace = """
  File "temp.py", line 2
    def add(a, b)
                ^
SyntaxError: invalid syntax
"""

    result = debugger(original_code, error_trace)

    print("Debugger Result:")
    print(result)
