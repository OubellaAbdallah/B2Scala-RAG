from retriever import Retriever
from langchain_community.llms import Ollama

LLM_MODEL = "llama3.1"

class RAGPipeline:
    def __init__(self, k=5):
        self.retriever = Retriever(k=k)
        self.llm = Ollama(model=LLM_MODEL)

    def generate_answer(self, query):
        # Step 1: Retrieve context
        context_chunks = self.retriever.get_context(query)
        context_text = "\n".join(context_chunks)

        # Step 2: Build prompt
        prompt = f"""
You are an assistant specialized in B2Scala code generation.

Context from documents:
{context_text}

Query:
{query}

Answer in a clear, structured way. If Scala code is required, provide clean and runnable code.
"""

        # Step 3: Call LLM
        print("🔹 Generating answer with LLM...")
        response = self.llm.invoke(prompt)
        return response, context_chunks

if __name__ == "__main__":
    rag = RAGPipeline(k=5)
    query = "Define an agent named Alice that uses the primitives tell and get."
    answer, context = rag.generate_answer(query)

    print("\n--- Retrieved Context ---")
    for c in context:
        print(c)
        print("---")

    print("\n--- Generated Answer ---")
    print(answer)
