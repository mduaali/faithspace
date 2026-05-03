# 🔮 FaithSpace
<img width="1680" height="959" alt="Screenshot 2026-05-03 at 7 05 51 PM" src="https://github.com/user-attachments/assets/4d17227d-1110-4b3c-ac00-facb5d413ba7" />
<img width="1680" height="961" alt="Screenshot 2026-05-03 at 7 06 14 PM" src="https://github.com/user-attachments/assets/c56cc51b-3506-4b32-b62d-1dcc5c1ec57c" />
<img width="1680" height="962" alt="Screenshot 2026-05-03 at 7 07 13 PM" src="https://github.com/user-attachments/assets/974c025e-6ed7-401f-851f-3037081aebbe" />
<img width="1680" height="960" alt="Screenshot 2026-05-03 at 7 07 40 PM" src="https://github.com/user-attachments/assets/5372b4f8-d6ea-4efb-8de7-12386440bd30" />

**"many paths, one shared light."**

FaithSpace is an immersive spiritual companion designed to bridge the gap between traditions. In a world that often feels divided, this platform offers a dreamy, safe space to explore wisdom through the lenses of **Islam, Christianity, Buddhism, and Hinduism.** 

Whether you are seeking guidance on love, struggling with doubt, or simply looking for a moment of peace, FaithSpace uses advanced AI to reflect the shared beauty of human faith.

---

## ✨ The Vision
FaithSpace was created to remind us that while our rituals may differ, our search for the divine often leads to the same truths. It is a tool for **peace, understanding, and interfaith harmony.**

## 🚀 Key Features
*   **Spiritual Pathfinding:** Select a specific tradition to receive guidance rooted in that faith’s sacred texts.
*   **Interfaith Reflections:** Use the "Hear Other Paths" feature to see how multiple religions answer the same heart-centered questions.
*   **RAG-Powered Wisdom:** Grounded in a vector database (ChromaDB) containing curated spiritual teachings to ensure authentic responses.
*   **Aesthetic Immersion:** A minimalist, "dreamy" UI designed to lower stress and encourage reflection.

## 🛠️ Technical Stack
*   **Language:** Python 3.10+
*   **Framework:** Streamlit
*   **AI Engine:** Google Gemini 3 Flash (2026 `google-genai` SDK)
*   **Vector DB:** ChromaDB (for Retrieval-Augmented Generation)
*   **Embeddings:** `all-miniLM-L6-v2` via Sentence-Transformers

## 📖 How to Run Locally

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/mduaali/faithspace.git](https://github.com/mduaali/faithspace.git)
   cd faithspace
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   
```

3. **Set up your Secrets:**
   Create a folder named `.streamlit` and a file inside called `secrets.toml`. Add your key:
   ```toml
   GEMINI_API_KEY = "your_google_api_key_here"
   ```

4. **Launch:**
   ```bash
   streamlit run app.py
   ```

## 🕊️ Note on Performance
FaithSpace is a deep-thinking application. Because it connects to high-fidelity AI models and scans multiple sacred databases at once, responses might occasionally be a little laggy. Quality wisdom takes time to gather—thank you for your patience.

---

### 🎓 Academic Context
Developed as a capstone project at **Florida State University (2026)**. This project explores the intersection of Communication, Media Studies, and Artificial Intelligence to foster global empathy.

**God is great, and we are never truly apart in our search for Him. 🤍**
```

### 💡 Pro-Tip
Since you are on your MacBook Pro, once you save this file, remember to do one last push so it shows up on GitHub:

```bash
git add README.md
git commit -m "Add eye-catching description and readme"
git push
```
