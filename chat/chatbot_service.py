# In chat/chatbot_service.py
# export GOOGLE_APPLICATION_CREDENTIALS="/Users/lokesh/Downloads/google-credentials.json"
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
from google.oauth2 import service_account
from django.conf import settings
import json

# --- Configuration ---
load_dotenv()
CHROMA_DIR = os.environ.get("CHROMA_DIR", "/app/ucmo_chroma_store")
EMBEDDING_MODEL = "text-embedding-3-large"
LLM_MODEL = "gemini-2.5-flash"
key_path = os.getenv("SERVICE_ACCOUNT_FILE")

class ChatbotService:
    def __init__(self):
        print("--- Initializing Chatbot Service ---")
        self.rag_chain = self._build_rag_chain()
        print("✅ Chatbot Service Initialized.")

    def _build_rag_chain(self):
        # 1. Initialize components
        embedding_function = OpenAIEmbeddings(model=EMBEDDING_MODEL)
        # llm = ChatGoogleGenerativeAI(model=LLM_MODEL, temperature=0.2)
        credentials = service_account.Credentials.from_service_account_file(key_path)
        llm = ChatGoogleGenerativeAI(model=LLM_MODEL, temperature=0.2, credentials=credentials)
        
        # 2. Set up the base EnsembleRetriever for Hybrid Search
        vector_store = Chroma(
            persist_directory=CHROMA_DIR,
            embedding_function=embedding_function
        )
        vector_retriever = vector_store.as_retriever(search_kwargs={"k": 5})
        
        all_docs = vector_store.get(include=["metadatas", "documents"])
        all_chunks = [
            Document(page_content=doc, metadata=meta)
            for doc, meta in zip(all_docs['documents'], all_docs['metadatas'])
        ]
        bm25_retriever = BM25Retriever.from_documents(all_chunks)
        bm25_retriever.k = 5

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
        Please strictly answer only to the questions relevant to UCM.
  Your job is to answer the user's question, using the provided context as the primary source of truth. 
  You can elaborate on the topics only if it is releated to university of central missouri. If the context mentions the topic, you can use the mentioned in the context with your general knowledge to provide a more complete and approachable answer. 
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
    
    async def ask_question_stream(self, question: str):
        full_response = ""
        # .astream() on the full chain will do retrieval first, then stream.
        async for chunk in self.rag_chain.astream(question):
            full_response += chunk
            yield f"data: {json.dumps({'token': chunk})}\n\n"

        # After the stream is finished, send a final "end" event.
        yield "event: end\ndata: {}\n\n"

# Create a single, global instance of the service to be used by Django
# This ensures the models are loaded only once.
chatbot_instance = ChatbotService()