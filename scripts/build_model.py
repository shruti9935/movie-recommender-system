"""Rebuild movies_dict.pkl, similarity.pkl and neighbours.pkl from the source CSVs.

Run from the project root, with tmdb_5000_movies.csv and tmdb_5000_credits.csv
present (see README for the Kaggle link):

    python scripts/build_model.py

Two things here differ from the original notebook, and both were silently
corrupting the model:

1. The join is on `movie_id`, not on `title`. Six titles appear twice in the
   dataset ("Batman", "The Host", "Out of the Blue"), so joining on title
   cross-joined them into 4 rows each -- 4809 rows instead of 4803. Worse, in a
   cross-joined row the `movie_id` came from the credits CSV while the plot and
   genres came from the movies CSV, so half of those rows described one film
   under another film's id.

2. `keywords` is parsed, and `cast`/`crew` actually reach the tags. In the
   shipped pickle the tags ended with the raw keywords JSON split character by
   character ('{ " i d " : 1 4 6 3 , ...'), and no cast or director appeared at
   all -- so 91% of rows fed the vectoriser punctuation and digits instead of
   the features the README advertises.
"""

import argparse
import ast
import os
import pickle
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
from nltk.stem.porter import PorterStemmer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from build_neighbours import build as build_neighbours

MAX_FEATURES = 5000
TOP_CAST = 3


def names(text, limit=None):
    """Pull the `name` field out of a JSON-encoded list of dicts."""
    try:
        parsed = ast.literal_eval(text) if isinstance(text, str) else text
    except (ValueError, SyntaxError):
        return []
    if not isinstance(parsed, list):
        return []
    out = [d['name'] for d in parsed if isinstance(d, dict) and 'name' in d]
    return out[:limit] if limit else out


def directors(text):
    try:
        parsed = ast.literal_eval(text) if isinstance(text, str) else text
    except (ValueError, SyntaxError):
        return []
    if not isinstance(parsed, list):
        return []
    return [d['name'] for d in parsed
            if isinstance(d, dict) and d.get('job') == 'Director']


def collapse(items):
    """'James Cameron' -> 'JamesCameron', so a name stays a single token."""
    return [str(i).replace(" ", "") for i in items]


def build_frame(data_dir):
    movies = pd.read_csv(os.path.join(data_dir, 'tmdb_5000_movies.csv'))
    credits = pd.read_csv(os.path.join(data_dir, 'tmdb_5000_credits.csv'),
                          engine='python', on_bad_lines='skip')

    # `id` in movies is `movie_id` in credits -- the same key under two names.
    movies = movies.rename(columns={'id': 'movie_id'})
    df = movies.merge(credits.drop(columns=['title']), on='movie_id')

    df = df[['movie_id', 'title', 'overview', 'genres', 'keywords', 'cast', 'crew']]
    df = df.dropna(subset=['overview', 'title'])

    # Positions must be contiguous: movies_dict.pkl is addressed by position from
    # app.py, and similarity/neighbours rows are positional too.
    df = df.reset_index(drop=True).copy()

    df['genres'] = df['genres'].apply(names).apply(collapse)
    df['keywords'] = df['keywords'].apply(names).apply(collapse)
    df['cast'] = df['cast'].apply(lambda t: collapse(names(t, TOP_CAST)))
    df['crew'] = df['crew'].apply(lambda t: collapse(directors(t)))
    df['overview'] = df['overview'].apply(lambda t: str(t).split())

    df['tags'] = df['overview'] + df['genres'] + df['keywords'] + df['cast'] + df['crew']

    out = df[['movie_id', 'title', 'tags']].copy()
    out['tags'] = out['tags'].apply(lambda t: ' '.join(t).lower())
    return out


def stem_column(series):
    ps = PorterStemmer()
    cache = {}

    def stem(text):
        words = []
        for w in text.split():
            if w not in cache:
                cache[w] = ps.stem(w)
            words.append(cache[w])
        return ' '.join(words)

    return series.apply(stem)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--data', default='.', help='directory holding the two CSVs')
    ap.add_argument('--out', default='.', help='directory to write the pickles to')
    args = ap.parse_args()

    df = build_frame(args.data)
    print(f"frame {df.shape}  unique movie_id: {df['movie_id'].nunique()}")

    df['tags'] = stem_column(df['tags'])

    cv = CountVectorizer(max_features=MAX_FEATURES, stop_words='english')
    vectors = cv.fit_transform(df['tags']).toarray()
    print(f"vectors {vectors.shape}  vocabulary {len(cv.vocabulary_)}")

    similarity = cosine_similarity(vectors)
    neighbours = build_neighbours(similarity)

    for name, obj in (('movies_dict.pkl', df.to_dict()),
                      ('similarity.pkl', similarity),
                      ('neighbours.pkl', neighbours)):
        path = os.path.join(args.out, name)
        with open(path, 'wb') as f:
            pickle.dump(obj, f, protocol=4)
        print(f"wrote {path} ({os.path.getsize(path) / 1e6:.1f} MB)")


if __name__ == '__main__':
    main()
