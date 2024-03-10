import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from embedding import generate_embedding
from milvus import init_milvus, get_recommended_songs
from pymilvus import (
    connections,
    utility,
    FieldSchema, CollectionSchema, DataType,
    Collection,
)
from pysecrets import secrets
secrets()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],
)

collection = init_milvus("localhost", "19530", "song_lyrics")

@app.post("/song")
def create_song(song_data: dict):
    song = song_data.get("lyrics")
    amount = song_data.get("numSongs")
    embedding = generate_embedding(song)
    collection.load()
    songs = get_recommended_songs(collection, embedding, amount)
    return {"songs": songs}

