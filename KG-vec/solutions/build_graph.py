# import asyncio
# import logging.config
# import os
# from dotenv import load_dotenv
# from neo4j import GraphDatabase
# from neo4j_graphrag.embeddings import OpenAIEmbeddings
# from neo4j_graphrag.experimental.components.text_splitters.fixed_size_splitter import (
#     FixedSizeSplitter,
# )
# from neo4j_graphrag.experimental.pipeline.kg_builder import SimpleKGPipeline
# from neo4j_graphrag.llm.openai_llm import OpenAILLM

# load_dotenv()

# # Set log level to DEBUG for all neo4j_graphrag.* loggers
# logging.config.dictConfig(
#     {
#         "version": 1,
#         "handlers": {
#             "console": {
#                 "class": "logging.StreamHandler",
#             }
#         },
#         "loggers": {
#             "root": {
#                 "handlers": ["console"],
#             },
#             "neo4j_graphrag": {
#                 "level": "DEBUG",
#             },
#         },
#     }
# )

# # Connect to the Neo4j database
# URI = os.getenv("NEO4J_URI")
# AUTH = (os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD"))
# driver = GraphDatabase.driver(URI, auth=AUTH)


# # 1. Chunk the text
# # tag::text_splitter[]
# text_splitter = FixedSizeSplitter(chunk_size=150, chunk_overlap=20)
# # end::text_splitter[]


# # 2. Embed the chunks
# # tag::embedder[]
# embedder = OpenAIEmbeddings(model="text-embedding-3-large")
# # end::embedder[]


# # 3. List entities and relationships to extract
# # tag::schema[]
# entities = ["Person", "House", "Planet", "Organization"]
# relations = ["SON_OF", "HEIR_OF", "RULES", "MEMBER_OF"]
# potential_schema = [
#     ("Person", "SON_OF", "Person"),
#     ("Person", "HEIR_OF", "House"),
#     ("House", "RULES", "Planet"),
#     ("Person", "MEMBER_OF", "Organization"),
# ]
# # end::schema[]


# # 4. Extract nodes and relationships from the chunks
# # tag::llm[]
# llm = OpenAILLM(
#     model_name="gpt-4o",
#     model_params={
#         "max_tokens": 2000,
#         "response_format": {"type": "json_object"},
#         "temperature": 0.0,
#         "seed": 123
#     },
# )
# # end::llm[]


# # 5. Create the pipeline
# # tag::create_pipeline[]
# pipeline = SimpleKGPipeline(
#     driver=driver,
#     text_splitter=text_splitter,
#     embedder=embedder,
#     entities=entities,
#     relations=relations,
#     potential_schema=potential_schema,
#     llm=llm,
#     on_error="IGNORE",
#     from_pdf=False,
# )
# # end::create_pipeline[]


# # 6. Run the pipeline
# # tag::run_pipeline[]
# asyncio.run(
#     pipeline.run_async(
#         text=(
#             "The son of Duke Leto Atreides and the Lady Jessica, Paul is the heir of "
#             "House Atreides, an aristocratic family that rules the planet Caladan. Lady "
#             "Jessica is a Bene Gesserit and an important key in the Bene Gesserit "
#             "breeding program."
#         )
#     )
# )
# # end::run_pipeline[]
# driver.close()
import asyncio
import logging.config
import os
from dotenv import load_dotenv
from neo4j import GraphDatabase
from neo4j_graphrag.embeddings import OpenAIEmbeddings
from neo4j_graphrag.experimental.components.text_splitters.fixed_size_splitter import (
    FixedSizeSplitter,
)
from neo4j_graphrag.experimental.pipeline.kg_builder import SimpleKGPipeline
from neo4j_graphrag.llm.openai_llm import OpenAILLM
from langchain_community.document_loaders import PyPDFLoader

load_dotenv()

# Logging
logging.config.dictConfig(
    {
        "version": 1,
        "handlers": {"console": {"class": "logging.StreamHandler"}},
        "loggers": {
            "root": {"handlers": ["console"]},
            "neo4j_graphrag": {"level": "DEBUG"},
        },
    }
)

# Neo4j connection
URI = os.getenv("NEO4J_URI")
AUTH = (os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD"))
driver = GraphDatabase.driver(URI, auth=AUTH)

# PDF loader
DOCS_PATH = "/Users/bara/Desktop/vegboom/GLEC_FRAMEWORK_v3.1_March_2025_1-3.pdf"
loader = PyPDFLoader(DOCS_PATH)
docs = loader.load()

# Combine all text into one string for pipeline
text_data = "\n".join([d.page_content for d in docs])

# 1. Split text into chunks
text_splitter = FixedSizeSplitter(chunk_size=800, chunk_overlap=100)

# 2. Embedder (GLEC requires accurate embeddings)
embedder = OpenAIEmbeddings(model="text-embedding-3-large")

# 3. Define schema based on GLEC Framework
entities = [
    "TransportChain",
    "TransportChainElement",
    "TransportOperationCategory",
    "HubOperationCategory",
    "EmissionScope",
    "EmissionType",
    "EnergyProvision",
    "Stakeholder",
    "Policy",
    "GreenFreightProgram",
    "Assurance",
    "Methodology"
]

relations = [
    "INCLUDES",
    "OPERATES",
    "USES",
    "REPORTS",
    "ASSURES",
    "ALIGNS_WITH",
    "BELONGS_TO"
]

# Example schema triples (you can expand later)
potential_schema = [
    ("Stakeholder", "OPERATES", "TransportChain"),
    ("TransportChain", "INCLUDES", "TransportChainElement"),
    ("TransportChainElement", "USES", "EnergyProvision"),
    ("TransportChain", "REPORTS", "EmissionType"),
    ("EmissionType", "BELONGS_TO", "EmissionScope"),
    ("Stakeholder", "ALIGNS_WITH", "Policy"),
    ("Policy", "ASSURES", "Assurance"),
    ("Stakeholder", "PART_OF", "GreenFreightProgram"),
]

# 4. LLM
llm = OpenAILLM(
    model_name="gpt-4o",
    model_params={
        "max_tokens": 2000,
        "response_format": {"type": "json_object"},
        "temperature": 0.0,
        "seed": 123
    },
)

# 5. Build the pipeline
pipeline = SimpleKGPipeline(
    driver=driver,
    text_splitter=text_splitter,
    embedder=embedder,
    entities=entities,
    relations=relations,
    potential_schema=potential_schema,
    llm=llm,
    on_error="IGNORE",
    from_pdf=True,   # important for PDF context
)

# 6. Run the pipeline on your PDF content
asyncio.run(pipeline.run_async(text=text_data))

driver.close()
