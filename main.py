import time

from src.planner import run_planner
from src.code_generator import generator
from src.tester import tester
from src.debugger import debugger

user_input = "Create a sql database for a library application with a login page."

print("Running Planner Agent to get subtasks...")
tasks = run_planner(user_input)
print("Subtasks found:")
for t in tasks:
    print(f"- {t}")

print("\nGenerating code for each subtask...")
code_dict = generator(user_input, tasks)

current_code = code_dict.copy()

MAX_RETRIES = 3

for attempt in range(1, MAX_RETRIES + 1):
    print(f"\n--- Testing Attempt {attempt} ---")
    test_results = tester(current_code)

    all_passed = True
    for task, result in test_results.items():
        print(f"\n=== Test Result for Task: {task} ===")
        print(f"Status: {result['result']}")
        print(result['details'])

        if result['result'] != "PASSED":
            all_passed = False

            error_trace = result.get('details', 'No traceback info')

            print(f"\nRunning Debugger Agent on task: {task} ...")
            fix_result = debugger(current_code[task], error_trace)

            if fix_result.get("status") == "FIXED":
                print("Debugger applied a fix.")
                current_code[task] = fix_result["fixed_code"]
            else:
                print("Debugger could not fix the issue automatically.")

    if all_passed:
        print("\nAll tests passed successfully!")
        break
    else:
        print(f"\nRetrying after fixes... (Attempt {attempt} complete)")
        time.sleep(1)

else:
    print("\nMax retries reached. Some tests are still failing.")

print("\n=== Final Code Output ===")
for task, code in current_code.items():
    print(f"\n--- Code for Task: {task} ---\n")
    print(code)
