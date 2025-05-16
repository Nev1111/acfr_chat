import streamlit as st
import pickle
import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
openai_key = os.getenv("OPENAI_API_KEY")

if not openai_key:
    st.error("OPENAI_API_KEY not found in .env file.")
    st.stop()

# Initialize OpenAI client
client = OpenAI(api_key=openai_key)

# Page setup
st.set_page_config(page_title="ACFR Chat", layout="wide")
st.title("📘 ACFR Chat")
st.caption("Ask questions about the TRS NYC Annual Comprehensive Financial Report (2024)")

# Load ACFR chunks
with open("trs_acfr2024_chunks.pkl", "rb") as f:
    chunks = pickle.load(f)

# Session state to manage user input reset
if "question" not in st.session_state:
    st.session_state.question = ""

if st.button("🆕 New Question"):
    for key in ["question", "answer", "context_chunks"]:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()


# Input box (preserves state)
st.session_state.question = st.text_input("Enter your question below:", value=st.session_state.question, placeholder="e.g., What are the 2024 pension returns?")

# GPT call function
@st.cache_data(show_spinner=False)
def ask_gpt(prompt):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant for financial reporting. Answer only using the provided context."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.2,
        max_tokens=1000
    )
    return response.choices[0].message.content

# Run if a question is asked
question = st.session_state.question
if question:
    # Score chunks
    scored = []
    for chunk in chunks:
        score = sum(1 for word in question.lower().split() if word in chunk["content"].lower())
        if score > 0:
            scored.append((score, chunk))

    top_chunks = [c for _, c in sorted(scored, key=lambda x: x[0], reverse=True)[:2]]
    context = "\n\n".join([f"(Page {c['page']}) {c['content']}" for c in top_chunks])

    prompt = f"""You are answering questions about a public pension fund's Annual Comprehensive Financial Report (ACFR).
Use only the context provided below. Be precise and helpful.

Context:
{context}

Question: {question}
Answer:"""

    answer = ask_gpt(prompt)

    st.subheader("📎 Answer")
    st.write(answer)

    with st.expander("🔍 Show reference context"):
        for c in top_chunks:
            st.markdown(f"**Page {c['page']}**")
            st.write(c["content"])
