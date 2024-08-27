import chromadb
import json
import ollama
from collections import Counter

chroma_client = chromadb.PersistentClient('database')

collections = chroma_client.list_collections()
print(collections)  # This should no longer list 'TAMU_Courses'

ollama_ef = chromadb.utils.embedding_functions.OllamaEmbeddingFunction(
    url="http://localhost:11434/api/embeddings",
    model_name="nomic-embed-text",
)


collection = chroma_client.get_or_create_collection(name="tamu_courses_collection",embedding_function=ollama_ef)

all_courses = json.load(open('courses.json')) # use class_info to get this

undergraduate_courses = []

# for key in all_courses.keys():
#     undergraduate_courses += all_courses[key]['Undergraduate']


for course in all_courses['CSCE']['Undergraduate']:
    if int(course['Course Number']) >= 300: # only upper division
        undergraduate_courses.append(course)

# print(len(undergraduate_courses))

collection.add(
    documents = [undergraduate_course['Course Name']+'\n'+undergraduate_course['Description'] for undergraduate_course in undergraduate_courses],
    metadatas = [{"Course Name": undergraduate_course['Course Name'], "Department": undergraduate_course['Department']} for undergraduate_course in undergraduate_courses],
    ids = [undergraduate_course['Department'] + ' ' + undergraduate_course['Course Number'] for undergraduate_course in undergraduate_courses]
)

results = collection.query(
    query_texts=[
        "Conduct logical analyses of business, scientific, engineering, and other technical problems, formulating mathematical models of problems for solution by computers",
        "Consult with users, management, vendors, and technicians to determine computing needs and system requirements."
    ]
,
    n_results=5, # 3-5 is a good tradeoff
    where={"Department":"CSCE"}
)

print(results['ids'])

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
    recommendations[course] = sum(recommendations[course]) / len(recommendations[course])


recommendations = dict(sorted(recommendations.items(), key=lambda item: item[1]))

print(recommendations)

# chroma_client.delete_collection(name='tamu_courses_collection')

# Step 2: Optionally, you can verify that the collection is deleted by listing all collections

# Step 3: Delete the ChromaDB client (if needed)
# del chroma_client
#
#

"""
TODO

1. have filtering by metadata, which includes other things in the json
2. check for cross listed courses
3. Ban special topics, research classes
"""
