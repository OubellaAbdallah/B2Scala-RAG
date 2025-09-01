import streamlit as st
import sys
import os
from retriever import Retriever
from langchain_community.llms import Ollama

# IMPORTANT: This is a placeholder for your RAGPipeline class.
# In a real app, you would import your actual RAGPipeline from its file.
# Since this is a self-contained example, we'll redefine a simplified version.
# To make this runnable, ensure your retriever.py file is in the same directory.

LLM_MODEL = "llama3.1"

class RAGPipeline:
    def __init__(self, k=3):
        try:
            # Assumes Retriever class and the required Ollama models are available
            self.retriever = Retriever(k=k)
            self.llm = Ollama(model=LLM_MODEL)
        except Exception as e:
            st.error(f"Error initializing RAGPipeline components: {e}")
            st.stop()

    def generate_answer(self, draft):
        # Step 1: Retrieve context
        try:
            context_chunks = self.retriever.get_context(draft)
            context_text = "\n".join(context_chunks)
        except Exception as e:
            st.error(f"Error during context retrieval: {e}")
            return None, []

        # Step 2: Build prompt
        prompt = f"""
        You are a code generation assistant specialized in translating structured protocol drafts into valid and full B2Scala code.
        Use the following retrieved examples and the draft to produce a B2Scala implementation. Provide only the source code file contents
        and include a short header comment with the draft title and which KB examples were used.
        The code should contain all necessary imports and be ready to compile. Do not use any undefined variables or methods.
        Do not add any extra syntax or imports that are not strictly necessary or they are not part of the B2Scala library.
        --- DRAFT ---
        {draft}

        --- RETRIEVED EXAMPLES (short summaries) ---
        {context_text}

        --- INSTRUCTIONS ---
        - Generate valid B2Scala code using the Bach primitives (tell, get, ask, nask, etc).
        - Keep code concise, with comments showing message flow.
        - If some draft assumptions are missing, keep TODO comments.
        - Output only the Scala code (no extra explanation).
        """

        # Step 3: Call LLM
        st.info("🔹 Generating answer with LLM...")
        try:
            response = self.llm.invoke(prompt)
            return response, context_chunks
        except Exception as e:
            st.error(f"Error calling LLM: {e}")
            return None, context_chunks

# --- Streamlit App ---

st.set_page_config(page_title="B2Scala Code Generator", page_icon="📝")

st.title("B2Scala Code Generator Chatbot")
st.caption("A RAG-powered assistant to formalize protocol drafts into B2Scala.")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("Enter your protocol draft here..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Instantiate the RAG pipeline
    rag_pipeline = RAGPipeline(k=5)

    # Get the code generation response
    with st.chat_message("assistant"):
        with st.spinner("Generating B2Scala code..."):
            answer, context = rag_pipeline.generate_answer(prompt)
        
        if answer:
            # Display the generated code
            st.code(answer, language="scala")
        else:
            st.warning("Could not generate code. Please check your Ollama server and model.")
