
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import requests

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))
key= "zU2DGyvd8gSgQfgTp0Y4PQ"

def get_GR_book(isbn):
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": key, "isbns": isbn})
    if res.status_code == 200:
        res = res.json()
        if res and "books" in res:
            grbook = res["books"][0]
            return grbook                
    
    return None    
    

def import_book_rating(isbn):
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": key, "isbns": isbn})
    if res.status_code == 200:
        try:
            res = res.json()
            if res and "books" in res:
                grbook = res["books"][0]
                if "average_rating" in grbook:
                    grbook_rating = grbook["average_rating"]
                if "grbook_count" in grbook:
                    grbook_count = grbook["work_ratings_count"]
                    return grbook_rating, grbook_count
            else:
                print(f"No average_rating info in book {book.id}")           
                return None     
        except:
            print(res)            
            return None                            
    print(res)            
    return None

def main():    
    books = db.execute("SELECT id, isbn, current_rating from books WHERE current_rating IS NULL").fetchall()
    n_unrated = len(books)
    print(f"There are {n_unrated} unrated books")
    count = 0
    for book in books:
        grbook_rating = import_book_rating(book.isbn)        
        if grbook_rating is None:
            print(f"No info from Goodreads API for book {book.id}")                    
        else:
            # Update
            db.execute("UPDATE books SET current_rating = :new_rating WHERE id = :book_id",
            {"new_rating": grbook_rating, "book_id": book.id})
            count += 1
            # commit every 100 updates
            if count >= 100:
                db.commit() 
                count = 0            
    if count >0:
        db.commit()
        
if __name__ == "__main__":
    main()
