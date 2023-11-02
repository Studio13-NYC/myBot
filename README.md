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

## Installation - very rough draft

### Download Code from GitHub and Set Up the Project

1. **Download and Install Git**: Git is a version control system that GitHub is built on. You can download it from the [official Git website](https://git-scm.com/downloads). During installation, choose "Git Bash Here" and "Windows Command Prompt" options for easy access to Git.

2. **Clone the GitHub repository**: Open Command Prompt, navigate to the directory where you want to download the code(say C:\projects) , and run the following command:

    ```cmd
    git clone https://github.com/Studio13-NYC/myBot.git
    ```


3. **Navigate to the cloned repository**: Use the `cd` command to navigate into the cloned repository:

    ```cmd
    cd myBot
    ```


4. **Create a virtual environment**: In the root directory of your project (say c:\projects\mybot), you can create a virtual environment using the `venv` module:

    ```cmd
    python -m venv .venv
    ```

5. **Activate the virtual environment**: Before you can start installing or using packages in the virtual environment, you'll need to activate it. On Windows, you can do this with the following command:

    ```cmd
    .venv\Scripts\activate
    ```

6. **Install the application**: 
if your virtual environment is activated, you should see a (.venv) at the beginning of your command prompt.
so your path might look like this: 
powershell
(.venv) PS C:\projects\myBot> 
or
cmd
(.venv) C:\projects\myBot> 

 run `pip install -r requirements.txt` to install the dependencies.
```
(.venv) C:\projects\myBot>pip install -r requirements.txt```
```
 when this completes, the application is installed and ready to run.

7. **Run the application**: 
Run `chainlit run app.py -w` to start the application.
like this 
```
(.venv) C:\projects\myBot>chainlit run app.py -w
```






Version 0.0.1