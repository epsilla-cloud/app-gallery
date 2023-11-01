import streamlit as st
from docagent import DocAgent

agent = DocAgent()

st.title("💬 Document Agent")
if "messages" not in st.session_state:
  st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you about the documents?"}]


for msg in st.session_state.messages:
  st.chat_message(msg["role"]).write(msg["content"])

if question := st.chat_input():
  st.session_state.messages.append({"role": "user", "content": question})

  st.chat_message("user").write(question)

  msg = { 'role': 'assistant', 'content': agent.solve(question) }
  st.session_state.messages.append(msg)
  st.chat_message("assistant").write(msg['content'])
