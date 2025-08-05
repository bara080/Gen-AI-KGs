import os
import pandas as pd
from neo4j import GraphDatabase
from langchain.text_splitter import RecursiveCharacterTextSplitter
from openai import OpenAI
import faiss
import numpy as np

# === Load Environment Variables ===
from dotenv import load_dotenv
load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USERNAME")
NEO4J_PASS = os.getenv("NEO4J_PASSWORD")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))
client = OpenAI(api_key=OPENAI_KEY)

# === Step 1: Load Structured Data ===
def load_structured():
    csv_path = "data/structured/scope3_emissions.csv"
    df = pd.read_csv(csv_path)
    query = """
    MERGE (c:Company {name:$company})
    MERGE (cat:Category {name:$category})
    CREATE (e:Emission {year:$year, amount:$amount})
    MERGE (c)-[:HAS_EMISSION]->(e)
    MERGE (e)-[:OF_CATEGORY]->(cat)
    """
    with driver.session() as session:
        for _, row in df.iterrows():
            session.run(query, company=row['Company'],
                                category=row['Category'],
                                year=int(row['Year']),
                                amount=float(row['Emissions_tCO2e']))
    print(" Structured data loaded into Neo4j")

# === Step 2: Load Unstructured Data ===
def load_unstructured():
    from PyPDF2 import PdfReader
    pdf_path = "data/unstructured/report.pdf"
    reader = PdfReader(pdf_path)
    text = " ".join([p.extract_text() for p in reader.pages])

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_text(text)

    embeddings = []
    for chunk in chunks:
        emb = client.embeddings.create(input=chunk, model="text-embedding-ada-002").data[0].embedding
        embeddings.append(emb)

    index = faiss.IndexFlatL2(len(embeddings[0]))
    index.add(np.array(embeddings).astype('float32'))
    faiss.write_index(index, "embeddings/faiss/scope3.index")

    with driver.session() as session:
        for i, chunk in enumerate(chunks):
            session.run("""
                MERGE (d:Document {id:$id, text:$text})
            """, id=f"doc_{i}", text=chunk)
    print(" Unstructured data processed & vector index created")

# === Step 3: Verify Graph ===
def verify_graph():
    with driver.session() as session:
        result = session.run("""
        MATCH (c:Company)-[:HAS_EMISSION]->(e:Emission)-[:OF_CATEGORY]->(cat:Category)
        RETURN c.name, e.year, e.amount, cat.name
        LIMIT 10
        """)
        for record in result:
            print(record)

if __name__ == "__main__":
    load_structured()
    load_unstructured()
    verify_graph()
