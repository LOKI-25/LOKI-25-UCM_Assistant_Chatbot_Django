# In chat/chatbot_service.py

import os
from dotenv import load_dotenv

# Import all your LangChain components
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.docstore.document import Document
from langchain.retrievers import BM25Retriever, EnsembleRetriever
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

# --- Configuration ---
load_dotenv()
CHROMA_DIR = "/Users/lokesh/Desktop/Folder/Test/ucmbot-refreshed/ucmo_chroma_store" # Make sure this path is correct
EMBEDDING_MODEL = "text-embedding-3-large"
LLM_MODEL = "gemini-1.5-pro"

class ChatbotService:
    def __init__(self):
        print("--- Initializing Chatbot Service ---")
        self.rag_chain = self._build_rag_chain()
        print("✅ Chatbot Service Initialized.")

    def _build_rag_chain(self):
        # 1. Initialize components
        embedding_function = OpenAIEmbeddings(model=EMBEDDING_MODEL)
        llm = ChatGoogleGenerativeAI(model=LLM_MODEL, temperature=0.2)
        
        # 2. Set up the base EnsembleRetriever for Hybrid Search
        vector_store = Chroma(
            persist_directory=CHROMA_DIR,
            embedding_function=embedding_function
        )
        vector_retriever = vector_store.as_retriever(search_kwargs={"k": 10})
        
        all_docs = vector_store.get(include=["metadatas", "documents"])
        all_chunks = [
            Document(page_content=doc, metadata=meta)
            for doc, meta in zip(all_docs['documents'], all_docs['metadatas'])
        ]
        bm25_retriever = BM25Retriever.from_documents(all_chunks)
        bm25_retriever.k = 10

        ensemble_retriever = EnsembleRetriever(
            retrievers=[bm25_retriever, vector_retriever],
            weights=[0.5, 0.5]
        )

        # 3. Set up the MultiQueryRetriever
        multi_query_retriever = MultiQueryRetriever.from_llm(
            retriever=ensemble_retriever, llm=llm
        )

        # 4. Define the prompt template
        prompt_template = """
        You are ChatUCM, a friendly and knowledgeable AI assistant for the University of Central Missouri (UCM). 
  Your job is to answer the user's question, using the provided context as the primary source of truth. 
  You can elaborate on the topics mentioned in the context with your general knowledge to provide a more complete and approachable answer. 
  If the context doesn't mention the topic at all, politely state you don't have that specific information.
  Please answer in a conversational style that is engaging and helpful.Use formatting like paragraphs and bullet points to make complex information easy to understand.

        Context:
        {context}

        Question:
        {question}

        Answer:
        """
        prompt = ChatPromptTemplate.from_template(prompt_template)

        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)

        return (
            {"context": multi_query_retriever | format_docs, "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )

    def ask_question(self, question: str):
        """Asks a question to the RAG chain and gets an answer."""
        return self.rag_chain.invoke(question)

# Create a single, global instance of the service to be used by Django
# This ensures the models are loaded only once.
chatbot_instance = ChatbotService()