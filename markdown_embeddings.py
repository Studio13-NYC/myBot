#markdown_embeddings.py
import os
import logging
import sys
import yaml
from dotenv import load_dotenv
import pinecone
from llama_index.vector_stores import PineconeVectorStore
from llama_index.text_splitter import SentenceSplitter
from llama_index.schema import TextNode
from llama_index.node_parser.extractors import MetadataExtractor, QuestionsAnsweredExtractor, TitleExtractor, SummaryExtractor, EntityExtractor, KeywordExtractor
from llama_index.node_parser.file import markdown
from llama_index.llms import OpenAI
from llama_index.embeddings import OpenAIEmbedding
from llama_index import ObsidianReader, VectorStoreIndex,StorageContext
from llama_index.schema import Document


#Set Version and Project Metadata Tags
project_name="myBot"
data_version="v0.0.1"
other_value="username"

# Set up logging
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

# Load environment variables
dotenv_path = "env"
load_dotenv(dotenv_path=dotenv_path)

# Initialize Pinecone and create an index
api_key = os.getenv('PINECONE_API_KEY')
environment ="gcp-starter"
pinecone.init(api_key=api_key, environment=environment)
index_name = "s13"
pinecone_index = pinecone.Index(index_name)
vector_store = PineconeVectorStore(pinecone_index=pinecone_index)
storage_context = StorageContext.from_defaults(vector_store=vector_store)


# Load your Markdown documents
documents = ObsidianReader("source_docs").load_data()
index = VectorStoreIndex.from_documents(documents, storage_context=storage_context)
document = Document()

# Construct nodes from the document text - note that the Obsidian reader returns a list of documents
nodes = [TextNode(text=document.text) for document in documents]
# Initialize the language model and metadata extractor
llm = OpenAI(model="gpt-4")
metadata_extractor = MetadataExtractor(
    extractors=[
        TitleExtractor(nodes=5, llm=llm),
        QuestionsAnsweredExtractor(questions=3, llm=llm),
        SummaryExtractor(llm=llm),  
        #EntityExtractor(llm=llm, num_entities=10),
        #KeywordExtractor(llm=llm, num_keywords=10),
    ],
    in_place=False,
)

# Process the nodes to extract metadata
nodes = metadata_extractor.process_nodes(nodes)

# Generate embeddings for each node
embed_model = OpenAIEmbedding()
for node in nodes:
    node_embedding = embed_model.get_text_embedding(node.get_content(metadata_mode="all"))
    node.embedding = node_embedding
    node.metadata['project'] = project_name
    node.metadata['version'] = data_version
    node.metadata['other'] = other_value


# Load nodes into the vector store
vector_store.add(nodes)


