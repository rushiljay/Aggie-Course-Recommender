from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
import chromadb

# TODO: add llm guardrails

load_dotenv()

user_request = input("User: ")

while user_request != "END":

    class PromptGuardrail(BaseModel):
        allowed: bool = Field(
            default=True,
            description="Determines if the user query aligns with the bot’s primary functions of providing academic advising and course recommendations. Queries directly related to academic courses, program selection, academic policies, and study strategies are set to True. Queries unrelated to academic advising, such as personal advice, entertainment, general knowledge, or any other non-educational topics, are automatically set to False to ensure the bot maintains its specialized focus."
        )




    class UserModel(BaseModel): # whatever one must know to advise someone
        name: str = Field(description="Name of the user")
        about_user: str = Field(description="Biodata about the user that may be relevant")
        queries : list[str] = Field(description="What is the user's desired areas of interest(s), niche area(s), and wishes for courses. Avoid being broad. Avoid using the word 'courses', adjectives, adverbs, or generic terms. Ensure the queries are specific and contextually relevant. DO NOT GENERATE NEW INFORMATION. DO NOT HALLUCINATE")

    llm = ChatGroq(model='llama3-groq-70b-8192-tool-use-preview', temperature=0.375)

    prompt_guardrail_llm = ChatGroq(model='llama3-groq-70b-8192-tool-use-preview', temperature=0.25).with_structured_output(PromptGuardrail)

    allowed= prompt_guardrail_llm.invoke(user_request).allowed

    if allowed:


        structured_llm = llm.with_structured_output(UserModel)

        name, about_user, queries = structured_llm.invoke(user_request)    # queries = ChatGroq(model='llama3-groq-70b-8192-tool-use-preview',temperature=1).with_structured_output(SearchQueries).invoke(prompt_template.format(query=query)).queries

        ollama_ef = chromadb.utils.embedding_functions.OllamaEmbeddingFunction(
            url="http://localhost:11434/api/embeddings",
            model_name="nomic-embed-text",
        )

        chroma_client = chromadb.PersistentClient('database')

        collection = chroma_client.get_or_create_collection(name="tamu_courses_collection", embedding_function=ollama_ef)


        # refactor and check the below code

        results = collection.query(
            query_texts=queries[1],
            n_results=4, # 3-5 is a good tradeoff
            where={"Department":"CSCE"},
        )

        #print(queries)

        recommendations = {}

        descriptions = {}

        for ids, distances, documents in zip(results['ids'], results['distances'], results['documents']):
            for id, distance, document in zip(ids, distances, documents):
                if id in recommendations:
                    recommendations[id].append(distance)
                else:
                    recommendations[id] = [distance]
                    descriptions[id] = document
            #recommendations += result
        # Create a copy of the keys to iterate over
        for course in list(recommendations.keys()):
            if len(recommendations[course]) < len(queries)/2:
                del recommendations[course]
            else:
                recommendations[course] = sum(recommendations[course]) / len(recommendations[course])


        recommendations = dict(sorted(recommendations.items(), key=lambda item: item[1]))

        top_three_recommendations = list(recommendations.keys())[0:3]

        # todo finetune this, for more consistent and helpful output
        prompt = PromptTemplate.from_template("""
        You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know. Use five sentences maximum and keep the answer concise. Utilize Emojis, and Markdown.

        Question: {question}

        Most Relevant Course: {name1} – {description1}

        2nd Most Relevant Course: {name2} – {description2}

        3rd Most Relevant Course: {name3} – {description3}

        Answer:
        """)

        final_message = prompt.invoke(
            {
                "name1": top_three_recommendations[0],
                "name2": top_three_recommendations[1],
                "name3": top_three_recommendations[2],
                "description1": descriptions[top_three_recommendations[0]],
                "description2": descriptions[top_three_recommendations[1]],
                "description3": descriptions[top_three_recommendations[2]],
                "question": user_request
            }
        )

        message = ChatGroq(model='llama3-groq-70b-8192-tool-use-preview', temperature=1).invoke(final_message)

        print(message.content)



    else:
        print("Uh oh! Not allowed sorry!") # make more descriptive

    user_request = input("User: ")



# TODO: add human in the loop when LLM is not entirely sure of the results
# have mechanism to make people more nuanced and specific in what they want (human in the loop)
# have a llm check for accuracy of rag outputs, and re run rag if necessary
# look thru each line of code and see potential features that can be add
