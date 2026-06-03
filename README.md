 CineMatch — Movie Recommender System
CineMatch is a Content-Based Movie Recommendation System that suggests movies similar to a user's selected movie.

The recommendation engine analyzes movie metadata such as genres, cast, crew, keywords, and plot descriptions to identify similar movies using Natural Language Processing (NLP) techniques and Cosine Similarity.

The project is deployed as an interactive Streamlit web application with movie posters, ratings, and filtering capabilities.

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

⚙️ Project Workflow
1. Data Collection
Load movies dataset
Load credits dataset
2. Data Preprocessing
Merge datasets
Remove irrelevant columns
Handle missing values
3. Feature Engineering

Extract:

Genres
Keywords
Top Cast Members
Director
Overview

Combine them into a single feature called tags.

4. Text Processing
Convert text to lowercase
Remove spaces
Apply Porter Stemming
5. Vectorization

Use CountVectorizer to convert text into numerical vectors.

6. Similarity Computation

Calculate Cosine Similarity between movie vectors.

7. Recommendation Generation

Return the most similar movies based on similarity scores.

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
