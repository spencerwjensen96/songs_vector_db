# hello_milvus.py demonstrates the basic operations of PyMilvus, a Python SDK of Milvus.
# 1. connect to Milvus
# 2. create collection
# 3. insert data
# 4. create index
# 5. search, query, and hybrid search on entities
# 6. delete entities by PK
# 7. drop collection
import time
import uuid

import numpy as np
import pandas as pd
from pymilvus import (
    connections,
    utility,
    FieldSchema, CollectionSchema, DataType,
    Collection,
)

fmt = "\n=== {:30} ===\n"
search_latency_fmt = "search latency = {:.4f}s"
embedding_size = 100

#################################################################################
# 1. connect to Milvus
# Add a new connection alias `default` for Milvus server in `localhost:19530`
# Actually the "default" alias is a buildin in PyMilvus.
# If the address of Milvus is the same as `localhost:19530`, you can omit all
# parameters and call the method as: `connections.connect()`.
#
# Note: the `using` parameter of the following methods is default to "default".
print(fmt.format("start connecting to Milvus"))
connections.connect("default", host="localhost", port="19530")

has = utility.has_collection("song_lyrics")
print(f"Does collection song_lyrics exist in Milvus: {has}")

print(fmt.format("Drop collection `song_lyrics`"))
utility.drop_collection("song_lyrics")

#################################################################################
# 2. create collection
# We're going to create a collection with 3 fields.
# +-+------------+------------+------------------+------------------------------+
# | | field name | field type | other attributes |       field description      |
# +-+------------+------------+------------------+------------------------------+
# |1|    "pk"    |   VarChar  |  is_primary=True |      "primary field"         |
# | |            |            |   auto_id=False  |                              |
# +-+------------+------------+------------------+------------------------------+
# |2|  "random"  |    Double  |                  |      "a double field"        |
# +-+------------+------------+------------------+------------------------------+
# |3|"embeddings"| FloatVector|     dim=8        |  "float vector with dim 8"   |
# +-+------------+------------+------------------+------------------------------+
fields = [
    FieldSchema(name="pk", dtype=DataType.VARCHAR, is_primary=True, auto_id=False, max_length=100),
    FieldSchema(name="track_name", dtype=DataType.VARCHAR, max_length=150),
    FieldSchema(name="track_artist", dtype=DataType.VARCHAR, max_length=150),
    FieldSchema(name="lyrics", dtype=DataType.VARCHAR, max_length=65535),
    FieldSchema(name="embeddings", dtype=DataType.FLOAT_VECTOR, dim=embedding_size)
]

schema = CollectionSchema(fields, "collection of song lyrics")

print(fmt.format("Create collection `song_lyrics`"))
song_lyrics = Collection("song_lyrics", schema, consistency_level="Strong")

################################################################################
# 3. insert data
# We are going to insert 3000 rows of data into `hello_milvus`
# Data to be inserted must be organized in fields.
#
# The insert() method returns:
# - either automatically generated primary keys by Milvus if auto_id=True in the schema;
# - or the existing primary key field from the entities if auto_id=False in the schema.


rng = np.random.default_rng()

# Read the CSV file
df = pd.read_csv("spotify_songs.csv")

# Get the desired columns
track_name = df["track_name"].tolist()
track_artist = df["track_artist"].tolist()
lyrics = df["lyrics"].tolist()

# Combine the columns into entities
num_entities = 100
print(fmt.format(f"Start inserting {num_entities} entities"))
entities = [
    [str(uuid.uuid4()) for _ in range(num_entities)],
    [str(x) for x in track_name[:num_entities]],
    [str(x) for x in track_artist[:num_entities]],
    [str(x) for x in lyrics[:num_entities]],
    rng.random((num_entities, embedding_size))
]

insert_result = song_lyrics.insert(entities)

song_lyrics.flush()
print(f"Number of entities in Milvus: {song_lyrics.num_entities}")  # check the num_entities

################################################################################
# 4. create index
# We are going to create an IVF_FLAT index for hello_milvus collection.
# create_index() can only be applied to `FloatVector` and `BinaryVector` fields.
print(fmt.format("Start Creating index IVF_FLAT"))
index = {
    "index_type": "IVF_FLAT",
    "metric_type": "L2",
    "params": {"nlist": 128},
}

song_lyrics.create_index("embeddings", index)

################################################################################
# 5. search, query, and hybrid search
# After data were inserted into Milvus and indexed, you can perform:
# - search based on vector similarity
# - query based on scalar filtering(boolean, int, etc.)
# - hybrid search based on vector similarity and scalar filtering.
#

# Before conducting a search or a query, you need to load the data in `hello_milvus` into memory.
print(fmt.format("Start loading"))
song_lyrics.load()
exit(1)
# -----------------------------------------------------------------------------
# search based on vector similarity
print(fmt.format("Start searching based on vector similarity"))
vectors_to_search = rng.random((3, embedding_size))
search_params = {
    "metric_type": "L2",
    "params": {"nprobe": 10},
}

start_time = time.time()
result = song_lyrics.search(vectors_to_search, "embeddings", search_params, limit=1, output_fields=["track_name", "track_artist"])
end_time = time.time()

for hits in result:
    for hit in hits:
        print(f"hit: {hit}, Song: {hit.entity.get('track_name')}, Artist: {hit.entity.get('track_artist')}\n")
print(search_latency_fmt.format(end_time - start_time))

###############################################################################
# 6. delete entities by PK
# You can delete entities by their PK values using boolean expressions.
ids = insert_result.primary_keys

expr = f'pk in ["{ids[0]}" , "{ids[1]}"]'
print(fmt.format(f"Start deleting with expr `{expr}`"))

result = song_lyrics.query(expr=expr, output_fields=["track_name", "track_artist", "embeddings"])
print(f"query before delete by expr=`{expr}` -> result: \n-{result[0]}\n-{result[1]}\n")

song_lyrics.delete(expr)

result = song_lyrics.query(expr=expr, output_fields=["track_name", "track_artist", "embeddings"])
print(f"query after delete by expr=`{expr}` -> result: {result}\n")


###############################################################################
# 7. drop collection
# Finally, drop the hello_milvus collection
print(fmt.format("Drop collection `song_lyrics`"))
utility.drop_collection("song_lyrics")