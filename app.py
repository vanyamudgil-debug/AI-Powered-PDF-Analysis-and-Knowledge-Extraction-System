import streamlit as st
from rag_engine import get_pdf_text, get_text_chunks, get_vectorstore, get_conversation_chain
import os

# Page Configuration
st.set_page_config(page_title="AI-Powered PDF Analysis and Knowledge Extraction System", page_icon="📚")

# CSS for better chat layout
st.markdown("""
<style>
.chat-message {
    padding: 1.5rem; border-radius: 0.5rem; margin-bottom: 1rem; display: flex
}
.chat-message.user {
    background-color: #2b313e
}
.chat-message.bot {
    background-color: #475063
}
.chat-message .avatar {
  width: 15%;
}
.chat-message .message {
  width: 85%;
  padding: 0 1.5rem;
  color: #fff;
}
</style>
""", unsafe_allow_html=True)

def handle_userinput(user_question):
    if st.session_state.conversation is None:
        st.warning("Please upload PDFs and click 'Process' first!")
        return

    # Get response from the chain
    response = st.session_state.conversation({'question': user_question})
    st.session_state.chat_history = response['chat_history']

    # Display chat history using native Streamlit chat elements
    # This automatically handles LaTeX ($...$) rendering
    for message in st.session_state.chat_history:
        if message.type == 'human':
            with st.chat_message("user"):
                st.markdown(message.content)
        else:
            with st.chat_message("assistant"):
                st.markdown(message.content)

def main():
    st.header("AI-Powered PDF Analysis and Knowledge Extraction System 📚")

    # Initialize Session State variables
    if "conversation" not in st.session_state:
        st.session_state.conversation = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = None

    # --- Sidebar ---
    with st.sidebar:
        st.subheader("Your Documents")
        
        # File Uploader
        pdf_docs = st.file_uploader(
            "Upload your PDFs here and click on 'Process'", 
            accept_multiple_files=True, 
            type="pdf"
        )
        
        # Process Button
        if st.button("Process Documents"):
            if not pdf_docs:
                st.error("Please upload at least one PDF file.")
            else:
                with st.spinner("Processing... This may take a moment."):
                    # 1. Get PDF Text
                    raw_text = get_pdf_text(pdf_docs)
                    
                    # 2. Get Text Chunks
                    text_chunks = get_text_chunks(raw_text)
                    
                    # 3. Create Vector Store
                    vectorstore = get_vectorstore(text_chunks)
                    
                    # 4. Create Conversation Chain
                    st.session_state.conversation = get_conversation_chain(vectorstore)
                    
                    st.success("Done! You can now chat with your documents.")
        
        st.markdown("---")
        st.write("### How to Remove Files?")
        st.info("Simply click the 'X' next to the file name in the uploader above, then click 'Process Documents' again to rebuild the knowledge base.")

    # --- Main Chat Interface ---
    user_question = st.chat_input("Ask a question about your documents...")
    if user_question:
        handle_userinput(user_question)

if __name__ == '__main__':
    main()