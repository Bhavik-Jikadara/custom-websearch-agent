from langchain_openai import ChatOpenAI
from src.utils import load_config
import os
from dotenv import load_dotenv
load_dotenv()

config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'config.yaml')
load_config(config_path)


def get_open_ai(temperature=0, model=os.getenv("OPENAI_MODEL_NAME")):
    llm = ChatOpenAI(
        model=model,
        temperature = temperature,
    )
    return llm

def get_open_ai_json(temperature=0, model=os.getenv("OPENAI_MODEL_NAME")):
    llm = ChatOpenAI(
        model=model,
        temperature = temperature,
        model_kwargs={"response_format": {"type": "json_object"}},
    )
    return llm