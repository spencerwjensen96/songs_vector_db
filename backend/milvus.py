from pymilvus import (
    connections,
    utility,
    FieldSchema, CollectionSchema, DataType,
    Collection,
)

class Song:
    def __init__(self, title: str, artist: str, lyrics: str):
        self.title = title
        self.artist = artist
        self.lyrics = lyrics

def get_recommended_songs(collection, embedding, amount) -> Song:
    search_params = {
        "metric_type": "L2",
        "params": {"nprobe": 10},
    }
    result = collection.search(embedding, "embeddings", search_params, limit=amount, output_fields=["track_name", "track_artist", "lyrics"])

    songs = []
    for hits in result:
        for hit in hits:
            song = Song(
                title=hit.entity.get('track_name'), 
                artist=hit.entity.get('track_artist'), 
                lyrics=hit.entity.get('lyrics'))
            songs.append(song)

    return songs

def init_milvus(host: str, port: str, collection_name: str):
    
    # Connect to Milvus server
    connections.connect("default", host=host, port=port)

    # Create a collection in Milvus
    dimension = 100

    fields = [
        FieldSchema(name="pk", dtype=DataType.VARCHAR, is_primary=True, auto_id=False, max_length=100),
        FieldSchema(name="track_name", dtype=DataType.VARCHAR, max_length=150),
        FieldSchema(name="track_artist", dtype=DataType.VARCHAR, max_length=150),
        FieldSchema(name="lyrics", dtype=DataType.VARCHAR, max_length=65535),
        FieldSchema(name="embeddings", dtype=DataType.FLOAT_VECTOR, dim=dimension)
    ]

    schema = CollectionSchema(fields, "collection of song lyrics")
    song_lyrics = Collection(collection_name, schema, consistency_level="Strong")
    return song_lyrics
