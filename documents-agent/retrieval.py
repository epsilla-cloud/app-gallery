import os, openai, json
from dotenv import load_dotenv
from pyepsilla import cloud
from typing import Any

load_dotenv()

class Retrieval:
  openai.api_key = os.getenv("OPENAI_KEY")
  if openai.api_key is None:
    raise ValueError("No OpenAI API key found. Please set it as an environment variable.")

  def rephrase(self, question: str) -> list[str]:
    messages = [
      {"role": "system", "content": "You are a helpful assistant that generates multiple search queries based on a single input query."},
      {"role": "user", "content": f"Rephrase the following question into 3 distinct alternatives to enhance information retrieval recall. Each rephrased question should be no longer than 3 times the original length: {question}"},
      {"role": "user", "content": "OUTPUT (3 questions):"}
    ]
    functions = [
      {
        "name": "get_question_list",
        "description": "Get 3 alternative questions.",
        "parameters": {
          "type": "object",
          "properties": {
            "questions": {
              "type": "array",
              "description": "The alternative questions",
              "items": {
                 "type": "string"
              }
            }
          },
          "required": ["questions"],
        },
      }
    ]

    rephrase_questions = openai.ChatCompletion.create(
      model="gpt-3.5-turbo-0613",
      messages=messages,
      functions=functions,
      function_call="auto"
    )

    result = json.loads(rephrase_questions.choices[0].message.function_call.arguments)
    return result["questions"]

  def vector_search(self, db: Any, question: str):
    result = openai.Embedding.create(
      input=question,
      model="text-embedding-ada-002"
    )

    query_vector = result["data"][0]["embedding"]
    status_code, response = db.query(table_name=os.getenv("TABLE_NAME"),
      query_field="embedding",
      query_vector=query_vector,
      limit=20,
      response_fields=["id", "doctitle", "context"],
      with_distance=True
    )
    if status_code != 200:
      raise Exception(response["message"])

    return response["result"]

  def ranking_fusion(self, original_query: str, query_score_dict: dict, limit = 5):
    if limit > 20:
      limit = 20

    fused_ranking = {}
    for query, doc_items in query_score_dict.items():
      for ranking, doc_item in enumerate(doc_items):
        doc_id = doc_item["id"]

        if doc_id not in fused_ranking:
          fused_ranking[doc_id] = {
            "score": 0,
            "count": 0,
            "item": doc_item
          }

        fused_ranking[doc_id]["count"] += 1

        if query == original_query:
          weight = 0.4
        else:
          weight = 0.2
        if doc_item["@distance"] < -1 or doc_item["@distance"] > 1:
          fused_ranking[doc_id]["score"] += 10 * weight
        else:
          fused_ranking[doc_id]["score"] += ranking * weight

    for doc_id, ranking_info in fused_ranking.items():
      if ranking_info["count"] < 4:
        cur_count = ranking_info["count"]
        ranking_info["score"] += (4 - cur_count) * 6 * 0.2

    # print(fused_ranking)
    result = []
    sorted_ranking = sorted(fused_ranking.items(), key=lambda item: item[1]["score"])
    for i in range(limit):
      result.append(sorted_ranking[i][1]["item"])

    return result

  def generate_content_based_on_ranking(self, ranking_result: dict) -> str:
    context_dict = {}
    for item in ranking_result:
      doc_title = item["doctitle"]
      if doc_title not in context_dict:
        context_dict[doc_title] = item["context"]
      else:
        context_dict[doc_title] += " " + item["context"]

    total = len(context_dict)
    content = ""
    for index, (title, context) in enumerate(context_dict.items()):
      content += "Title of the document: " + title + "\n"
      content += "Relevant document content: \n" + context
      if index < total - 1:
        content += "\n\n"

    return content

# Main function
if __name__ == "__main__":
    retrieval = Retrieval()
    question = "Find contracts that mention limitations of liability"

    qs = retrieval.rephrase(question=question)
    print(qs)

    client = cloud.Client(
      project_id=os.getenv("PROJECT_ID"),
      api_key=os.getenv("EPSILLA_API_KEY")
    )
    db = client.vectordb(db_id=os.getenv("DB_ID"))

    query_score_dict = {}
    item = retrieval.vector_search(db, question)
    # print(item)
    query_score_dict[question] = item
    for q in qs:
      item = retrieval.vector_search(db, q)
      query_score_dict[q] = item
    # print(query_score_dict)

    ranking_result = retrieval.ranking_fusion(original_query=question, query_score_dict=query_score_dict)
    final_result = retrieval.generate_content_based_on_ranking(ranking_result)
    # print(final_result)

