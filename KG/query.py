# import os
# from dotenv import load_dotenv
# from neo4j import GraphDatabase

# load_dotenv()

# URI = os.getenv("NEO4J_URI")
# AUTH = (os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD"))

# driver = GraphDatabase.driver(URI, auth=AUTH)

# def test_query():
#     with driver.session() as session:
#         result = session.run("""
#             MATCH (n)
#             RETURN DISTINCT labels(n) AS node_labels
#             LIMIT 10
#         """)
#         print("✅ Node Labels in PDF_KGs:")
#         for row in result:
#             print("-", row["node_labels"])

#         result = session.run("""
#             MATCH (a)-[r]->(b)
#             RETURN DISTINCT type(r) AS relationship_type
#             LIMIT 10
#         """)
#         print("\n🔗 Relationship Types:")
#         for row in result:
#             print("-", row["relationship_type"])

#         result = session.run("""
#             MATCH (n)
#             RETURN n
#             LIMIT 3
#         """)
#         print("\n🧠 Sample Nodes:")
#         for row in result:
#             print(dict(row["n"]))

# if __name__ == "__main__":
#     test_query()
#     driver.close()
import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

URI = os.getenv("NEO4J_URI")
AUTH = (os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD"))

# Explicitly target the right DB
driver = GraphDatabase.driver(URI, auth=AUTH, database="neo4j")

def test_query():
    with driver.session() as session:
        # Count nodes
        result = session.run("MATCH (n) RETURN count(n) AS node_count")
        print("🟢 Total nodes:", result.single()["node_count"])

        # Count relationships
        result = session.run("MATCH ()-[r]->() RETURN count(r) AS rel_count")
        print("🔗 Total relationships:", result.single()["rel_count"])

        # Preview labels
        result = session.run("MATCH (n) RETURN DISTINCT labels(n) AS labels LIMIT 10")
        print("\nLabels:")
        for row in result:
            print("-", row["labels"])

if __name__ == "__main__":
    test_query()
    driver.close()
