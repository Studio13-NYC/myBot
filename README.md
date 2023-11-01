# myBot
This is a project that provides an intermediate level RAG Pipeline
allowing the user to create a knowledge base from a set of documents
that can be queried by a user in a conversational manner.

## The project is built on top of the following technologies:
- [OpenAI's GPT-4](https://openai.com/blog/openai-api/)
- [Llama-Index](https://gpt-index.readthedocs.io/en/stable/)
- [Pinecone.ai](https://www.pinecone.io/)
- [Chainlit](https://docs.chainlit.io/get-started/overview)
- Python 3.11 (3.8+ should work)    
- The application can be run locally or deployed to the cloud.
- for cloud deployment, we have tested the application on Azure Applications Services.
- the application has been tested on Windows 11. 
- Mac & Linux users should be able to run the application with minimal changes.
 
Note: myBot is currently set up to discuss large language models based on some very simple markdown formatted documents that I had ChatGPT write for me. If you run this you would need to change the documents and the topic to something that you want to discuss. And then you would need to run markdown_embeddings.py to create the embeddings for the documents.

You will also need to set up accounts and get API keys for the following services:
- [OpenAI's GPT-4](https://openai.com/blog/openai-api/)
- pinecone.ai key   
- Chainlit
 
 You will also need to create a Chainlit Auth Secret. See the Chainlit documentation for details.


Version 0.0.1