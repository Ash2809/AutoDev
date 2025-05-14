from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from dotenv import load_dotenv
import os
import re
import warnings

warnings.filterwarnings("ignore")
load_dotenv()

def clean_task_line(line):
    line = re.sub(r"\*\*(.*?)\*\*", r"\1", line)  
    line = re.sub(r"^[\s*\-•]+", "", line)      
    return line.strip()


def run_planner(user_input: str):
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

    llm = ChatGoogleGenerativeAI(
        temperature=0.4,
        model="gemini-1.5-flash",
        api_key=GOOGLE_API_KEY
    )

    template = """
    You are the Planner Agent. 
    Your task is to break down the user's high-level prompt into smaller subtasks for code generation.

    User Request: {user_input}

    Return each task as a bullet point list.
    """

    prompt = PromptTemplate(
        input_variables=["user_input"],
        template=template
    )

    chain = LLMChain(llm=llm, prompt=prompt)
    response = chain.run(user_input)

    tasks = [
        clean_task_line(task)
        for task in response.strip().split("\n")
        if task.strip()
    ]

    return tasks

if __name__ == "__main__":
    user_input = "Create a simple library application with a login page."
    tasks = run_planner(user_input)
    print("Subtasks:")
    for task in tasks:
        print(f"- {task}")
