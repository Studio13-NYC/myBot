"""
This is a simple chatbot that uses the LangChainLLM to generate responses. 
It will create a query engine when the chatbot is started and persist it 
in the user session. It will then retrieve the query engine from the 
user session when a message is received and use it to generate a response."""

import json
import logging
import sys
from typing import Optional

import chainlit as cl
import pinecone
from langchain.chat_models import ChatOpenAI
from llama_index import ServiceContext, VectorStoreIndex
from llama_index.callbacks.base import CallbackManager
from llama_index.chat_engine import ContextChatEngine
from llama_index.llms import LangChainLLM
from llama_index.memory import ChatMemoryBuffer
from llama_index.vector_stores import PineconeVectorStore
from llama_index.vector_stores.types import MetadataFilters, ExactMatchFilter

import s13_functions as s13

# This is what is used to enable debgging in VS Code
if __name__ == "__main__":
    from chainlit.cli import run_chainlit
    run_chainlit("app.py")

# Set up logging
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

# Initialize Pinecone client
pinecone.init(
    api_key=s13.get_pinecone_api_key(), environment=s13.get_pinecone_environment()
)


@cl.on_chat_start
async def factory():
    """this is a factory function that will be 
    called when the chatbot is started. It will create the 
    query engine and persist it in the user session"""
    my_system_prompt_message_content = open(
        "system_prompt.txt", "r", encoding='utf-8').read()
    llm = LangChainLLM(ChatOpenAI(
        temperature=0, model_name="gpt-4", streaming=True))
    service_context = ServiceContext.from_defaults(
        llm=llm,
        chunk_size=512,
        chunk_overlap=20,
        context_window=2048,
        callback_manager=CallbackManager([cl.LlamaIndexCallbackHandler()]),
        num_output=1000,
    )
    pinecone_index = pinecone.Index(s13.get_pinecone_index_name())
    vector_store = PineconeVectorStore(pinecone_index=pinecone_index)
    memory = ChatMemoryBuffer.from_defaults(llm=llm, token_limit=1500)
    index = VectorStoreIndex.from_vector_store(vector_store=vector_store)
    
    query_engine = index.as_chat_engine(
        chat_mode="context", 
        service_context=service_context,streaming=True,
        memory=memory,
        system_prompt= my_system_prompt_message_content, 
        similarity_top_k=4,
        filters=MetadataFilters(
            filters=[
                ExactMatchFilter(
                    key="project", value="myBot",
                    key = "version", value="v0.0.1",
                    key = "other", value="username")
            ]) 
        )


    # # Sending an action button within a chatbot message
    # actions = [
    #     cl.Action(name="action_button", label="Create the Formatted Summary", value="example_value", description="Click me!")
    # ]
    # await cl.Message(content="Interact with this action button:", actions=actions).send()
    # #persisting the query engine
    cl.user_session.set("query_engine", query_engine)


@cl.on_message
async def main(message):
    """
    this is the main function that will be called when a message is received. 
    It will retrieve the query engine from the user session and use it to generate a response
    """
    cl.user_session.get("user")
    query_engine = cl.user_session.get(
        "query_engine")  # type: ContextChatEngine
    response = await cl.make_async(query_engine.stream_chat)(message.content)
    response_message = cl.Message(content="")
    for token in response.response_gen:
        await response_message.stream_token(token=token)
    await response_message.send()
    label_list = []
    count = 1
    for sr in response.source_nodes:
        elements = [
            cl.Text(
                name="S" + str(count),
                content=f"{sr.node.text}",
                display="side",
                size="small",
            )
        ]
        response_message.elements = elements
        label_list.append("S" + str(count))
        await response_message.update()
        count += 1
    response_message.content += "\n\nSources: " + \
        ", ".join(label_list) + "\n\n"
    await response_message.update()


@cl.password_auth_callback
async def auth_callback(username: str, password: str) -> Optional[cl.AppUser]:
    """this is the authentication callback function that 
    will be called when a user tries to log in. 
    It will check the username and password against the users.json file"""
    with open("users.json", "r", encoding='utf-8') as f:
        people = json.load(f)
        for person in people:
            if person["username"] == username and person["password"] == password:
                return cl.AppUser(username)


# @cl.action_callback("action_button")
# async def on_action(action):
#     """this is the action callback function that will be called when the user 
#       interacts with the action button. It will retrieve the query engine from 
#       the user session and use it to generate a response"""
#     # Do something with the action
#     mySystemPromptMessageContent = open("sp_FormatSummary.txt", "r").read()
#     myqueryengine = cl.user_session.get("query_engine")
#     system_prompt= mySystemPromptMessageContent
#     cl.user_session.set("query_engine", myqueryengine)
#     myOpenAIApiKey = s13.get_openai_api_key()
#     mySystemPromptMessageContent = open("sp_FormatSummary.txt", "r").read()
#     llm=LangChainLLM(ChatOpenAI(temperature=0,model_name="gpt-4",streaming=True))
#     service_context = ServiceContext.from_defaults(llm=llm,chunk_size=512,
#       chunk_overlap=20,
#       context_window=2048,
#       callback_manager=CallbackManager(
#           [cl.LlamaIndexCallbackHandler()]),num_output=1000)
#     storage_context = LlamaStorageContext.from_defaults()
#     pinecone_index = pinecone.Index(s13.get_pinecone_index_name())
#     vector_store = PineconeVectorStore(pinecone_index=pinecone_index)
#     memory = ChatMemoryBuffer.from_defaults(llm=llm, token_limit=1500)
#     index = VectorStoreIndex.from_vector_store(vector_store=vector_store)
#     query_engine = index.as_chat_engine(
#         chat_mode="context",
#         service_context=service_context,streaming=True,
#         memory=memory,
#         system_prompt= mySystemPromptMessageContent
#         )
#     # Sending an action button within a chatbot message
#     actions = [
#         cl.Action(name="action_button", label="Create the Formatted Summary", value="example_value", description="Click me!")
#     ]
#     await cl.Message(content="Interact with this action button:", actions=actions).send()
#     """this is a factory function that will be called when the chatbot is started. It will create the query engine and persist it in the user session"""
#     #persisting the query engine
#     cl.user_session.set("query_engine", query_engine)

#     await cl.Message(content=f"Executed {action.name}").send()
#     """this is the action callback function that will be called when the user interacts with the action button. It will retrieve the query engine from the user session and use it to generate a response"""
#     # Optionally remove the action button from the chatbot user interface
#     # await action.remove()
