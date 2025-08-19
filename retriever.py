from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma

KB_DIR = "./kb"
COLLECTION_NAME = "b2scala_knowledge"
EMBEDDING_MODEL = "nomic-embed-text"

class Retriever:
    def __init__(self, k=5):
        print("🔹 Initializing embeddings...")
        embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)

        print("🔹 Loading ChromaDB knowledge base...")
        self.db = Chroma(
            persist_directory=KB_DIR,
            embedding_function=embeddings,
            collection_name=COLLECTION_NAME
        )
        self.k = k

    def get_context(self, query):
        print(f"🔹 Retrieving top {self.k} documents...")
        retrieved_docs = self.db.similarity_search(query, k=self.k)
        return [doc.page_content for doc in retrieved_docs]

if __name__ == "__main__":
    retriever = Retriever(k=3)
    query = "Define an agent named Alice that uses the primitives tell and get."
    context = retriever.get_context(query)
    print("\n--- Retrieved Context ---")
    for c in context:
        print(c)
        print("---")
