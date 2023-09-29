from langchain.vectorstores import Epsilla
from pyepsilla import vectordb
from sentence_transformers import SentenceTransformer
import streamlit as st

import subprocess
from typing import List

model = SentenceTransformer('all-MiniLM-L6-v2')

class LocalEmbeddings():
  def embed_query(self, text: str) -> List[float]:
    return model.encode(text).tolist()

embeddings = LocalEmbeddings()

client = vectordb.Client()
vector_store = Epsilla(
  client,
  embeddings,
  db_path="/tmp/localchatdb",
  db_name="LocalChatDB"
)
vector_store.use_collection("LocalChatCollection")

st.title("💬 Chatbot")
if "messages" not in st.session_state:
  st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]


for msg in st.session_state.messages:
  st.chat_message(msg["role"]).write(msg["content"])

if question := st.chat_input():
  st.session_state.messages.append({"role": "user", "content": question})

  context = '\n'.join(map(lambda doc: doc.page_content, vector_store.similarity_search(question, k = 5)))

  st.chat_message("user").write(question)
  prompt = f'''
    Answer the Question based on the given Context. Try to understand the Context and rephrase them.
    Please don't make things up or say things not mentioned in the Context. Ask for more information when needed.

    Context:
    {context}

    Question:
    {question}

    Answer:
    '''
  print(prompt)

  command = ['llm', '-m', 'llama-2-7b-chat', prompt]
  process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
  content = ''
  while True:
    output = process.stdout.readline()
    if output:
      content = content + output
    return_code = process.poll()
    if return_code is not None:
      break

  msg = { 'role': 'assistant', 'content': content }
  st.session_state.messages.append(msg)
  st.chat_message("assistant").write(msg['content'])
