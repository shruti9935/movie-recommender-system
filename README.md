# 🎬 CineMatch — Movie Recommender System

CineMatch is a **Content-Based Movie Recommendation System** that suggests movies
similar to a user's selected movie.

The recommendation engine analyzes movie metadata such as genres, cast, crew, keywords
and plot descriptions to identify similar movies using Natural Language Processing (NLP)
techniques and **Cosine Similarity**.

The project is deployed as an interactive Streamlit web application with movie posters,
ratings and filtering capabilities.

**Try it live →** https://movie-recommender-systemgit-22rxlr8dfrxzbchywpyxnn.streamlit.app/

---

## What It Does

Given any movie from 4,800 titles, it recommends 5 similar movies with live posters
fetched from the TMDB API — based on genres, cast, director, keywords and plot.

## How It Works

1. Merged & cleaned two TMDB datasets on `movie_id`, with custom JSON parsers
2. Built an NLP pipeline: lowercasing → stop-word removal → Porter stemming
3. Vectorized text using Bag of Words (`CountVectorizer`, 5000 features)
4. Ranked recommendations using Cosine Similarity
5. Deployed with Streamlit + live TMDB API poster fetching

## Tech Stack

Python · Pandas · NumPy · Scikit-learn · NLTK · Streamlit · TMDB API · Pickle

---

## Run Locally

```bash
git clone https://github.com/shruti9935/movie-recommender-system.git
cd movie-recommender-system
pip install -r requirements.txt
```

Get a free API key from [TMDB](https://www.themoviedb.org/settings/api), then create a
`.env` file in the project root:

```bash
cp .env.example .env
# then edit .env and set your key
TMDB_API_KEY=your_key_here
```

```bash
streamlit run app.py
```

`.env` is gitignored — never commit it.

### Deploying to Streamlit Community Cloud

`.env` files are not uploaded. Set the key under **Settings → Secrets** instead:

```toml
TMDB_API_KEY = "your_key_here"
```

The app reads `.env` first and falls back to `st.secrets`, so the same code works in
both places.

---

## Project Structure

```
movie-recommender-system/
│
├── app.py                      # Streamlit application
├── movie_recommendar.ipynb     # model-building notebook
├── requirements.txt
├── README.md
├── .env.example                # copy to .env and add your key
│
├── scripts/
│   ├── build_model.py          # rebuilds all three pickles from the two CSVs
│   └── build_neighbours.py     # regenerates neighbours.pkl from similarity.pkl
│
├── movies_dict.pkl             # movie_id / title / tags   (~2 MB)
├── neighbours.pkl              # top-20 rankings, int16     (~188 KB)  ← loaded at runtime
└── similarity.pkl              # full 4800×4800 matrix      (~184 MB, Git LFS)
```

**Not committed:** `tmdb_5000_movies.csv` and `tmdb_5000_credits.csv` (~45 MB), needed
only to re-run the notebook. Download them from the
[TMDB 5000 Movie Dataset on Kaggle](https://www.kaggle.com/datasets/tmdb/tmdb-movie-metadata)
and place them in the project root.

### A note on the two model files

`similarity.pkl` is the full cosine-similarity matrix and is kept as the documented
model artifact. **The app never loads it** — at 185 MB of `float64` it would dominate
the memory budget of a free Streamlit Cloud instance, and it is delivered over Git LFS,
which that platform does not reliably fetch.

Instead the app loads `neighbours.pkl`: the top-20 ranked neighbours per movie as
`int16` indices, ~188 KB. Only the *ordering* is ever needed, never the raw scores.

```bash
python scripts/build_neighbours.py   # neighbours.pkl from an existing similarity.pkl
python scripts/build_model.py        # all three, from the two CSVs
```

`scripts/build_model.py` is the same pipeline as the notebook and produces
byte-identical pickles; use whichever is more convenient.

---

## ⚙️ Project Workflow

1. **Data Collection** — load the movies and credits datasets
2. **Preprocessing** — merge, drop irrelevant columns, handle missing values
3. **Feature Engineering** — extract genres, keywords, top 3 cast, director and overview
   into a single `tags` field
4. **Text Processing** — lowercase, remove spaces, apply Porter stemming
5. **Vectorization** — `CountVectorizer` → numerical vectors
6. **Similarity** — cosine similarity between movie vectors
7. **Recommendation** — return the most similar movies by score

---

## Rebuilding the model

The committed pickles were regenerated after two defects were found in the original
pipeline. If you re-run the notebook, note both:

- **The datasets join on `movie_id`, not on `title`.** Six films share a title with
  another film (`Batman`, `The Host`, `Out of the Blue`), so joining on title
  cross-joined them into four rows each — 4809 rows instead of 4803. In a
  cross-joined row `movie_id` came from the credits CSV while the plot and genres
  came from the movies CSV, so half of those rows described one film under a
  different film's id, and the app fetched the wrong poster and rating for them.

- **`keywords` must be parsed, and `cast`/`crew` must reach `tags`.** In the
  original pickle 91% of rows carried the raw keywords JSON split character by
  character (`{ " i d " : 1 4 6 3 , ...`) and contained no cast or director at all,
  so the vectoriser was largely counting punctuation and digits.

Both are fixed in the notebook and in `scripts/build_model.py`, which assert against
regressions.
