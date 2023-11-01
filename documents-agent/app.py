import streamlit as st
from docagent import DocAgent

agent = DocAgent()
all_docus = agent.list_docs()

st.title("💬 Document Agent")
if "messages" not in st.session_state:
  st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you about the documents?"}]


for msg in st.session_state.messages:
  st.chat_message(msg["role"]).write(msg["content"])

if question := st.chat_input():
  st.session_state.messages.append({"role": "user", "content": question})

  st.chat_message("user").write(question)

  # if agent.can_loop(question):
    # Loop through each document
  questions = agent.rephrase(question)
  concated = ''
  for file in all_docus:
    for retry in range(5):
      try:
        print('Processing ' + file)
        result = file + ": " + agent.solve_one(file, question, questions)
        concated += result + '\n\n\n'
        msg = { 'role': 'assistant', 'content': result }
        st.session_state.messages.append(msg)
        st.chat_message("assistant").write(msg['content'])
        break
      except Exception as e:
        print('Retrying ' + file)
        pass
  # Compose final summary result
  print('Final result')
  msg = { 'role': 'assistant', 'content': 'Final Answer: ' + agent.summary(question, concated) }
  st.session_state.messages.append(msg)
  st.chat_message("assistant").write(msg['content'])
  # else:
  #   prompt = f'''You are an agent to help answering questions from a large set of documents.
  #   Pay attention to the document title and relevant content from search to answer the question.

  #   Question: {question}
  #   '''

  #   msg = { 'role': 'assistant', 'content': agent.solve(prompt) }
  #   st.session_state.messages.append(msg)
  #   st.chat_message("assistant").write(msg['content'])
