CREATE TABLE avatars (
	id SERIAL PRIMARY KEY,
	filename TEXT NOT NULL
);

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    avatar_id INTEGER NOT NULL REFERENCES avatars     
);

CREATE TABLE authors (
	id SERIAL PRIMARY KEY,
	name TEXT NOT NULL UNIQUE
);

CREATE TABLE books (
	id SERIAL PRIMARY KEY,
	isbn TEXT NOT NULL UNIQUE,
	title TEXT NOT NULL,
	author_id INTEGER NOT NULL REFERENCES authors,
	year INTEGER,
	current_rating REAL
);

CREATE TABLE reviews (
	id SERIAL PRIMARY KEY,
	book_id INTEGER NOT NULL REFERENCES books,
	user_id INTEGER NOT NULL REFERENCES users,
	comment TEXT,
	rating INTEGER NOT NULL CHECK (rating > 0 AND rating <=5)
);

CREATE EXTENSION pgcrypto;
