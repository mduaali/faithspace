import json
import os
import chromadb
from chromadb.utils import embedding_functions

# --- STEP 1: LOAD RAW FILES ---
def load_book(file_path, use_sig=False):
    encoding = 'utf-8-sig' if use_sig else 'utf-8'
    with open(file_path, 'r', encoding=encoding) as f:
        return json.load(f)

base_path = "data/books"

print("Loading raw JSON files...")
quran_raw = load_book(os.path.join(base_path, "quran_en.json"))
bible_raw = load_book(os.path.join(base_path, "BBE.json"))
hindu_raw = load_book(os.path.join(base_path, "translation.json"), use_sig=True)
buddha_raw = load_book(os.path.join(base_path, "dhammapada.json"))

# --- STEP 2: EXTRACT AND NORMALIZE ---
all_documents = []

# 1. Islam
for surah in quran_raw:
    for v in surah['verses']:
        all_documents.append({
            "text": v['translation'], 
            "metadata": {"religion": "Islam", "source": "Quran", "chapter": surah['name']}
        })

# 2. Christianity
for book in bible_raw.get('books', []):
    for chapter_data in book.get('chapters', []):
        chapter_num = chapter_data.get('chapter')
        for v in chapter_data.get('verses', []):
            if v.get('text'):
                all_documents.append({
                    "text": v.get('text'), 
                    "metadata": {"religion": "Christianity", "source": "Bible", "book": book['name'], "chapter": chapter_num}
                })

# 3. Hinduism
for i, v in enumerate(hindu_raw):
    text = v.get('translation') or v.get('description') or v.get('text') if isinstance(v, dict) else str(v)
    if text:
        all_documents.append({
            "text": text, 
            "metadata": {"religion": "Hinduism", "source": "Bhagavad Gita", "verse_num": i+1}
        })

# --- 4. BUDDHISM (Dhammapada) ---
buddha_docs = []

# Logic for the 'pages' section (Intro)
for page in buddha_raw.get('pages', []):
    for paragraph in page.get('content', []):
        if len(paragraph) > 10:
            buddha_docs.append({
                "text": paragraph,
                "metadata": {"religion": "Buddhism", "source": "Dhammapada", "section": "Intro"}
            })

# Logic for the 'chapters' section (Verses)
for ch in buddha_raw.get('chapters', []):
    ch_title = ch.get('title', 'Unknown')
    for v in ch.get('verses', []):
        # We explicitly use 'verse' here based on your find_buddha.py results
        v_text = v.get('verse') 
        if v_text:
            buddha_docs.append({
                "text": v_text, 
                "metadata": {"religion": "Buddhism", "source": "Dhammapada", "chapter": ch_title}
            })

print(f"Added {len(buddha_docs)} Buddhist items.")
# --- IMPORTANT: ADD THE BUDDHIST DOCS TO THE MAIN LIST ---
all_documents.extend(buddha_docs)

print(f"✅ Total standard documents prepared: {len(all_documents)}")

# --- STEP 3: INITIALIZE CHROMADB ---
client = chromadb.PersistentClient(path="./faith_db")
emb_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

# Create (or clear) the collection
try:
    client.delete_collection("religious_texts")
except:
    pass
collection = client.create_collection(name="religious_texts", embedding_function=emb_fn)

# --- STEP 4: INDEX IN BATCHES ---
ids = [str(i) for i in range(len(all_documents))]
documents = [doc['text'] for doc in all_documents]
metadatas = [doc['metadata'] for doc in all_documents]

batch_size = 4000
print(f"Indexing {len(all_documents)} items in batches...")

for i in range(0, len(all_documents), batch_size):
    end_idx = i + batch_size
    collection.add(
        ids=ids[i:end_idx],
        documents=documents[i:end_idx],
        metadatas=metadatas[i:end_idx]
    )
    print(f"Uploaded batch {i} to {min(end_idx, len(all_documents))}")

print(f"✅ FINAL SUCCESS: Indexed {collection.count()} items.")