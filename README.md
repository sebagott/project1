# Project 1

For this project, as required, I developed a website for *Book Reviews*. 

The **starting page** has a login form and a link to register a new account. 

To **create an account** click on the corresponding link and create your account with an username, a password and choosing an avatar. 

If registration is successful you will be redirected to the **home page**, where you can click on your username to change your avatar, you can Logout or you can search for a book using the search bar. If you can't register, for example, because the username you chose is already taken, you will see a message and you can try again.

On any page available after login, you will see the search bar next to your profile name and your avatar. The **search engine** of the website allows you to type an ISBN, a book title, or an author's name. Allowing also to search by partial content of any of this fields.
The results are displayed in a list, where you can click any book to refer to that book's page.

The **book page** displays all the book information, as well as the current rating (with number of reviews on this site) and the current rating obtained from Goodreads web (with its own review count). If you haven't submitted a review for that book, you will be allowed to submit a review with a rating (1 to 5 stars) and optionally a comment.

Below the book's information, you will see a list of cards showing all the available reviews on that title from different users. (For, example if you search for "Lord of the rings", you can see a few reviews, as shown in the screencast)


The files and folders included in this project are as follow:

- `application.py`: The main application file where all the FLASK routes are defined and links the project's database with the FLASK server. Also contains methods that call some repeated queries, such as getting an user by id, etc.

- `goodreads.py`: Contains all communication methods for obtaining information from Goodreads website. When run as script, it will try to initialize the value of 'current_rating' of the *books* table of all books that don't have a rating assigned yet, using the current average rating from Goodreads.

- `import.py`: Contains the script that imports books from the `books.csv` file onto our database.

- `create.sql`: Contains the SQL commands used for creating all tables involved in this project. For password handling the extension 'pgcrypto' was used.

- `style.css`: Contains the personalized CSS styling.

- `templates` folder: Has all html files. Where `base.html` is a macro for all templates and `logged_base.html` is a macro used for the routes only allowed for logged users.

- `static` folder: Contains all images used as icons or background, with proper mention to the authors shown on the footer section of the website.

Finally, the url `/api/isbn` implements the API that will return a 400 error for bad requests (any request different than GET), 404 error for book not found, and 200 HTTP response for success request for a book using the ISBN number, along with a JSON response containing the book information as follows: 

`{
    "title": "Memory",
    "author": "Doug Lloyd",
    "year": 2015,
    "isbn": "1632168146",
    "review_count": 28,
    "average_score": 5.0
}
