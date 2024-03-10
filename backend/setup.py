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

print(fmt.format("start connecting to Milvus"))
connections.connect("default", host="localhost", port="19530")

has = utility.has_collection("song_lyrics")
print(f"Does collection song_lyrics exist in Milvus: {has}")

print(fmt.format("Drop collection `song_lyrics`"))
utility.drop_collection("song_lyrics")

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

rng = np.random.default_rng()

# Read the CSV file
df = pd.read_csv("spotify_songs.csv")
df = df[df["language"] == "en"]

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
print(entities)
insert_result = song_lyrics.insert(entities)

song_lyrics.flush()
print(f"Number of entities in Milvus: {song_lyrics.num_entities}")  # check the num_entities

print(fmt.format("Start Creating index IVF_FLAT"))
index = {
    "index_type": "IVF_FLAT",
    "metric_type": "L2",
    "params": {"nlist": 128},
}

song_lyrics.create_index("embeddings", index)
exit(1)
print(fmt.format("Start loading"))
song_lyrics.load()