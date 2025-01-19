from langgraph.graph import MessagesState
from dotenv import load_dotenv

load_dotenv()

class State(MessagesState):
    user_prompt: str
    list_of_docs: list[str]
