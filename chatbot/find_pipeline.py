from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
import pickle
import os

class Document:
    def __init__(self, page_content, metadata):
        self.page_content = page_content
        self.metadata = metadata

def create_index():
    with open('index.pkl', 'rb') as inp:
        chunks = pickle.load(inp)

    data = []
    for repo, readme in chunks:
        metadata = {'source': f"https://github.com/{repo}", 'tool': repo}
        document = Document(page_content=readme, metadata=metadata)
        data.append(document)

    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_documents(data, embedding=embeddings)
    vectorstore.save_local("vectorstore/db_faiss")

def load_index():
    if not os.path.exists("vectorstore/db_faiss"):
        create_index()
    embeddings = OpenAIEmbeddings()
    return FAISS.load_local("vectorstore/db_faiss", embeddings, allow_dangerous_deserialization=True)

def get_llm():
    return ChatOpenAI(temperature=0.0, model_name="gpt-3.5-turbo")

def get_preliminary_prompt():
    prompt = """
    System: You are a bioinformatician. Given a query, reference documents, and the chat history,
    I want you to determine whether the query is
    1) A query about general bioinformatics or earlier chat that you can answer directly. 
    2) A query about nextflow pipelines that you can answer given the provided documents
        and/or chat history.
    3) A request to run a tool.
    4) A query that is not about bioinformatics and you also cannot answer given the 
        provided documents and chat history. 
    Output a single number matching any one of these.
    Here is the chat history: "{chat_history}"
    Here is the context from the provided documents: "{context}"
    Here is the query: "{question}"
    """
    return ChatPromptTemplate.from_template(prompt)

def get_prompt_1():
    prompt = """
    System: You are a bioinformatician with an undying passion for nf-core.
    Answer the given query.
    Here is the chat history: "{chat_history}"
    Here is the given query: "{question}"
    """
    return ChatPromptTemplate.from_template(prompt)

def get_prompt_2():
    prompt = """
    System: You are a bioinformatician with an undying passion for nf-core. Answer
    the given query using the provided documents for accuracy.
    Here is the chat history: "{chat_history}"
    Here is the context from the provided documents: "{context}"
    Here is the query you need to answer: "{question}"
    """
    return ChatPromptTemplate.from_template(prompt)

def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)


if __name__ == "__main__":
    if "OPENAI_API_KEY" in os.environ:
        api_key = os.environ["OPENAI_API_KEY"]
    else:
        api_key = input("Please enter your OpenAI API key: ")
        os.environ["OPENAI_API_KEY"] = api_key
    
    vectorstore = load_index()
    llm = get_llm()
    chat_history = ""

    while True:
        query = input("Please enter your query or 'exit':\n")
        if query == 'exit':
            break

        documents = vectorstore.similarity_search(query)
        similar_embeddings = FAISS.from_documents(documents=documents[:2], embedding=OpenAIEmbeddings())
        retriever = similar_embeddings.as_retriever()

        preliminary_chain = (
                {"context": retriever | format_docs, "question": RunnablePassthrough(), "chat_history": lambda x: chat_history}
                | get_preliminary_prompt()
                | llm
                | StrOutputParser()
        )

        query_type = preliminary_chain.invoke(query).strip()

        if query_type == 1:
            rag_chain = (
                {"question": RunnablePassthrough(), "chat_history": lambda x: chat_history}
                | get_prompt_1()
                | llm
                | StrOutputParser()
            )
            response = rag_chain.invoke(query)
        elif query_type == 2: 
            rag_chain = (
                {"context": retriever | format_docs, "question": RunnablePassthrough(), "chat_history": lambda x: chat_history}
                | get_prompt_2()
                | llm
                | StrOutputParser()
            )
            response = rag_chain.invoke(query)
        elif query_type == 3:
            tool = documents[0].metadata['tool']
            response = f"You are looking to run a tool. We have determined that {tool} is an appropriate one for this task. y/n?"
            chat_history += f"Question: {query}\n Bot response: {response}"

            query = input(response)

            if query[0].lower() == 'y':
                if tool == "nf-core/ampliseq":
                    pipeline_talk(tool)
            
            response = f"OK! Let's continue the conversation then!"    
        else:
            response = "This query is not about bioinformatics and also cannot be answered given our previous conversation"
        
        print(response)
        chat_history += f"User input: {query}\n Bot response: {response}"
