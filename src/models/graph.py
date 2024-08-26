from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
import chromadb

# TODO: add llm guardrails

load_dotenv()

class UserModel(BaseModel):
    name: str = Field(description="Name of the user")
    about_user: str = Field(description="Biodata about the user that may be relevant")
    query : str = Field(description="What is the user's desired area of interest, niche area(s), and wishes for courses")

llm = ChatGroq(model='llama3-groq-70b-8192-tool-use-preview')

structured_llm = llm.with_structured_output(UserModel)


name, about_user, query = structured_llm.invoke(input("User: "))

class SearchQueries(BaseModel):
    queries : list[str] = Field(description="Search queries for a Vector Database contain course descriptions")

prompt_template = PromptTemplate.from_template(
    "Give me 5-10 search queries for a Vector Database containing course descriptions \
    for the following user query: {query} \
    \
    DO NOT USE the word 'courses', or any adjectives/adverbs. Adjust the queries to ensure relevance and precision."
)



queries = llm.with_structured_output(SearchQueries).invoke(prompt_template.format(query=query)).queries

chroma_client = chromadb.PersistentClient('database')

ollama_ef = chromadb.utils.embedding_functions.OllamaEmbeddingFunction(
    url="http://localhost:11434/api/embeddings",
    model_name="nomic-embed-text",
)


collection = chroma_client.get_or_create_collection(name="tamu_courses_collection", embedding_function=ollama_ef)

results = collection.query(
    query_texts=queries,
    n_results=5, # 3-5 is a good tradeoff
    where={"Department":"CSCE"}
)

recommendations = {}

for ids, distances in zip(results['ids'], results['distances']):
    for id, distance in zip(ids, distances):
        if id in recommendations:
            recommendations[id].append(distance)
        else:
            recommendations[id] = [distance]
    #recommendations += result
# Create a copy of the keys to iterate over
for course in list(recommendations.keys()):
    if len(recommendations[course]) < len(queries)/2:
        del recommendations[course]
    else:
        recommendations[course] = sum(recommendations[course]) / len(recommendations[course])


recommendations = dict(sorted(recommendations.items(), key=lambda item: item[1]))

print(recommendations)
