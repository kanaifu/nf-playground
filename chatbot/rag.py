from langchain.chains import RetrievalQA
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import DocArrayInMemorySearch
from langchain_openai import OpenAIEmbeddings
from langchain_community.embeddings import HuggingFaceInstructEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.indexes import VectorstoreIndexCreator
from langchain_experimental.agents.agent_toolkits.csv.base import create_csv_agent
from langchain.agents.agent_types import AgentType
from langchain.memory import ConversationBufferMemory
import tiktoken
import os
import pickle

class Document:
    def __init__(self, page_content, metadata):
        self.page_content = page_content
        self.metadata = metadata    

def index():
    with open('index.pkl', 'rb') as inp:
        chunks = pickle.load(inp)

    data = []
    for repo, readme in chunks:
        metadata = {'source': f"https://github.com/{repo}"}
        document = Document(page_content=readme, metadata=metadata)
        data.append(document)

    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_documents(data, embedding=embeddings)
    return vectorstore

if __name__ == "__main__":
    if "OPENAI_API_KEY" in os.environ:
        api_key = os.environ["OPENAI_API_KEY"]
    else:
        api_key = input("Please enter your OpenAI API key: ")
        os.environ["OPENAI_API_KEY"] = api_key

    llm_model = "gpt-3.5-turbo"

    vectorstore = index()
    llm = ChatOpenAI(temperature=0.5, model_name="gpt-4")
    memory = ConversationBufferMemory(
    memory_key='chat_history', return_messages=True)
    conversation_chain = ConversationalRetrievalChain.from_llm(
            llm=llm,
            chain_type="stuff",
            retriever=vectorstore.as_retriever(),
            memory=memory
            )
    
    while True:
        query = input("Please enter your query or 'exit':\n")
        
        if query == 'exit':
            break

        result = conversation_chain.invoke({"question": query})
        # print(result)
        answer = result["answer"]
        print(answer)

