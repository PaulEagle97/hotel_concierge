import os
import openai
import chainlit as cl
from json import load
from datetime import datetime

from llama_index.core import (
    Settings,
    StorageContext,
    VectorStoreIndex,
    load_index_from_storage,
)
from llama_index.core import Document, set_global_handler, PromptTemplate
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core.callbacks import CallbackManager
from llama_index.core.storage.chat_store import SimpleChatStore
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.agent.openai import OpenAIAgent
from llama_index.llms.openai import OpenAI
from llama_index.core.base.llms.types import ChatMessage
from llama_index.core.tools import QueryEngineTool, ToolMetadata, FunctionTool
from dotenv import load_dotenv

def load_or_build_index(data_path: str, index_name: str):
    with open(data_path, 'r') as json_file:
        json_data = load(json_file)
    documents = [Document(**i) for i in json_data]    

    try:
        # rebuild storage context
        storage_context = StorageContext.from_defaults(persist_dir=f"./cache/{index_name}")
        # load index
        index = load_index_from_storage(storage_context)
    except:
        index = VectorStoreIndex.from_documents(documents)
        index.storage_context.persist(f'./cache/{index_name}')

    return index

def read_prompt(path):
    with open(path) as prompt:
        return prompt.read()

def call_taxi(full_name: str, destination: str, time: datetime):
    """Tool to call the taxi service with the provided client's data."""
     # call some localhost API endpoint
    print(f"Called taxi API with parameters:\nFull Name:{full_name}\nDestination:{destination}\nTime:{time}")


set_global_handler("simple")
load_dotenv()
openai.api_key = os.environ.get("OPENAI_API_KEY")

Settings.callback_manager = CallbackManager([cl.LlamaIndexCallbackHandler()])
Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-large")
Settings.context_window = 4096
VERBOSE_MODE = True
TOP_K = 5

LLM = OpenAI(
    model="gpt-4o",
    temperature=0.7,
    max_tokens=1024,
    # streaming=True
)

hotel_index = load_or_build_index('./datasets/salzburg_hotel.json', 'hotel')
city_index = load_or_build_index('./datasets/salzburg_city.json', 'city')

hotel_query_engine = hotel_index.as_query_engine(
                                                 llm=LLM,
                                                 text_qa_template=PromptTemplate(read_prompt('prompts/hotel_search_prompt.md')),
                                                 similarity_top_k=TOP_K,
                                                 verbose=VERBOSE_MODE)

city_query_engine = city_index.as_query_engine(
                                               llm=LLM,
                                               text_qa_template=PromptTemplate(read_prompt('prompts/city_search_prompt.md')),
                                               similarity_top_k=TOP_K,
                                               verbose=VERBOSE_MODE)


hotel_tool = QueryEngineTool(
    hotel_query_engine,
    ToolMetadata(
        description=(
            "Tool to get a specific information for anything regarding Hotel Sacher and its services."
        ),
        name="QA_Tool_Hotel",
        return_direct=False
    )
)

city_tool = QueryEngineTool(
    city_query_engine,
    ToolMetadata(
        description=(
            "Tool to get a specific information for anything regarding the city of Salzburg."
        ),
        name="QA_Tool_City",
        return_direct=False
    )
)

taxi_tool = FunctionTool.from_defaults(fn=call_taxi)


@cl.on_chat_start
async def start():
    check_in_msg = read_prompt('prompts/check_in_confirm.md')

    await cl.Message(
        author="Assistant",
        content=check_in_msg
    ).send()

    chat_memory = ChatMemoryBuffer.from_defaults(
        chat_history=[ChatMessage(content=check_in_msg, role="assistant")],
        token_limit=3000,
        chat_store=SimpleChatStore(),
        chat_store_key="user1",
    )

    current_date = datetime.now().strftime("%Y-%m-%d")
    agent_prompt = read_prompt('prompts/agent_system_prompt.md').replace("{date}", current_date)

    agent = OpenAIAgent.from_tools(
        tools=[hotel_tool, city_tool, taxi_tool],
        memory=chat_memory,
        llm=LLM,
        verbose=VERBOSE_MODE,
        system_prompt=agent_prompt,
    )

    cl.user_session.set("agent", agent)



@cl.on_message
async def main(message: cl.Message):
    agent = cl.user_session.get("agent") # type: OpenAIAgent

    msg = cl.Message(content="", author="Assistant")

    res = agent.stream_chat(message.content)

    for token in res.response_gen:
        await msg.stream_token(token)
    await msg.send()

