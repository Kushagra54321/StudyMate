# backend/vector_store.py

import importlib
from pathlib import Path

try:
    chromadb = importlib.import_module("chromadb")
except ImportError as exc:
    raise ImportError(
        "ChromaDB is required. Install it with: pip install chromadb"
    ) from exc
try:
    SentenceTransformer = importlib.import_module(
        "sentence_transformers"
    ).SentenceTransformer
except ImportError as exc:
    raise ImportError(
        "sentence-transformers is required. Install it with: "
        "pip install sentence-transformers"
    ) from exc
try:
    # Import dynamically so this module works both as part of the backend
    # package and when executed directly from the backend directory.
    if __package__:
        extract_text_from_pdf = importlib.import_module(
            f"{__package__}.pdf_reader"
        ).extract_text_from_pdf
        create_chunks = importlib.import_module(
            f"{__package__}.chunker"
        ).create_chunks
    else:
        extract_text_from_pdf = importlib.import_module(
            "pdf_reader"
        ).extract_text_from_pdf
        create_chunks = importlib.import_module("chunker").create_chunks
except ImportError:
    # Support running this file directly from the backend directory.
    extract_text_from_pdf = importlib.import_module(
        "pdf_reader"
    ).extract_text_from_pdf
    create_chunks = importlib.import_module("chunker").create_chunks

# =========================================================
# STEP 6: Embedding Model Load Karna
# =========================================================
# Ye model text ko 384-dimensional vector (numbers) mein convert karta hai
print("Loading Embedding Model...")
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")


# =========================================================
# STEP 7: ChromaDB Persistent Database Setup
# =========================================================
# Local folder '../vectorstore' mein ChromaDB save/load hoga
client = chromadb.PersistentClient(
    path=str(Path(__file__).resolve().parent.parent / "vectorstore")
)

# 'studymate' naam ka collection get karo ya naya banao
collection = client.get_or_create_collection(name="studymate")


# =========================================================
# STEP 8: Chunks ke Embeddings Banakar Vector DB Mein Save Karna
# =========================================================
def store_chunks_in_db(chunks):
    """
    create_chunks() se mile chunks ke embeddings banata hai 
    aur unhe ChromaDB vector database mein add karta hai.
    """
    for index, chunk in enumerate(chunks):
        # Text ka embedding vector banao
        vector = embedding_model.encode(chunk["text"]).tolist()
        
        # Unique Chunk ID handle karein
        chunk_id = chunk.get("chunk_id", f"chunk_{index}")
        
        # ChromaDB mein store karo
        collection.add(
            ids=[chunk_id],
            embeddings=[vector],
            documents=[chunk["text"]],
            metadatas=[{"page": chunk.get("page_number", chunk.get("page", 1))}]
        )
    
    print(f"✅ Successfully stored {len(chunks)} chunks in ChromaDB!")


# =========================================================
# STEP 9: Semantic Similarity Search (Question Search)
# =========================================================
def search_similar_chunks(query_text, top_k=3):
    """
    User ke question ko vector mein convert karke 
    ChromaDB se sabse relevant top_k chunks dhoondhta hai.
    """
    # 1. Question ka embedding vector banao
    query_vector = embedding_model.encode(query_text).tolist()

    # 2. ChromaDB mein similarity search run karo
    results = collection.query(
        query_embeddings=[query_vector],
        n_results=top_k
    )

    # 3. Matching chunks aur unke metadata extract karke return karo
    retrieved_chunks = []
    
    if results and results.get("documents") and len(results["documents"]) > 0:
        documents = results["documents"][0]
        metadatas = results["metadatas"][0]
        distances = results.get("distances", [[]])[0]

        for doc, meta, dist in zip(documents, metadatas, distances):
            retrieved_chunks.append({
                "text": doc,
                "page": meta.get("page"),
                "score": dist
            })

    return retrieved_chunks


# =========================================================
# Execution & Testing Flow
# =========================================================
if __name__ == "__main__":
    pdf_path = Path(__file__).resolve().parent.parent / "data" / "sample.pdf"
    
    print("\n--- Phase 1: PDF Read & Chunking ---")
    pages = extract_text_from_pdf(pdf_path)
    chunks = create_chunks(pages, chunk_size=500, overlap=100)
    print(f"Total chunks created: {len(chunks)}")
    
    print("\n--- Phase 2: Storing in ChromaDB ---")
    store_chunks_in_db(chunks)
    
    print("\n--- Phase 3: Testing Step 9 Search ---")
    test_question = "What is deadlock?"
    print(f"Searching for: '{test_question}'\n")
    
    search_results = search_similar_chunks(test_question, top_k=3)
    
    for idx, res in enumerate(search_results, 1):
        print(f"Result {idx} | Page {res['page']} | Distance Score: {res['score']:.4f}")
        print(f"Text: {res['text']}")
        print("-" * 60)