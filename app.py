import streamlit as st
import pickle
import pandas as pd
import requests

# ---------------- PAGE CONFIG ---------------- #
st.set_page_config(
    page_title="CineMatch – Movie Recommender",
    page_icon="🎬",
    layout="wide"
)

# ---------------- UI STYLE ---------------- #
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=DM+Sans:wght@300;400;500&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [data-testid="stAppViewContainer"] {
    background-color: #0a0a0f;
    color: #e8e0d5;
    font-family: 'DM Sans', sans-serif;
}

[data-testid="stAppViewContainer"] {
    background: radial-gradient(ellipse at 20% 10%, #1a0a2e 0%, #0a0a0f 50%),
                radial-gradient(ellipse at 80% 90%, #0d1a2e 0%, transparent 60%);
}

/* Hide default streamlit elements */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stDecoration"] { display: none; }

/* Hero Header */
.hero {
    text-align: center;
    padding: 3rem 1rem 1.5rem;
    position: relative;
}
.hero-tag {
    display: inline-block;
    font-family: 'DM Sans', sans-serif;
    font-size: 11px;
    font-weight: 500;
    letter-spacing: 4px;
    text-transform: uppercase;
    color: #c8a97e;
    border: 1px solid rgba(200,169,126,0.3);
    padding: 6px 18px;
    border-radius: 20px;
    margin-bottom: 1.2rem;
}
.hero-title {
    font-family: 'Playfair Display', serif;
    font-size: clamp(2.8rem, 6vw, 5rem);
    font-weight: 900;
    color: #f0e6d3;
    line-height: 1.05;
    letter-spacing: -1px;
    margin-bottom: 0.8rem;
}
.hero-title span {
    color: #c8a97e;
    font-style: italic;
}
.hero-subtitle {
    font-size: 1rem;
    color: rgba(232,224,213,0.5);
    font-weight: 300;
    letter-spacing: 0.5px;
}
.divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(200,169,126,0.4), transparent);
    margin: 2rem auto;
    max-width: 600px;
}

/* Selectbox */
[data-testid="stSelectbox"] > div > div {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(200,169,126,0.25) !important;
    border-radius: 12px !important;
    color: #e8e0d5 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 15px !important;
    padding: 4px 8px !important;
    transition: border-color 0.2s;
}
[data-testid="stSelectbox"] > div > div:hover {
    border-color: rgba(200,169,126,0.6) !important;
}
[data-testid="stSelectbox"] label {
    color: rgba(232,224,213,0.6) !important;
    font-size: 12px !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    font-family: 'DM Sans', sans-serif !important;
}

/* Button */
[data-testid="stButton"] > button {
    background: linear-gradient(135deg, #c8a97e, #a07850) !important;
    color: #0a0a0f !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    letter-spacing: 1.5px !important;
    text-transform: uppercase !important;
    padding: 0.65rem 2.5rem !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 4px 20px rgba(200,169,126,0.25) !important;
}
[data-testid="stButton"] > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 30px rgba(200,169,126,0.4) !important;
}

/* Movie cards */
.movie-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(200,169,126,0.12);
    border-radius: 14px;
    overflow: hidden;
    transition: transform 0.25s ease, border-color 0.25s ease, box-shadow 0.25s ease;
    height: 100%;
}
.movie-card:hover {
    transform: translateY(-6px);
    border-color: rgba(200,169,126,0.4);
    box-shadow: 0 16px 40px rgba(0,0,0,0.5);
}
.movie-card img {
    width: 100%;
    aspect-ratio: 2/3;
    object-fit: cover;
    display: block;
}
.movie-card-title {
    padding: 10px 12px 12px;
    font-family: 'DM Sans', sans-serif;
    font-size: 13px;
    font-weight: 500;
    color: #e8e0d5;
    text-align: center;
    line-height: 1.3;
}

/* Section label */
.section-label {
    font-family: 'DM Sans', sans-serif;
    font-size: 11px;
    font-weight: 500;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: #c8a97e;
    margin-bottom: 1.2rem;
    text-align: center;
}

/* Filter panel */
.filter-header {
    font-family: 'Playfair Display', serif;
    font-size: 1.1rem;
    color: #f0e6d3;
    margin-bottom: 0.5rem;
}

/* Sidebar styling */
[data-testid="stSidebar"] {
    background: rgba(10,10,15,0.95) !important;
    border-right: 1px solid rgba(200,169,126,0.1) !important;
}
[data-testid="stSidebar"] * {
    color: #e8e0d5 !important;
    font-family: 'DM Sans', sans-serif !important;
}

/* Spinner */
[data-testid="stSpinner"] { color: #c8a97e !important; }

/* Error / warning */
.stAlert { border-radius: 10px !important; }

/* Active filter badge */
.filter-active {
    display: inline-block;
    background: rgba(200,169,126,0.15);
    border: 1px solid rgba(200,169,126,0.3);
    color: #c8a97e;
    font-size: 11px;
    padding: 3px 10px;
    border-radius: 20px;
    margin-top: 6px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- LOAD DATA ---------------- #
@st.cache_resource
def load_data():
    movies_dict = pickle.load(open('movies_dict.pkl', 'rb'))
    movies = pd.DataFrame(movies_dict)
    similarity = pickle.load(open('similarity.pkl', 'rb'))
    return movies, similarity

movies, similarity = load_data()

# ---------------- API KEY (SECURE) ---------------- #
# Store your key in Streamlit secrets: Settings > Secrets > TMDB_API_KEY = "your_key"
# For local dev, create .streamlit/secrets.toml with: TMDB_API_KEY = "your_key"
def get_api_key():
    try:
        return st.secrets["TMDB_API_KEY"]
    except Exception:
        # Fallback for local testing only — remove before making repo public
        return ""

# ---------------- POSTER FUNCTION ---------------- #
@st.cache_data(show_spinner=False)
def fetch_poster(movie_id):
    try:
        api_key = get_api_key()
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=en-US"
        response = requests.get(url, timeout=5)
        if response.status_code != 200:
            return "https://via.placeholder.com/300x450?text=No+Image", None, None
        data = response.json()
        poster_path = data.get('poster_path')
        full_path = (
            "https://image.tmdb.org/t/p/w500/" + poster_path
            if poster_path else
            "https://via.placeholder.com/300x450?text=No+Image"
        )
        rating = data.get('vote_average', 0)
        release = data.get('release_date', '')
        year = release[:4] if release else 'N/A'
        return full_path, round(rating, 1), year
    except Exception:
        return "https://via.placeholder.com/300x450?text=No+Image", None, None

# ---------------- FETCH MOVIE DETAILS ---------------- #
@st.cache_data(show_spinner=False)
def fetch_movie_details(movie_id):
    try:
        api_key = get_api_key()
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=en-US"
        response = requests.get(url, timeout=5)
        if response.status_code != 200:
            return {}
        return response.json()
    except Exception:
        return {}

# ---------------- RECOMMEND FUNCTION (FIXED) ---------------- #
def recommend(movie, min_rating=0.0, year_range=(1950, 2024)):
    try:
        movie_index = movies[movies['title'] == movie].index[0]
    except IndexError:
        st.error(f"Movie '{movie}' not found in the database.")
        return [], []

    distances = similarity[movie_index]
    movie_list = sorted(
        list(enumerate(distances)),
        reverse=True,
        key=lambda x: x[1]
    )[1:21]  # Fetch top 20 to allow filtering

    recommended_names = []
    recommended_posters = []
    recommended_ratings = []
    recommended_years = []

    for i in movie_list:
        mid = movies.iloc[i[0]].movie_id
        poster, rating, year = fetch_poster(mid)

        # Apply sidebar filters
        if rating is not None and rating < min_rating:
            continue
        if year and year.isdigit():
            if not (year_range[0] <= int(year) <= year_range[1]):
                continue

        recommended_names.append(movies.iloc[i[0]].title)
        recommended_posters.append(poster)
        recommended_ratings.append(rating)
        recommended_years.append(year)

        if len(recommended_names) == 5:
            break

    # If filters are too strict, fill remaining with unfiltered results
    if len(recommended_names) == 0:
        st.warning("No results match your filters. Showing top recommendations instead.")
        for i in movie_list[:5]:
            mid = movies.iloc[i[0]].movie_id
            poster, rating, year = fetch_poster(mid)
            recommended_names.append(movies.iloc[i[0]].title)
            recommended_posters.append(poster)
            recommended_ratings.append(rating)
            recommended_years.append(year)

    return recommended_names, recommended_posters, recommended_ratings, recommended_years

# ---------------- SIDEBAR ---------------- #
with st.sidebar:
    st.markdown("<p style='font-family:Playfair Display,serif;font-size:1.3rem;font-weight:700;color:#f0e6d3;margin-bottom:1.2rem;'>🎛️ Filters</p>", unsafe_allow_html=True)

    min_rating = st.slider("⭐ Minimum Rating", 0.0, 10.0, 0.0, 0.5,
                           help="Filter recommendations by minimum TMDB rating")

    year_range = st.slider("📅 Release Year Range", 1950, 2024, (1980, 2024),
                           help="Only show movies within this release window")

    st.markdown("---")
    st.markdown("""
    <div style='font-size:12px;color:rgba(232,224,213,0.5);line-height:1.7;'>
    <b style='color:#c8a97e;font-size:13px;'>How it works</b><br><br>
    This system uses <b>Content-Based Filtering</b>.<br><br>
    Movies are matched by combining genres, cast, director, keywords & plot — 
    then ranked using <b>Cosine Similarity</b> across 4800+ titles.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div style='font-size:11px;color:rgba(232,224,213,0.3);'>
    Built with Python · Scikit-learn · NLTK · Streamlit · TMDB API
    </div>
    """, unsafe_allow_html=True)

# ---------------- HERO HEADER ---------------- #
st.markdown("""
<div class='hero'>
    <div class='hero-tag'>✦ AI-Powered Discovery</div>
    <div class='hero-title'>Find Your Next<br><span>Favourite Film</span></div>
    <div class='hero-subtitle'>Content-based recommendations across 4,800+ movies</div>
</div>
<div class='divider'></div>
""", unsafe_allow_html=True)

# ---------------- MOVIE SELECT ---------------- #
col_select, col_btn = st.columns([4, 1], gap="medium")

with col_select:
    movies_list = movies['title'].tolist()
    selected_movie_name = st.selectbox(
        "CHOOSE A MOVIE",
        movies_list,
        index=0,
        label_visibility="visible"
    )

with col_btn:
    st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
    recommend_btn = st.button("✦ Recommend", use_container_width=True)

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

# ---------------- RESULTS ---------------- #
if recommend_btn:
    with st.spinner("Curating your recommendations..."):
        names, posters, ratings, years = recommend(
            selected_movie_name,
            min_rating=min_rating,
            year_range=year_range
        )

    if names:
        st.markdown("<p class='section-label'>✦ Recommended For You ✦</p>", unsafe_allow_html=True)

        cols = st.columns(5, gap="medium")
        for idx, col in enumerate(cols):
            if idx < len(names):
                with col:
                    rating_str = f"⭐ {ratings[idx]}" if ratings[idx] else ""
                    year_str = f"· {years[idx]}" if years[idx] else ""
                    st.markdown(f"""
                    <div class='movie-card'>
                        <img src='{posters[idx]}' alt='{names[idx]}'/>
                        <div class='movie-card-title'>
                            {names[idx]}<br>
                            <span style='font-size:11px;color:rgba(200,169,126,0.8);'>{rating_str} {year_str}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
else:
    # Placeholder state
    st.markdown("""
    <div style='text-align:center;padding:3rem 1rem;'>
        <div style='font-size:3rem;margin-bottom:1rem;'>🎬</div>
        <p style='color:rgba(232,224,213,0.3);font-size:0.95rem;font-family:DM Sans,sans-serif;'>
            Select a movie above and click <b style='color:#c8a97e;'>Recommend</b> to discover similar films
        </p>
    </div>
    """, unsafe_allow_html=True)
