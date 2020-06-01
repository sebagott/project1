import os

from flask import Flask, session, render_template, request, redirect, url_for, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from goodreads import get_GR_book

app = Flask(__name__)
app.secret_key = b'\x1d\xa2P\x87\xe8\x82\xab1\xed\x85\x1e\xfc`\xf5\xeaF'

# Check for environment variable
if not os.getenv("DATABASE_URL"):
	raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def login_user(name, password):
	
	# check if name exist in DB.
	if db.execute("SELECT * FROM users WHERE name LIKE :name", {"name": name}).rowcount == 0:
		return False
	# check password match.
	pwd_match = db.execute("SELECT password = crypt(:password, password) AS pwd_match from users WHERE name = :name", 
		{"name": name, "password": password}).fetchone()[0]
	if pwd_match:
		user = db.execute("SELECT id, name, avatar_id FROM users WHERE name LIKE :name", {"name": name}).fetchone()
		# store session
		session["user_id"] = user.id
		return True
	return False
	
def get_current_user():
	if "user_id" in session:	
		user = db.execute("SELECT users.id, users.name, avatars.filename FROM users JOIN avatars ON users.avatar_id = avatars.id WHERE users.id = :id",
		 {"id": session["user_id"]}).fetchone()
		return user
	return None	

def get_booksearch_results(search):
	books_match = db.execute("SELECT books.id, title, isbn, year, authors.name FROM books JOIN authors ON books.author_id = authors.id WHERE\
													 LOWER(isbn) LIKE LOWER(:search) OR \
													 LOWER(title) LIKE LOWER(:search) OR \
													 LOWER(authors.name) LIKE LOWER(:search)",
						{"search":  f"%{search}%"}).fetchall()	
	return books_match

def get_book(book_id):
	book = db.execute("SELECT books.id, title, isbn, year, current_rating, authors.name FROM books JOIN authors ON books.author_id = authors.id WHERE books.id = :book_id",
						{"book_id": book_id}).fetchone()	
	return book

def get_reviews(book):
	reviews = db.execute("SELECT reviews.id, reviews.rating, reviews.comment, users.name, avatars.filename FROM reviews\
						JOIN users ON reviews.user_id = users.id JOIN avatars ON users.avatar_id = avatars.id \
	 					WHERE book_id = :book_id", {"book_id":book.id}).fetchall()	
	return reviews

def update_rating(book):
	new_rating = db.execute("SELECT avg(rating) FROM reviews WHERE book_id = :book_id", {"book_id":book.id}).fetchone()[0]
	db.execute("UPDATE books SET current_rating = :new_rating WHERE id = :book_id",
            {"new_rating": new_rating, "book_id": book.id})	
	db.commit()

@app.route("/", methods=["GET", "POST"])
def index():
	if request.method == "POST":
		username = request.form.get("username")
		password = request.form.get("password")
		if login_user(username,password):			
			user = get_current_user()
			return render_template("home.html", user = user)		
		else:
			return render_template("index.html", login_fail = True)

	user = get_current_user()
	if user:
		return redirect(url_for('home'))
	return render_template("index.html")


@app.route("/register", methods = ["GET","POST"])
def register():
	registration_invalid = False
	if request.method == "POST":
		username = request.form.get("username")
		password = request.form.get("password")    				
		avatar_id = request.form.get("avatar_id")  			
		#check if username already exists
		if db.execute("SELECT * FROM users WHERE name LIKE :username",{"username":username}).rowcount == 1:
			registration_invalid = True
		else:							
			db.execute("INSERT INTO users (name, password, avatar_id) VALUES (:name, crypt(:password, gen_salt('md5')), :avatar_id)",
							{"name": username, "password": password, "avatar_id": avatar_id})		
			db.commit()							
			return render_template("index.html", registration_success = True)		
	
	avatars = db.execute("SELECT id, filename from avatars").fetchall()
	return render_template("register.html", avatars = avatars, registration_invalid = registration_invalid)


@app.route("/home", methods= ["GET", "POST"])
def home():
	user = get_current_user()
	if user is None :			
		return render_template("error.html", message = "Please log in first.")	
	if request.method == "POST":
		# get search terms
		search = request.form.get("search")
		if search != "":
			results = get_booksearch_results(search = search)
			if results:
				return render_template("home.html", user = user, search= search, results= results)
			return render_template("home.html", user = user, search= search)	
	return render_template("home.html", user = user)


@app.route("/logout")
def logout():
	if "user_id" in session:
		session.pop("user_id")
	return redirect(url_for('index'))

@app.route("/profile", methods = ["GET","POST"])
def profile():
	if request.method == "GET" or "POST":
		user = get_current_user()
		if user:
			avatars = db.execute("SELECT id, filename FROM avatars").fetchall()
			if request.method == "POST":
				avatar_id = request.form.get("avatar_id")
				if avatar_id is not None:
					avatar_id = int(avatar_id)
				db.execute("UPDATE users SET avatar_id = :avatar_id WHERE id = :user_id",
        		{"avatar_id": avatar_id, "user_id": user.id})
				db.commit()				
				return redirect(url_for('home')) 
			return render_template("profile.html", avatars= avatars, user = user)				
	return render_template("error.html", message = "Please log in first.")


@app.route("/book/<int:book_id>", methods= ["GET", "POST"])
def book(book_id):

	user = get_current_user()
	if user is None :			
		return render_template("error.html", message = "Please log in first.")	
	book = get_book(book_id)	
	reviews = get_reviews(book)	
	can_review = db.execute("SELECT * FROM reviews WHERE book_id = :book_id and user_id = :user_id", {"book_id":book.id, "user_id": user.id}).rowcount == 0

	if request.method == "POST":		
		if not can_review:
			return redirect(url_for('book',book_id=book_id))	

		comment = request.form.get("review")		
		rating = float(request.form.get("rating"))
		db.execute("INSERT INTO reviews (book_id, user_id, rating, comment)  VALUES (:book_id, :user_id, :rating, :comment)",
							 {"book_id": book.id, "user_id": user.id, "rating": rating, "comment": comment})
		db.commit()
		update_rating(book)		
		return redirect(url_for('book',book_id=book_id))

	gr_info = get_GR_book(book.isbn)
	if gr_info:
		grbook = {}
		if "average_rating" in gr_info:
			grbook_rating = gr_info["average_rating"]
			grbook["rating"] = float(grbook_rating)
		if "work_ratings_count" in gr_info:
			grbook_count = gr_info["work_ratings_count"]
			grbook["count"] = grbook_count		
		return render_template("book.html", book= book, user = user, grbook = grbook, reviews= reviews, can_review = can_review)		
	return render_template("book.html", book= book, user = user, reviews= reviews, can_review = can_review)


@app.route("/api/<isbn>", methods=["GET"])
def api(isbn):
	if request.method == "GET":
		book = db.execute("SELECT books.id, title, year, authors.name, isbn, current_rating FROM books JOIN authors ON books.author_id = authors.id WHERE isbn LIKE :isbn",
			{"isbn":isbn}).fetchone()
		print(book)
		if book:
			#get review count
			review_count = db.execute("SELECT * FROM reviews WHERE book_id = :book_id", {"book_id":book.id}).rowcount			
			jbook = jsonify({
				"title": book.title,
				"year": book.year,
				"isbn": book.isbn,
				"author": book.name,				
				"review_count": review_count,
    			"average_score": book.current_rating
			})
			return jbook, 200			
		return jsonify({"error":"Book not found"}), 403
	return jsonify({"error":"Invalid request"}), 400