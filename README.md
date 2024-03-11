# songs_vector_db
Explain how you are feeling today and we will recommend a song.

This is a sample project, which sets up a vector database with songs and embeds their lyrics. The idea is you describe how you are feeling and that text is used to do a similarity lookup in the vector db in order to make a song recommendation.

Begin setup with activating a virtual environment and running 
```
pip install -r requirements.txt
```

## Milvus DB and FastAPI
This project uses milvus db as a vector database. This is in the backend project as a docker container that will run an instance of milvus on localhost:19530.

There is a script called setup.py that will instantiate the db with songs that were taken from [kaggle](https://www.kaggle.com/datasets/imuhammad/audio-features-and-lyrics-of-spotify-songs/data`). After db initialization, you will need to run the backend fast api. This can be done by running: 
```./venv/bin/uvicorn fast-api:app --reload```

## SvelteKit
The front end can be run with the following:
```
npm install
npm run dev -- --open
```

## Embeddings
Right now the embeddings are randomly generated, which doesn't work, but this function can easily be replaced by using embeddings from any LLM.
