# Movie Recommender System

This is a simple movie recommender system built with Flask. It loads movie and rating data from CSV files and provides a web interface.

## Project Structure

```
movie-recommender/
│
├── app.py          # Main Flask application
├── movies.csv      # Movie metadata
├── ratings.csv     # User ratings
└── README.md       # Project documentation
```

## How to Run

1. Make sure you have Python 3 and pip installed.
2. Install dependencies:
   ```bash
   pip install flask pandas
   ```
3. Run the app:
   ```bash
   python app.py
   ```
4. Open your browser and go to `http://127.0.0.1:5000/`.

## Data
- `movies.csv`: Contains movie information (e.g., movieId, title, genres).
- `ratings.csv`: Contains user ratings (e.g., userId, movieId, rating, timestamp). 