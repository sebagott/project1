
import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


def import_authors():
    f = open("books.csv")
    reader = csv.reader(f)

    authors = set()
    for isbn, title, author, year in reader:
        if author == "author" and isbn == "isbn" and title == "title" and year == "year":
            pass
        else:
            authors.add(author)
    for name in authors:
        db.execute("INSERT INTO authors (name) VALUES (:name)",
                {"name": name})
        print(f"Added author named {name} to the Database.")
    db.commit()


def get_authors():

    authors = db.execute("SELECT * from authors;").fetchall()
    return authors


def get_author_id(author):
    author = db.execute("SELECT id from authors WHERE name LIKE :author",
                      {"author": author}).fetchone()
    return author.id


def import_books():
    f = open("books.csv")
    reader = csv.reader(f)

    for isbn, title, author, year in reader:
        if author == "author" and isbn == "isbn" and title == "title" and year == "year":
            pass
        else:
            author_id = get_author_id(author)
            db.execute("INSERT INTO books (isbn, title, author_id, year) VALUES (:isbn, :title, :author_id, :year)",
                   {"isbn": isbn, "title": title, "author_id": author_id, "year": year})

            db.commit()


def main():

    authors = get_authors()
    if len(authors) == 0:
        import_authors()
    import_books()
    print("All books and authors imported to database.")


if __name__ == "__main__":
    main()
