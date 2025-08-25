from retriever import Retriever
from langchain_community.llms import Ollama
import os
import sys

LLM_MODEL = "llama3.1"

class RAGPipeline:
    def __init__(self, k=5):
        self.retriever = Retriever(k=k)
        self.llm = Ollama(model=LLM_MODEL)
    
    def load_structured_draft(self, file_path):
        """
        Loads a structured protocol draft from a text file.
        Includes error handling for file operations.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            print(f"Error: Draft file '{file_path}' not found.", file=sys.stderr)
            return None
        except Exception as e:
            print(f"An unexpected error occurred while reading the file: {e}", file=sys.stderr)
            return None

    def generate_answer(self, draft):
        # Step 1: Retrieve context
        try:
            context_chunks = self.retriever.get_context(draft)
            context_text = "\n".join(context_chunks)
        except Exception as e:
            print(f"Error during context retrieval: {e}", file=sys.stderr)
            return None, []

        # Step 2: Build prompt
        prompt = f"""
        You are a code generation assistant specialized in translating structured protocol drafts into valid B2Scala code.
        Use the following retrieved examples and the draft to produce a B2Scala implementation. Provide only the source code file contents
        and include a short header comment with the draft title and which KB examples were used.

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
        print("🔹 Generating answer with LLM...")
        try:
            response = self.llm.invoke(prompt)
            return response, context_chunks
        except Exception as e:
            print(f"Error calling LLM: {e}", file=sys.stderr)
            return None, context_chunks

if __name__ == "__main__":
    draft_file = "structured_draft.txt"
    output_file = os.path.join("Generated", "generated_code.scala")
    rag = RAGPipeline(k=5)

    # Load the structured draft with error handling
    protocol_draft = rag.load_structured_draft(draft_file)
    if not protocol_draft:
        sys.exit(1)

    answer, context = rag.generate_answer(protocol_draft)

    # Check if a valid answer was returned before proceeding
    if answer is None:
        print("Code generation failed. Exiting.", file=sys.stderr)
        sys.exit(1)

    print("\n--- Retrieved Context ---")
    try:
        with open("context.txt", "w", encoding="utf-8") as file:
            for c in context:
                file.write(str(c) + "\n---\n")
    except Exception as e:
        print(f"Failed to write context file: {e}", file=sys.stderr)

    print("\n--- Generated Answer ---")
    try:
        os.makedirs("Generated", exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(answer)
        print("Code generation successful. Check the 'Generated' directory.")
    except Exception as e:
        print(f"Failed to write generated code file: {e}", file=sys.stderr)