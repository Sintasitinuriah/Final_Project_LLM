import os
import json
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import LLMChain
from langchain.prompts import ChatPromptTemplate
from langchain.memory import ConversationBufferMemory
from dotenv import load_dotenv

# --- Page Config ---
st.set_page_config(page_title="🎓 Chatbot Kampus A")

# --- Load API key dari .env ---
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

# --- Sidebar ---
with st.sidebar:
    st.title("⚙️ Pengaturan Chatbot")
    
    # Pilih model
    selected_model = st.selectbox(
        "Pilih Model Gemini",
        ["gemini-2.0-flash", "gemini-2.5-flash", "gemini-2.5-pro"],
        index=1
    )

    # Atur parameter
    temperature = st.slider("Temperature", 0.0, 1.0, 0.2, step=0.1)
    max_output_tokens = st.slider("Max Output Tokens", 128, 2048, 512, step=64)

    # Tombol clear chat
    def clear_chat_history():
        st.session_state.messages = []
        st.session_state.memory = ConversationBufferMemory(return_messages=True)
    st.button("🗑️ Hapus Riwayat Chat", on_click=clear_chat_history)

# --- Load Knowledge Base dari JSON ---
with open("knowledge.json", "r", encoding="utf-8") as f:
    kampus_info = json.load(f)

def get_kampus_info(question: str) -> str | None:
    q = question.lower()
    
    if "jurusan" in q or "prodi" in q:
        return f"{kampus_info['nama']} memiliki jurusan: {', '.join(kampus_info['jurusan'])}."
    if "biaya semester" in q or "spp" in q:
        return f"Biaya semester di {kampus_info['nama']} adalah Rp {kampus_info['biaya']['semester']:,}."
    if "biaya pmb" in q or "pendaftaran" in q:
        return f"Biaya PMB (Penerimaan Mahasiswa Baru) adalah Rp {kampus_info['biaya']['pmb']:,}."
    if "fasilitas" in q:
        return f"Fasilitas di {kampus_info['nama']}: {', '.join(kampus_info['fasilitas'])}."
    if "beasiswa" in q:
        return f"Tersedia program beasiswa: {', '.join(kampus_info['beasiswa'])}."
    if "kurikulum" in q or "mata kuliah" in q or "pelajari" in q:
        if "industri" in q:
            return f"Kurikulum Teknik Industri: {', '.join(kampus_info['jurusan']['industri']['kurikulum'])}."
        elif "informatika" in q:
            return f"Kurikulum Teknik Informatika: {', '.join(kampus_info['jurusan']['informatika']['kurikulum'])}."
        else:
            return f"Kurikulum tersedia untuk: {', '.join(kampus_info['jurusan'].keys())}. Sebutkan jurusan yang ingin diketahui."
    if "alamat" in q or "kontak" in q:
        k = kampus_info['kontak']
        return f"Kontak {kampus_info['nama']}: {k['alamat']}, Telp {k['telepon']}, Email {k['email']}."
    return None

# --- Setup LLM ---
llm = ChatGoogleGenerativeAI(
    model=selected_model,
    google_api_key=api_key,
    temperature=temperature,
    max_output_tokens=max_output_tokens
)

# --- Memory ---
if "memory" not in st.session_state:
    st.session_state.memory = ConversationBufferMemory(return_messages=True)

# --- Prompt Template ---
prompt = ChatPromptTemplate.from_template("""
Anda adalah asisten virtual kampus.
Fokus Anda: layanan kampus (akademik, administrasi, beasiswa, fasilitas).
❌ Jika pertanyaan tidak ada hubungannya dengan kampus, jawab:
"Maaf, saya hanya bisa membantu terkait layanan kampus."

Riwayat percakapan:
{history}

Mahasiswa: {input}
Asisten:
""")

conversation = LLMChain(
    llm=llm,
    prompt=prompt,
    memory=st.session_state.memory,
    verbose=False
)

# --- UI Utama ---
st.title("🎓 Chatbot InfoAja ")
st.write("Halo! Saya asisten virtual kampus. Silakan tanyakan seputar akademik, administrasi, biaya, kurikulum, atau fasilitas kampus.")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Input user
user_input = st.chat_input("Tanya seputar layanan kampus...")

if user_input:
    # Coba jawab dari knowledge base
    kb_answer = get_kampus_info(user_input)
    if kb_answer:
        response = kb_answer
    else:
        response = conversation.run({"input": user_input})
    
    st.session_state.messages.append(("You", user_input))
    st.session_state.messages.append(("Bot", response))

# Tampilkan percakapan
for role, msg in st.session_state.messages:
    if role == "You":
        st.markdown(f"**🧑‍🎓 {role}:** {msg}")
    else:
        st.markdown(f"**🤖 {role}:** {msg}")
