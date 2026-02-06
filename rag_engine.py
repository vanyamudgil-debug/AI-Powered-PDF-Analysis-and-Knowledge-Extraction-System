import os
import fitz  # PyMuPDF
from langchain_classic.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_classic.chains import ConversationalRetrievalChain
from langchain_classic.memory import ConversationBufferMemory
from langchain_classic.prompts import PromptTemplate
from dotenv import load_dotenv

load_dotenv()

def get_pdf_text(pdf_docs):
    """
    Extracts text using PyMuPDF (fitz) which is better for math/layout.
    """
    text = ""
    for pdf in pdf_docs:
        # Read the stream from Streamlit
        doc = fitz.open(stream=pdf.read(), filetype="pdf")
        for page in doc:
            # "text" flag usually preserves spacing better than PyPDF2
            text += page.get_text() 
    return text

def get_text_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_text(text)
    return chunks

def get_vectorstore(text_chunks):
    """
    Creates a Vector Store (FAISS) using Local Embeddings (HuggingFace).
    This runs on your CPU and avoids Google API rate limits.
    """
    # Changed: Using a free, high-performance local model
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
    return vectorstore


def get_conversation_chain(vectorstore):
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.3)

    memory = ConversationBufferMemory(
        memory_key='chat_history',
        return_messages=True
    )

    # Create a custom prompt that forces LaTeX formatting
    template = """
    You are a helpful AI assistant.
    Answer the user's question based ONLY on the context provided below.
    
    IMPORTANT FORMATTING INSTRUCTIONS:
    1. If the answer contains math formulas, YOU MUST format them using LaTeX.
    2. Enclose inline math in single dollar signs, e.g., $E=mc^2$.
    3. Enclose independent equations in double dollar signs, e.g., $$a^2 + b^2 = c^2$$.
    4. Do not use bold or code blocks for math. Use strictly LaTeX delimiters.

    Context: {context}

    Question: {question}
    """
    
    prompt = PromptTemplate(
        template=template,
        input_variables=["context", "question"]
    )

    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(search_kwargs={"k": 10}),
        memory=memory,
        combine_docs_chain_kwargs={"prompt": prompt}  # Inject the custom prompt here
    )
    return conversation_chain