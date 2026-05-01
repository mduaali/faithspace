import chromadb
from chromadb.utils import embedding_functions

# 1. Connect to the existing database
client = chromadb.PersistentClient(path="./faith_db")
emb_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
collection = client.get_collection(name="religious_texts", embedding_function=emb_fn)

# 2. Ask a question
query_text = "I am feeling very lonely and forgotten"

# 3. Search for the top 2 closest verses from EACH religion
# We use a filter to show how powerful the metadata we saved is!
for religion in ["Islam", "Christianity", "Hinduism", "Buddhism"]:
    print(f"\n--- Wisdom from {religion} ---")
    results = collection.query(
        query_texts=[query_text],
        n_results=2,
        where={"religion": religion}
    )
    
    for i in range(len(results['documents'][0])):
        text = results['documents'][0][i]
        meta = results['metadatas'][0][i]
        print(f"[{meta.get('source')}]: {text}")