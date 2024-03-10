<style>
    .container {
        width: 100%;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }

    form{
        width: 60%;
    }
    .form-group {
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
    }
    .short{
        width: 30%;
    }
    .results {
        margin-top: 2rem;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }
    .song {
        margin-bottom: 1rem;
    }
</style>

<script>
    let numSongs = 1;
    let lyrics = '';
    let songs = [];

    async function handleSubmit(event) {
        event.preventDefault(); // Prevent the form from being submitted normally

        const response = await fetch('http://localhost:8000/song', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ numSongs, lyrics }) // Send the form data as JSON
        });

        if (response.ok) {
            const data = await response.json();
            songs = data.songs;
        } else {
            console.error('Error:', response.status, response.statusText);
        }
    }
</script>

<div class="container">
    <h1>Song Recommender</h1>
    <p class="description">Enter the number of songs to return and write your text below:</p>
    <form on:submit={handleSubmit}>
        <div class="form-group short">
            <label for="numSongs">Number of Songs:</label>
            <input type="number" id="numSongs" bind:value={numSongs} required>
        </div>
        <div class="form-group">
            <label for="textArea">Text:</label>
            <textarea id="textArea" bind:value={lyrics} rows="5" required></textarea>
        </div>
        <button type="submit">Submit</button>
    </form>
    {#if songs.length > 0}
        <div class="results">
            {#each songs as song}
                <div class="song">
                    <h3>{song.title}</h3>
                    <p>Artist: {song.artist}</p>
                </div>
            {/each}
        </div>
    {/if}
</div>

