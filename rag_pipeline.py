import ollama
from retriever import retrieve_context
import os



    
def load_structured_draft(file_path):
    """
    Loads a structured protocol draft from a text file.
    """
    with open(file_path, 'r') as f:
        return f.read()

def generate_b2scala_code(draft, context):
    """
    Uses the local Ollama LLM to generate B2Scala code based on the draft and retrieved context.
    """
    prompt = f"""
            You are a code generation assistant specialized in translating structured protocol drafts into valid B2Scala code.
            Use the following retrieved examples and the draft to produce a B2Scala implementation. Provide only the source code file contents
            and include a short header comment with the draft title and which KB examples were used.

            --- DRAFT ---
            {draft}

            --- RETRIEVED EXAMPLES (short summaries) ---
            {context}

            --- INSTRUCTIONS ---
            - Generate valid B2Scala code using the Bach primitives (tell, get, ask, nask, etc).
            - Keep code concise, with comments showing message flow.
            - If some draft assumptions are missing, keep TODO comments.
            - Output only the Scala code (no extra explanation).
            """
    
    print("Sending prompt to local LLM for code generation...")
    try:
        response = ollama.chat(
            model='llama3.1',  # Or the model you installed (e.g., 'llama3')
            messages=[{'role': 'user', 'content': prompt}]
        )
        return response['message']['content']
    except Exception as e:
        return f"An error occurred with the LLM: {e}"

if __name__ == "__main__":
    draft_file = "structured_draft.txt"
    output_file = os.path.join("Generated", "generated_code.scala")

    if not os.path.exists(draft_file):
        print(f"Error: Draft file '{draft_file}' not found. Please create one.")
    else:
        # Load the structured draft
        protocol_draft = load_structured_draft(draft_file)

        # Retrieve relevant context from the knowledge base
        retrieved_context = retrieve_context(protocol_draft)
        
        # Generate the code
        generated_code = generate_b2scala_code(protocol_draft, "\n\n".join(retrieved_context))
        
        # Save the generated code
        os.makedirs("Generated", exist_ok=True)
        with open(output_file, "w") as f:
            f.write(generated_code)
        
        print("\n--- Generated B2Scala Code ---")
        print(generated_code)
        print(f"\nCode saved to {output_file}")




