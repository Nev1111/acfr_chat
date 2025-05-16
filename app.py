import streamlit as st
import pickle
import os
from openai import OpenAI
from dotenv import load_dotenv

# Load API key
load_dotenv()
openai_key = os.getenv("OPENAI_API_KEY")
if not openai_key:
    st.error("OPENAI_API_KEY not found.")
    st.stop()

client = OpenAI(api_key=openai_key)

# Streamlit config
st.set_page_config(page_title="ACFR Chat", layout="wide")
st.title("📘 ACFR Chat")
st.caption("Chat with the TRS NYC ACFR 2024 — just like ChatGPT.")

# Load ACFR chunks
with open("trs_acfr2024_chunks.pkl", "rb") as f:
    chunks = pickle.load(f)

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# GPT function
def ask_gpt(prompt):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant for financial reporting. Use only the context provided."
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

# Show chat history
for i, turn in enumerate(st.session_state.chat_history):
    with st.chat_message("user"):
        st.markdown(turn["question"])
    with st.chat_message("assistant"):
        st.markdown(turn["answer"])

# Input box with streaming behavior
if prompt := st.chat_input("Type your question here..."):
    # Match chunks
    scored = []
    for chunk in chunks:
        score = sum(1 for word in prompt.lower().split() if word in chunk["content"].lower())
        if score > 0:
            scored.append((score, chunk))

    top_chunks = [c for _, c in sorted(scored, key=lambda x: x[0], reverse=True)[:2]]
    context = "\n\n".join([f"(Page {c['page']}) {c['content']}" for c in top_chunks])

    full_prompt = f"""You are answering questions about a public pension fund's Annual Comprehensive Financial Report (ACFR).
Use only the context provided below. Be precise and helpful.

Context:
{context}

Question: {prompt}
Answer:"""

    # Show user message instantly
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get model reply
    response = ask_gpt(full_prompt)

    # Show model reply
    with st.chat_message("assistant"):
        st.markdown(response)

    # Add to history
    st.session_state.chat_history.append({
        "question": prompt,
        "answer": response,
        "context": top_chunks
    })
