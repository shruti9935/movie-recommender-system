import streamlit as st
import pickle
import os
import html
import pandas as pd
import requests
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()  # local dev: reads TMDB_API_KEY from .env

# Resolve model files against this file, not the working directory, so
# `streamlit run /path/to/app.py` works from anywhere.
BASE_DIR = Path(__file__).resolve().parent

EARLIEST_YEAR = 1950
CURRENT_YEAR = datetime.now().year

# Inline so the fallback has no third-party dependency of its own -- the old
# via.placeholder.com host no longer resolves, which left even the "no image"
# case showing a broken image.
NO_IMAGE = (
    "data:image/svg+xml;utf8,"
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 450">'
    '<rect width="300" height="450" fill="%231a1a24"/>'
    '<text x="150" y="225" fill="%23c8a97e" font-family="sans-serif" '
    'font-size="16" text-anchor="middle">No Image</text></svg>'
)

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
    with open(BASE_DIR / 'movies_dict.pkl', 'rb') as f:
        movies = pd.DataFrame(pickle.load(f)).reset_index(drop=True)

    # Precomputed top-20 rankings -- see scripts/build_neighbours.py.
    # similarity.pkl is kept in the repo as the model artifact but is never read
    # at runtime: it is 185 MB, and only the ordering it implies is ever needed.
    with open(BASE_DIR / 'neighbours.pkl', 'rb') as f:
        neighbours = pickle.load(f)

    return movies, neighbours


@st.cache_data
def build_labels(titles):
    """Disambiguate the handful of titles that appear more than once, so every
    entry in the selectbox is reachable."""
    counts = Counter(titles)
    seen = {}
    labels = []
    for title in titles:
        if counts[title] == 1:
            labels.append(title)
        else:
            seen[title] = seen.get(title, 0) + 1
            labels.append(f"{title} ({seen[title]})")
    return labels


try:
    movies, neighbours = load_data()
except FileNotFoundError as exc:
    st.error(
        f"**Missing model file:** `{Path(exc.filename).name}`. Generate the model "
        "files with `python scripts/build_model.py` (needs the two TMDB CSVs — see "
        "the README), or `python scripts/build_neighbours.py` if you only need to "
        "rebuild `neighbours.pkl` from an existing `similarity.pkl`."
    )
    st.stop()

labels = build_labels(tuple(movies['title']))

# ---------------- API KEY ---------------- #
# Checked in order:
#   1. TMDB_API_KEY in the environment (or a .env file, for local overrides)
#   2. st.secrets -- the Streamlit dashboard value, when one is set
#   3. the committed .streamlit/secrets.toml, which is what makes the deployed
#      app work with no configuration at all
def _key_from_secrets_file():
    """Read .streamlit/secrets.toml next to this file.

    st.secrets resolves that path against the working directory, so it misses
    when the app is launched from elsewhere -- `streamlit run /path/to/app.py`.
    Model files are already resolved against BASE_DIR; this keeps the key
    consistent with them.
    """
    path = BASE_DIR / '.streamlit' / 'secrets.toml'
    if not path.exists():
        return None
    try:
        import tomllib
        with open(path, 'rb') as f:
            return tomllib.load(f).get("TMDB_API_KEY")
    except ModuleNotFoundError:  # Python < 3.11
        for line in path.read_text(encoding='utf-8').splitlines():
            name, sep, value = line.partition('=')
            if sep and name.strip() == "TMDB_API_KEY":
                return value.strip().strip('"').strip("'") or None
    except (OSError, ValueError):
        return None
    return None


def get_api_key():
    key = os.getenv("TMDB_API_KEY")
    if key:
        return key
    try:
        return st.secrets["TMDB_API_KEY"]
    except Exception:
        pass
    return _key_from_secrets_file()


API_KEY = get_api_key()
if not API_KEY:
    st.error(
        "**TMDB_API_KEY is not set.** The repository ships a key in "
        "`.streamlit/secrets.toml`; if that file is missing, add "
        "`TMDB_API_KEY=your_key` to a `.env` file in the project root, or set it "
        "under Settings > Secrets when deploying to Streamlit Community Cloud."
    )
    st.stop()

# ---------------- POSTER FUNCTION ---------------- #
def _fetch_poster_raw(movie_id):
    """Plain and uncached so it is safe to call from worker threads.

    Never touch st.* in here -- Streamlit's cache and script context are not
    available off the main thread.

    Returns (poster, rating, year, status). `status` distinguishes "TMDB says
    this film has no poster" from "TMDB never answered"; without it a rejected
    API key looked exactly like a catalogue of films with missing artwork.
    """
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US"
    try:
        response = requests.get(url, timeout=5)
    except requests.RequestException:
        return NO_IMAGE, None, None, 'unreachable'

    if response.status_code in (401, 403):
        return NO_IMAGE, None, None, 'unauthorized'
    if response.status_code == 429:
        return NO_IMAGE, None, None, 'rate_limited'
    if response.status_code != 200:
        return NO_IMAGE, None, None, 'error'

    try:
        data = response.json()
    except ValueError:
        return NO_IMAGE, None, None, 'error'

    poster_path = data.get('poster_path')
    full_path = (
        "https://image.tmdb.org/t/p/w500/" + poster_path
        if poster_path else
        NO_IMAGE
    )
    rating = data.get('vote_average')
    release = data.get('release_date') or ''
    return (
        full_path,
        round(rating, 1) if rating is not None else None,
        release[:4] if release else None,
        'ok',
    )


def fetch_posters(movie_ids):
    """Fetch a batch concurrently, remembering only the successes.

    Deliberately a hand-rolled session cache rather than @st.cache_data: that
    memoises whatever the function returned, so a single TMDB blip pinned broken
    placeholders to those films for the life of the process -- and a Streamlit
    Cloud app stays up for days. Caching per movie rather than per batch also
    means overlapping recommendations reuse earlier fetches.
    """
    cache = st.session_state.setdefault('poster_cache', {})
    missing = [m for m in dict.fromkeys(movie_ids) if m not in cache]

    fresh = {}
    if missing:
        with ThreadPoolExecutor(max_workers=8) as pool:
            for mid, result in zip(missing, pool.map(_fetch_poster_raw, missing)):
                fresh[mid] = result
                if result[3] == 'ok':
                    cache[mid] = result

    return {m: cache.get(m) or fresh[m] for m in movie_ids}


# ---------------- RECOMMEND FUNCTION ---------------- #
def _report_fetch_problems(details):
    """Say so when TMDB did not answer.

    Recommendations themselves are local, so a TMDB outage still produces five
    correct titles -- just with no artwork, and with the rating and year filters
    unable to do anything. Previously that was indistinguishable from a working
    app, which made a revoked key impossible to diagnose from the UI.
    """
    statuses = {d[3] for d in details.values()}

    if 'unauthorized' in statuses:
        st.error(
            "**TMDB rejected the API key.** Recommendations below are still correct, "
            "but posters, ratings and release years are unavailable and the sidebar "
            "filters cannot be applied. Check `TMDB_API_KEY`."
        )
    elif 'rate_limited' in statuses:
        st.warning(
            "**TMDB rate limit reached.** Some posters and ratings are missing, and "
            "the sidebar filters skip those titles."
        )
    elif statuses - {'ok'}:
        st.warning(
            "Could not reach TMDB for some titles — posters and ratings may be "
            "missing, and the sidebar filters skip those titles."
        )


def recommend(position, min_rating=0.0, year_range=(EARLIEST_YEAR, CURRENT_YEAR)):
    """`position` is a row offset into `movies`, which is also the row offset
    into `neighbours`. Taking a position rather than a title keeps the two
    aligned by construction -- looking a title up returned an index *label*,
    which silently diverges from the positional offset the moment any row is
    dropped upstream."""
    if not 0 <= position < len(movies):
        st.error("That movie is no longer in the database.")
        return [], [], [], []

    candidates = [int(i) for i in neighbours[position]]
    movie_ids = tuple(int(movies.iloc[i].movie_id) for i in candidates)
    details = fetch_posters(movie_ids)
    _report_fetch_problems(details)

    names, posters, ratings, years = [], [], [], []

    for pos, mid in zip(candidates, movie_ids):
        poster, rating, year, _status = details[mid]

        # Apply sidebar filters. A missing rating or year means TMDB did not tell
        # us, so the film is kept rather than silently dropped.
        if rating is not None and rating < min_rating:
            continue
        if year and year.isdigit() and not (year_range[0] <= int(year) <= year_range[1]):
            continue

        names.append(movies.iloc[pos].title)
        posters.append(poster)
        ratings.append(rating)
        years.append(year)

        if len(names) == 5:
            break

    # If filters are too strict, fall back to the unfiltered top 5
    if not names:
        st.warning("No results match your filters. Showing top recommendations instead.")
        for pos, mid in list(zip(candidates, movie_ids))[:5]:
            poster, rating, year, _status = details[mid]
            names.append(movies.iloc[pos].title)
            posters.append(poster)
            ratings.append(rating)
            years.append(year)

    return names, posters, ratings, years

# ---------------- SIDEBAR ---------------- #
with st.sidebar:
    st.markdown("<p style='font-family:Playfair Display,serif;font-size:1.3rem;font-weight:700;color:#f0e6d3;margin-bottom:1.2rem;'>🎛️ Filters</p>", unsafe_allow_html=True)

    min_rating = st.slider("⭐ Minimum Rating", 0.0, 10.0, 0.0, 0.5,
                           help="Filter recommendations by minimum TMDB rating")

    year_range = st.slider("📅 Release Year Range",
                           EARLIEST_YEAR, CURRENT_YEAR,
                           (EARLIEST_YEAR, CURRENT_YEAR),
                           help="Only show movies within this release window")

    st.markdown("---")
    st.markdown("""
    <div style='font-size:12px;color:rgba(232,224,213,0.5);line-height:1.7;'>
    <b style='color:#c8a97e;font-size:13px;'>How it works</b><br><br>
    This system uses <b>Content-Based Filtering</b>.<br><br>
    Movies are matched by combining genres, cast, director, keywords & plot — 
    then ranked using <b>Cosine Similarity</b> across 4,800 titles.
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
    <div class='hero-tag'>✦ CineMatch</div>
    <div class='hero-title'>Find Your Next<br><span>Favourite Film</span></div>
    <div class='hero-subtitle'>Content-based recommendations across 4,800 movies</div>
</div>
<div class='divider'></div>
""", unsafe_allow_html=True)

# ---------------- MOVIE SELECT ---------------- #
col_select, col_btn = st.columns([4, 1], gap="medium")

with col_select:
    selected_position = st.selectbox(
        "CHOOSE A MOVIE",
        options=range(len(movies)),
        format_func=lambda i: labels[i],
        index=0,
        label_visibility="visible"
    )

with col_btn:
    st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
    recommend_btn = st.button("✦ Recommend", use_container_width=True)

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

# ---------------- RESULTS ---------------- #
# Buttons are only True on the run that handled the click, so gating the results
# on `recommend_btn` alone wiped them the moment a sidebar filter moved -- which
# is exactly what a user reaches for next. Latch it instead and recompute: the
# candidates are unchanged and their posters are already cached, so re-filtering
# costs no extra requests and the filters now apply live.
if recommend_btn:
    st.session_state['show_results'] = True

if st.session_state.get('show_results'):
    with st.spinner("Curating your recommendations..."):
        names, posters, ratings, years = recommend(
            selected_position,
            min_rating=min_rating,
            year_range=year_range
        )

    if names:
        st.markdown("<p class='section-label'>✦ Recommended For You ✦</p>", unsafe_allow_html=True)

        cols = st.columns(5, gap="medium")
        for idx, col in enumerate(cols):
            if idx < len(names):
                with col:
                    # Joined rather than concatenated so a missing rating does not
                    # leave the separator dangling in front of the year.
                    meta = " · ".join(
                        part for part in (
                            f"⭐ {ratings[idx]}" if ratings[idx] is not None else "",
                            years[idx] or "",
                        ) if part
                    )
                    # 217 titles contain an apostrophe and 61 contain &/</>,
                    # which break out of the single-quoted attribute below.
                    safe_title = html.escape(names[idx], quote=True)
                    st.markdown(f"""
                    <div class='movie-card'>
                        <img src='{posters[idx]}' alt='{safe_title}'/>
                        <div class='movie-card-title'>
                            {safe_title}<br>
                            <span style='font-size:11px;color:rgba(200,169,126,0.8);'>{meta}</span>
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