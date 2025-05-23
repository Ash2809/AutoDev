from tempfile import NamedTemporaryFile
import traceback
import importlib.util
import unittest
import os
import sys
import re

def sanitize_code(code: str) -> str:
    return re.sub(r"```(?:python)?|```", "", code).strip()

def is_python_code(code: str) -> bool:
    python_keywords = ["def ", "import ", "class ", "print(", "return ", ":", "self"]
    return any(keyword in code for keyword in python_keywords)

def tester(code_dict: dict) -> dict:
    results = {}

    for task, raw_code in code_dict.items():
        try:
            code = sanitize_code(raw_code)

            if not is_python_code(code):
                results[task] = {
                    "result": "SKIPPED",
                    "details": "Non-Python code detected. Tester Agent currently only supports testing Python code."
                }
                continue

            with NamedTemporaryFile(delete=False, suffix=".py", mode='w') as temp_file:
                temp_file.write(code)
                temp_file_path = temp_file.name

            module_name = os.path.splitext(os.path.basename(temp_file_path))[0]
            spec = importlib.util.spec_from_file_location(module_name, temp_file_path)
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)

            loader = unittest.TestLoader()
            suite = loader.loadTestsFromModule(module)
            runner = unittest.TextTestRunner(verbosity=2, resultclass=unittest.result.TestResult)

            result = runner.run(suite)

            if result.wasSuccessful():
                results[task] = {"result": "PASSED", "details": f"All {result.testsRun} tests passed."}
            else:
                error_msgs = []
                for test, err in result.errors + result.failures:
                    error_msgs.append(f"{test}:\n{err}")
                results[task] = {
                    "result": "FAILED",
                    "details": "\n".join(error_msgs)
                }

        except Exception:
            results[task] = {"result": "ERROR", "details": traceback.format_exc()}
        finally:
            if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
                os.remove(temp_file_path)

    return results


if __name__ == "__main__":
    sample_code_dict = {
        "Python Task": """
def add(a, b):
    return a + b

import unittest

class TestAdd(unittest.TestCase):
    def test_add(self):
        self.assertEqual(add(2, 3), 5)
""",
        "HTML Task": """
<!DOCTYPE html>
<html>
<head><title>Test</title></head>
<body><h1>Hello</h1></body>
</html>
"""
    }

    test_results = tester(sample_code_dict)

    for task, result in test_results.items():
        print(f"=== Test Result for Task: {task} ===")
        print(f"Status: {result['result']}")
        print(result['details'])
        print()
