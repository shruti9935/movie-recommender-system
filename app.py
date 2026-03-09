import streamlit as st
import pickle
import pandas as pd
import requests

# ---------------- UI STYLE ---------------- #
st.markdown("""
<style>
.main-title {
    text-align: center;
    font-size: 42px;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='main-title'>🎬 Movie Recommender System</div>", unsafe_allow_html=True)

# ---------------- LOAD DATA ---------------- #
movies_dict = pickle.load(open('movies_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)

similarity = pickle.load(open('similarity.pkl', 'rb'))

# ---------------- POSTER FUNCTION ---------------- #
def fetch_poster(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=f85dd0c4db54d280e041f62e63df9401&language=en-US"
        response = requests.get(url, timeout=5)

        if response.status_code != 200:
            return "https://via.placeholder.com/300x450?text=No+Image"

        data = response.json()

        poster_path = data.get('poster_path')

        if poster_path is None:
            return "https://via.placeholder.com/300x450?text=No+Image"

        full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
        return full_path

    except:
        return "https://via.placeholder.com/300x450?text=No+Image"


# ---------------- RECOMMEND FUNCTION ---------------- #
def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]

    movie_list = sorted(
        list(enumerate(distances)),
        reverse=True,
        key=lambda x: x[1]
    )[1:6]

    recommended_movie_names = []
    recommended_movie_posters = []

    for i in movie_list:

        movie_id = movies.iloc[i[0]].movie_id

        recommended_movie_names.append(
            movies.iloc[i[0]].title
        )

        recommended_movie_posters.append(
            fetch_poster(movie_id)
        )

    return recommended_movie_names, recommended_movie_posters


# ---------------- SELECT MOVIE ---------------- #
movies_list = movies['title'].tolist()

selected_movie_name = st.selectbox(
    "🎥 Select a movie:",
    movies_list
)

st.markdown("---")

# ---------------- BUTTON ---------------- #
if st.button("Recommend Movie"):

    with st.spinner("Finding similar movies..."):

        names, posters = recommend(selected_movie_name)

        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            st.text(names[0])
            st.image(posters[0])

        with col2:
            st.text(names[1])
            st.image(posters[1])

        with col3:
            st.text(names[2])
            st.image(posters[2])

        with col4:
            st.text(names[3])
            st.image(posters[3])

        with col5:
            st.text(names[4])
            st.image(posters[4])


# ---------------- SIDEBAR ---------------- #
st.sidebar.title("🔎 Filters")

min_rating = st.sidebar.slider(
    "Minimum Rating",
    0.0,
    10.0,
    7.0
)

year = st.sidebar.slider(
    "Release Year",
    1950,
    2024,
    (2000, 2020)
)

st.sidebar.markdown("---")

st.sidebar.title("About")

st.sidebar.info("""
Movie recommender system built using:

• Python  
• Pandas  
• Machine Learning  
• Streamlit  
""")