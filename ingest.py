"""
ingest anything create embeddings and metadata and load into pinecone index
"""

# ingest.py is the script that will ingest the data into the vector database (pinecone) with metadata and embeddings
# https://gpt-index.readthedocs.io/en/latest/understanding/loading/loading.html - baseline for what is here
# https://llamahub.ai/ - llama hub is loader and tools for llama index
# https://github.com/run-llama/llama-hub/tree/main
# https://gpt-index.readthedocs.io/en/latest/examples/metadata_extraction/MetadataExtractionSEC.html - example of metadata extraction

import logging
import os
import sys

import graphsignal
import pinecone
import torch

from llama_index import (ServiceContext, SimpleDirectoryReader,
                         StorageContext, VectorStoreIndex, set_global_service_context)
from llama_index.embeddings import OpenAIEmbedding
from llama_index.indices.prompt_helper import PromptHelper
from llama_index.llms import OpenAI
from llama_index.node_parser import SimpleNodeParser
from llama_index.node_parser.extractors import (EntityExtractor, KeywordExtractor,
                                                MetadataExtractor, QuestionsAnsweredExtractor,
                                                SummaryExtractor, TitleExtractor)
from llama_index.text_splitter import TokenTextSplitter
from llama_index.vector_stores import PineconeVectorStore



# Set up logging
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

# setup graphsignal tracing for debugging
##GRAPHSIGNAL_API_KEY = os.environ["GRAPHSIGNAL_API_KEY"]
graphsignal.configure(api_key='cc451d52547c1a0a01a2e9c33ff4c7c6', deployment='my-app-prod')

# setup system tests
# test to see if cuda is available
cuda_available = torch.cuda.is_available()

# These are user defined variables - they should be moved into .env or somehting
DOC_PATH = r"soucedocs"  # be sure to keep the r in front of the string to make it a raw string
SPLITTER_CHUNK_SIZE = 1024
SPLITTER_CHUNK_OVERLAP = 20
NODE_CHUNK_SIZE = 200
NODE_CHUNK_OVERLAP = 20
LLM_MODEL_MODEL = "gpt-4"
LLM_MAX_TOKENS = 3000
EMBED_MODEL_MODEL = "text-embedding-ada-002"
CONTEXT_WINDOW = 500

# Metadata variables
PRODUCT_NAME = "myBot"
DATA_VERSION = "v0.0.1"
USERNAME = "username"
RELEASE_STATUS = "dev"  # test, dev, prod

# set up OpenAI API
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

# Set up Pinecone - assumes you have an index already created
PINECONE_INDEX_NAME = "s13"
PINECONE_ENVIRONMENT = "gcp-starter"
PIENCONE_API_KEY = os.getenv("PINECONE_API_KEY")
pinecone.init(api_key=PIENCONE_API_KEY, environment=PINECONE_ENVIRONMENT)
pinecone_index = pinecone.Index(PINECONE_INDEX_NAME)

# Set up the vector store
vector_store = PineconeVectorStore(pinecone_index=pinecone_index)

# Set up the storage context
storage_context = StorageContext.from_defaults(vector_store=vector_store)

# set the LLM
llm = OpenAI(
    temperature=0.1,
    model=LLM_MODEL_MODEL,
    max_tokens=LLM_MAX_TOKENS,
    api_key=OPENAI_API_KEY,
)

# Define metadata
metadata = {
    "product_name": PRODUCT_NAME,
    "data_version": DATA_VERSION,
    "username": USERNAME,
    "release_status": RELEASE_STATUS,
}

# Set up the text splitter
text_splitter = TokenTextSplitter(
    separator=" ",
    chunk_size=SPLITTER_CHUNK_SIZE,
    chunk_overlap=SPLITTER_CHUNK_OVERLAP,
    backup_separators=["\n"],
)

# Set up the metadata extractor
# The MetadataExtractor class is used to extract metadata from TextNodes.
metadata_extractor = MetadataExtractor(
    extractors=[
        TitleExtractor(nodes=5, llm=llm),
        QuestionsAnsweredExtractor(questions=3, llm=llm),
        EntityExtractor(
            prediction_threshold=0.5,
            #it will load the Entity Extractor on the gpu if it is available
            device="cuda" if cuda_available else "cpu",
            label_entities=True,
        ),
        SummaryExtractor(summaries=["self"], llm=llm),
        KeywordExtractor(keywords=5, llm=llm),
        # CustomExtractor()
    ],
)

# Set up the node parser
node_parser = SimpleNodeParser.from_defaults(
    chunk_size=NODE_CHUNK_SIZE,
    chunk_overlap=NODE_CHUNK_OVERLAP,
    text_splitter=text_splitter,
    include_metadata=True,
    include_prev_next_rel=True,
    metadata_extractor=metadata_extractor,
)

#Set up the embed model
embed_model=OpenAIEmbedding(
    api_key=OPENAI_API_KEY,
    temperature=0.1,
    model=EMBED_MODEL_MODEL
    )

# Set up the prompt helper
prompt_helper=PromptHelper(
    context_window=CONTEXT_WINDOW,
)

#set up ServiceContext
service_context = ServiceContext.from_defaults(
    llm=llm,
    embed_model=embed_model,
    node_parser=node_parser,
    prompt_helper=prompt_helper,
    )

# set ServiceContext as global
set_global_service_context(service_context)

# Loading the data
# The SimpleDirectoryReader class is used to load a directory of documents.
documents = SimpleDirectoryReader(DOC_PATH).load_data()

# Update the metadata for each document
for document in documents:
    document.metadata.update(metadata)

# Construct nodes from the document text
my_nodes = node_parser.get_nodes_from_documents(documents)

# Generate embeddings for each node
for node in my_nodes:
    node_embedding = embed_model.get_text_embedding(
        node.get_content(metadata_mode="all")
    )
    node.embedding = node_embedding
    node.metadata.update(metadata)


storage_context.vector_store.add(my_nodes)

index = VectorStoreIndex.from_documents(
    documents,
    service_context=service_context,
    show_progress=True,
    storage_context=storage_context,
)


for node in my_nodes:
    print(node)
    print(node.metadata)
    print(node.embedding)
    print(node.excluded_embed_metadata_keys)
    print(node.id_)
