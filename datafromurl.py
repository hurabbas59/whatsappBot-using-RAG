import pickle
from langchain_community.document_loaders import AsyncHtmlLoader
from langchain_community.document_transformers import Html2TextTransformer
from langchain_community.embeddings.openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from links import web_links  # Ensure this contains a list of URLs to process

class SimpleDocumentIndexer:
    def __init__(self, urls=web_links, model_name="text-embedding-ada-002", store_path="faiss_store"):
        self.urls = urls
        self.model_name = model_name
        self.store_path = store_path

    def process_documents(self):
        # Load and transform documents
        loader = AsyncHtmlLoader(self.urls)
        docs = loader.load()
        transformer = Html2TextTransformer()
        docs_transformed = transformer.transform_documents(docs)

        # Split documents
        splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(chunk_size=550, chunk_overlap=50)
        chunked_docs = splitter.split_documents(docs_transformed)

        # Embed documents and create FAISS index
        embeddings = OpenAIEmbeddings(model=self.model_name)
        faiss_store = FAISS.from_documents(documents=chunked_docs, embedding=embeddings)
        faiss_store.save_local(self.store_path)

