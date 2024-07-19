import yaml
import pickle
import os
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI


def load_command_docs(file_path):
    with open(file_path, 'r') as file:
        return list(yaml.safe_load_all(file))

def get_retriever():
    command_docs = load_command_docs('ampliseq_commands.yaml')

    embeddings = OpenAIEmbeddings()
    texts = [f"{doc['command_id']}: {doc['description']}\nUsage: {doc['usage']}" for doc in command_docs]
    vectorstore = FAISS.from_texts(texts, embeddings)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

    return retriever

def get_llm():
    return ChatOpenAI(temperature=0.0, model_name="gpt-3.5-turbo")

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

def get_prompt():
    template = """
    You are an assistant for the nf-core/ampliseq pipeline. Your task is to recommend the most appropriate command based on the user's query.
    Use the following pieces of context to inform your recommendations:

    {context}

    Based on this information and the user's query, recommend the most appropriate command.
    Include an explanation for why you're recommending this command and list any input placeholders that need to be filled.

    User Query: {query}

    Your response should be in this format:
    Recommended Command: [command_id]
    Explanation: [Your explanation here]
    Command to run: [Full command with placeholders]
    Input Placeholders:
    - [placeholder_name]: [description]
    ...

    Assistant: Based on the user's query and the provided context, here is my recommendation:

    """
    prompt = ChatPromptTemplate.from_template(template)
    return prompt

if __name__=="__main__":
    qa_chain = (
        {"context": get_retriever() | format_docs, "query": RunnablePassthrough()}
        | get_prompt()
        | get_llm()
        | StrOutputParser()
    )

    def recommend_command(query: str) -> str:
        result = qa_chain.invoke(query)
        return result

    # Usage
    query = "I want to run ampliseq for 16S rRNA gene sequencing"
    recommendation = recommend_command(query)
    print(recommendation)