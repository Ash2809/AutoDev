from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from dotenv import load_dotenv
import os
import re
import warnings

warnings.filterwarnings("ignore")
load_dotenv()

def generator(user_input: str, task_list: list[str]) -> dict:
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

    llm = ChatGoogleGenerativeAI(
        temperature=0.4,
        model="gemini-1.5-flash",
        api_key=GOOGLE_API_KEY
    )

    template = """
    You are the Code Generator Agent. Generate clean, functional, and well-documented code for the given task.

    High-Level Project Request:
    {user_input}

    Specific Task to Implement:
    {task}

    Please ensure:
    - The code is complete and self-contained for the given task.
    - Include necessary imports.
    - Add comments to explain important logic.
    """

    prompt = PromptTemplate(
        input_variables=["user_input", "task"],
        template=template
    )

    chain = LLMChain(llm=llm, prompt=prompt)

    code_outputs = {}
    for task in task_list:
        try:
            response = chain.run({"user_input": user_input, "task": task})
            code_outputs[task] = response
        except Exception as e:
            code_outputs[task] = f"Error generating code: {str(e)}"

    return code_outputs

if __name__ == "__main__":
    user_input = "Create a simple library application with a login page."
    tasks = [
        "Design Database Schema: Define the database schema including tables for users and books.",
        "Create User Model/Class: Develop a class or model to represent a user, with registration and authentication methods.",
        "Implement Login Logic: Handle user login and session management.",
    ]

    code_dict = generator(user_input, tasks)

    for task, code in code_dict.items():
        print(f"\n=== Code for Task: {task} ===\n")
        print(code)
