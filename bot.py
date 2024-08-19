from dotenv import load_dotenv
import os
import pickle
from redisManager import ChatHistoryManager
import openai
from langchain_core.prompts import PromptTemplate
from langchain_openai import OpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI
from prompts import prompts


load_dotenv()
WHATSAPP_ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN")
WHATSAPP_API_URL = os.getenv("WHATSAPP_API_URL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai.api_key = OPENAI_API_KEY



redis_manager = ChatHistoryManager()
embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")
vector_store = FAISS.load_local(
    "faiss_store", embeddings, allow_dangerous_deserialization=True
)





# Database for saving chathistory using redis - Done
# Format history -> done
# Extract doc from vector db -- done
# Run chain--done


def get_docs(query,top_k=4):

    results = vector_store.similarity_search(
    query=query,
    k=top_k,
    )
    formated_docs = ""
     

    for result in results:
        formated_docs += result.page_content

    return formated_docs

def run(chat_id,query):

    history = redis_manager.get_history(chat_id=chat_id)
    history_formated = ""
    if history:
        for hist in history:

            history_formated += f"USER: {hist['user']}\nAI assistant:{hist['assistant']}\n"

    docs = get_docs(query)

    prompt = PromptTemplate(
        input_variables=["chat_history","question","context"], template=prompts
    )
    llm = ChatOpenAI(model="gpt-4o-mini")
    chain = prompt | llm | StrOutputParser()
    data = {
        "chat_history":history_formated,
        "question":query,
        "context":docs
    }


    response =  chain.invoke(data)

    message = [{"user":query,"assistant":response}]
    redis_manager.add_chat_history(chat_id=chat_id,messages=message)
    
    return response

        

        
