 CineMatch — Movie Recommender System
A content-based movie recommendation engine built with NLP and Machine Learning, deployed live on Streamlit.

What It Does
Given any movie from 4,800+ titles, it recommends 5 similar movies with live posters fetched from the TMDB API — based on genres, cast, director, keywords and plot.
Try it live → https://movie-recommender-systemgit-22rxlr8dfrxzbchywpyxnn.streamlit.app/

 How It Works

Merged & cleaned two TMDB datasets with custom JSON parsers
Built NLP pipeline: stemming → lowercasing → stop-word removal
Vectorized text using Bag of Words (5000 features)
Ranked recommendations using Cosine Similarity
Deployed with Streamlit + live TMDB API poster fetching

Tech Stack
Python Pandas Scikit-learn NLTK Streamlit TMDB API Pickle

# 📂 Project Structure


CineMatch/
│
├── app.py
├── movie_recommender.ipynb
├── movies_dict.pkl
├── similarity.pkl
├── requirements.txt
├── README.md
│
├── .streamlit/
│   └── secrets.toml
│
└── datasets/
    ├── movies.csv
    └── credits.csv

Run Locally
bashgit clone https://github.com/shruti9935/movie-recommender-system.git

cd movie-recommender-system

pip install -r requirements.txt

streamlit run app.py

Add your TMDB API key in .streamlit/secrets.toml as TMDB_API_KEY = "your_key"
