import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import streamlit as st
from difflib import get_close_matches

# Load the dataset
movies = pd.read_csv('movies.csv')
ratings = pd.read_csv('ratings.csv')

# Preprocess titles (remove year and make lowercase for better matching)
movies['clean_title'] = movies['title'].str.replace(r' \(\d{4}\)$', '', regex=True)
movies['lower_title'] = movies['clean_title'].str.lower()

# Merge with ratings data
movie_data = pd.merge(movies, ratings.groupby('movieId')['rating'].mean().reset_index(), on='movieId')
movie_data = movie_data.rename(columns={'rating': 'avg_rating'})

# Title-based similarity search
def find_similar_titles(query, titles=movie_data['lower_title'].tolist(), n=5):
    query = query.lower().strip()
    # First check exact match
    exact_matches = movie_data[movie_data['lower_title'] == query]
    if not exact_matches.empty:
        return exact_matches
    
    # Then similar matches
    matches = get_close_matches(query, titles, n=n, cutoff=0.6)
    if matches:
        return movie_data[movie_data['lower_title'].isin(matches)]
    return None

# Genre-based recommendation engine
tfidf = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf.fit_transform(movie_data['genres'])
cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)

def get_genre_recommendations(movie_id, n=5):
    idx = movie_data.index[movie_data['movieId'] == movie_id].tolist()[0]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:n+1]
    movie_indices = [i[0] for i in sim_scores]
    return movie_data.iloc[movie_indices]

# Streamlit UI
st.title('🎬 Movie Recommender')
st.write("Find movies similar to what you like (title-based first, genre-based second)")

# Search input
search_query = st.text_input('Search for a movie:', 
                            placeholder='e.g. The Shawshank Redemption')

if search_query:
    # First try title-based similarity
    similar_titles = find_similar_titles(search_query)
    
    if similar_titles is not None and not similar_titles.empty:
        st.subheader("Did you mean these movies?")
        
        for idx, movie in similar_titles.iterrows():
            with st.expander(f"✨ {movie['title']} (Rating: {movie['avg_rating']:.1f}⭐)",expanded=True):
                st.write(f"**Genres**: {movie['genres']}")
                
                # Get genre recommendations
                recs = get_genre_recommendations(movie['movieId'])
                
                st.write("**Similar movies you might like:**")
                for _, rec in recs.iterrows():
                    st.write(f"- {rec['title']} ({rec['genres']}, Rating: {rec['avg_rating']:.1f})")
    
    else:
        # Fall back to genre-based search
        st.warning(f"No similar titles found for '{search_query}'. Showing genre-based recommendations...")
        
        # Vectorize the search query as if it was a genre
        query_genre = tfidf.transform([search_query])
        query_sim = linear_kernel(query_genre, tfidf_matrix)
        
        sim_scores = list(enumerate(query_sim[0]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        sim_scores = sim_scores[:5]
        
        st.subheader("Movies that might match:")
        for i, score in sim_scores:
            movie = movie_data.iloc[i]
            st.write(f"- {movie['title']} ({movie['genres']}, Rating: {movie['avg_rating']:.1f})")
