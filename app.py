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
        You are an expert in protocol modeling and B2Scala.
        You have access to a Knowledge Base which contains canonical, working B2Scala examples.
        One canonical example in the Knowledge Base is the QUIC v1 handshake file that uses the exact
        package, imports, object structure, DATA / AGENTS / FORMULA & EXEC sections, and B2Scala primitives
        shown below. Use that example as the authoritative template and style guide.

        Your tasks (MANDATORY):
        1) Read the given protocol draft (variable `draft` below) and the Knowledge Base context (variable `context_text`).
        2) Summarize the draft internally (agents, messages, goals, assumptions) and then produce a single output:
        - Exactly one Scala source file, and nothing else (no extra prose).
        - The Scala file MUST follow the package, imports, object name, and structural layout shown in the canonical example.
        - All tokens, case classes, agents, messages and formulas MUST be adapted from the draft but preserve the canonical coding style.
        3) If any detail in the draft is missing, make reasonable assumptions and document them with inline // comments in the Scala file.
        4) Ensure the Scala file is self-contained (all needed case classes and Tokens declared) and is syntactically consistent with the canonical QUIC example from the Knowledge Base.
        5) Do NOT output anything outside the Scala file. The entire assistant response must be the file contents only.

        RESTRICTIONS (must obey):
        - Use **exactly** this package and imports header at the top of the file:
        package bscala.bsc_program

        import bscala.bsc_data._
        import bscala.bsc_agent._
        import bscala.bsc_runner._
        import bscala.bsc_settings._
        import bscala.bsc_formula._

        - Follow the canonical section headings and layout: DATA, AGENTS, FORMULA & EXEC as in the example.
        - Preserve naming style: Tokens named with quotes like Token("Name"), SI_Term case classes, Agent scripts using tell/get/ask composition, and final execution via new BSC_Runner_BHM().execute(Protocol, F).
        - Produce case classes for all structured terms you need (messages, crypto, envelopes, events, etc.).
        - All assumptions must be inline commented with // and briefly justified.
        - Output must be a compilable B2Scala program using core primitives only (no external libraries beyond the imports above).

        VERY IMPORTANT OUTPUT RULE:
        - The assistant MUST output a single Scala file only, using the object name `BSC_modelling_<ProtocolNameNoSpaces>` where <ProtocolNameNoSpaces> is derived from the draft title (remove spaces, punctuation).
        - Include a one-line doc comment right after the imports briefly describing the protocol.

        Input variables available:
        - draft: the protocol draft text (use to extract agents, messages, goals, assumptions).
        {draft}
        - context_text: Knowledge Base context (contains canonical B2Scala examples you MUST follow).
        {context_text}
        Now produce the Scala file ONLY, using the canonical QUIC example style from the Knowledge Base as the template and adapting tokens/messages/agents from the draft. Ensure all missing details are commented with // assumptions.
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
            output_file = os.path.join("Generated", "generated_code.scala")
            # Display the generated code
            st.code(answer, language="scala")
            try:
                os.makedirs("Generated", exist_ok=True)
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(answer)
                print("Code generation successful. Check the 'Generated' directory.")
            except Exception as e:
                print(f"Failed to write generated code file: {e}", file=sys.stderr)
        else:
            st.warning("Could not generate code. Please check your Ollama server and model.")
