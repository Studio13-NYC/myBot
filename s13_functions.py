import logging
import os
import subprocess
import sys

import chainlit as cl
import openai
import pinecone
from langchain.chat_models import ChatOpenAI
import json

import llama_index
from llama_index import LLMPredictor, ServiceContext, StorageContext
from llama_index.callbacks.base import CallbackManager
from llama_index.llms import OpenAI
from llama_index.query_engine.retriever_query_engine import \
    RetrieverQueryEngine


# PINECONE
#Magic number for the numbers for Pinecone
def get_pinecone_api_key():
    """Returns the Pinecone API key from the environment variables"""
    return os.getenv('PINECONE_API_KEY')

def get_pinecone_index_name():
    """Returns the Pinecone index name from the environment variables"""
    return "s13"

def get_pinecone_environment():
    """Returns the Pinecone environment from the environment variables"""
    return "gcp-starter"

def get_pinecone_dimensions():
    """Returns the Pinecone dimensions from the environment variables"""
    return 1536

def get_pinecone_metric():
    """Returns the Pinecone metric from the environment variables"""
    return "cosine"

def get_pinecone_shards():
    """Returns the Pinecone shards from the environment variables"""
    return 1

def get_pinecone_replicas():
    """Returns the Pinecone replicas from the environment variables"""
    return 0

#basic Functions for Pinecone

def create_pinecone_index(pinecone_index_name):
    """Creates a Pinecone index with the given name"""
    pinecone.init(api_key=get_pinecone_api_key(), environment=get_pinecone_environment())   
    pinecone.create_index(name=pinecone_index_name, dimension=get_pinecone_dimensions(), metric=get_pinecone_metric(), shards=get_pinecone_shards(), replicas=get_pinecone_replicas())

def is_existing_index(index_name):
    """Checks if the given index name exists in Pinecone"""
    pinecone.init(api_key=get_pinecone_api_key(), environment=get_pinecone_environment())
    index_list = pinecone.list_indexes()
    index_names = []
    for index in index_list:
            index_names.append(index_list)
    if index_name in index_list:
        return True
    else:
        return False
    

def get_pinecone_indexes_names():
    """Returns the names of the existing indexes in Pinecone"""
    pinecone.init(api_key=get_pinecone_api_key(), environment=get_pinecone_environment())
    index_list = pinecone.list_indexes()
    index_names = []
    for index in index_list:
            index_names.append(index_list)
    return index_names

# LLM Magic Functions


def get_openai_api_key():
    """Returns the OpenAI API key from the environment variables"""
    return os.getenv('OPENAI_API_KEY')

def define_llm(openai_api_key):
    """Defines the LLM with the given API key"""
    llm = OpenAI(temperature=0.1, model="gpt-4", max_tokens=512, api_key=openai_api_key)
    return llm


# utilities

def set_logging(enabled):
    """ Enables or disables logging."""
    if enabled:
        logging.basicConfig(stream=sys.stdout, level=logging.INFO)
        logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))
    else:
        logging.disable(logging.CRITICAL)

def set_observability(enabled):
    """ Enables or disables observability."""
    if enabled:
        llama_index.set_global_handler("simple")
    else:
        llama_index.set_global_handler(None)
def what_attributes(the_function):
    print([attr for attr in dir(the_function) if not attr.startswith('__')])


#authentications

def check_user_and_password(username, password):
    """Checks if the given username and password are valid"""
    with open('users.json', 'r') as f:
        people = json.load(f)
        for person in people:
            if person['username'] == username and person['password'] == password:
                return cl.AppUser(username=username, role=person['role'], provider=person['provider'])
    return None


