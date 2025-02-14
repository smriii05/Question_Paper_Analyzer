from flask import Flask, json, render_template, request, jsonify, redirect, url_for, flash, session
import sqlite3
from datetime import timedelta
from process_questions import process_questions

app = Flask(__name__)
app.secret_key = 'qClassifier'  # For session and flash messages
app.permanent_session_lifetime = timedelta(days=1)  # Set session to last for a d

# Database connection function
def get_db_connection():
    conn = sqlite3.connect("sqlite db/palpasadb.db")
    conn.row_factory = sqlite3.Row  # Allows dictionary-like access
    return conn

# Initialize the database if not exists
def init_db():
    conn = sqlite3.connect("sqlite db/palpasadb.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            fullname TEXT NOT NULL,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Function to create the table
def create_table():
    conn = get_db_connection()  # Get the database connection
    cursor = conn.cursor()  # Create a cursor to interact with the database
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question TEXT NOT NULL
    );
    ''')  # Execute the SQL query to create the table if it doesn't exist
    conn.commit()  # Commit the changes to the database
    conn.close()  # Close the connection

# Call this function when the app starts or at an appropriate place in your app
create_table()

@app.route("/")
def home():
    return render_template('home.html')

# Route to render signup page
@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/register', methods=['POST'])
def register():
    fullname = request.form['fullname']
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']

    try:
        conn = sqlite3.connect("sqlite db/palpasadb.db")
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (fullname, username, email, password) VALUES (?, ?, ?, ?)', 
                       (fullname, username, email, password))
        conn.commit()
        conn.close()
        flash('Registration successful! Please log in.', 'success')
        # Render the login.html template
        return render_template('login.html')
    except sqlite3.IntegrityError as e:
        conn.close()  # Ensure the connection is closed in case of an error
        if 'username' in str(e):
            flash('Username already exists. Please choose another one.', 'error')
        elif 'email' in str(e):
            flash('Email already exists. Please use a different email.', 'error')
        else:
            flash('An error occurred. Please try again.', 'error')
        return redirect(url_for('signup'))

# Route to render the login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']


        conn = sqlite3.connect("sqlite db/palpasadb.db")
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            session['user_id'] = user[0]
            session['username'] = user[2]  
            print("User session set:", session)
            flash('Login successful!', 'success')
            return redirect(url_for('home')) 
        else:
            flash('Invalid username or password. Please try again.', 'error')
            return render_template('login.html')

    return render_template('login.html')

@app.route('/analyze', methods=['GET','POST'])
def analyze():
    # Check if the user is logged in
    if not session.get("username"):
        # Redirect to the login page
        return redirect(url_for("login"))
    
    # Handle GET request to render the analyze page
    if request.method == "GET":
        return render_template('analyze.html')
    
    # Handle POST request to process the uploaded file/content
    elif request.method == "POST":
        if 'file' not in request.files:
            return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']

    if file:
        # Read the file content (assuming text file)
        file_content = file.read().decode('utf-8')

        # Process the content to extract questions
        # For this example, let's split the content by newlines
        questions_list = file_content.splitlines()
        print("Received Questions:", questions_list)

        # Store the questions in the 'questions' variable
        global questions
        questions = questions_list
        results = process_questions(questions)
        # print(results)
        
        difficulty_mapping = {0: 'easy', 1: 'moderate', 2: 'hard'}
        difficulty_level = [difficulty_mapping[int(result)] for result in results]

        conn = sqlite3.connect('sqlite db/palpasadb.db')
        cursor = conn.cursor()
        
        user_id = session.get('user_id')  # Get user_id from session
    
        if not user_id:
            flash("Please log in to submit questions.", "danger")
            return redirect(url_for('login'))  # Redirect to login if user is not logged in
        
        # Insert questions and difficulty levels into the database
        for q_text, difficulty in zip(questions, difficulty_level):
            # Insert each question and its difficulty level
            cursor.execute("INSERT INTO classified_questions (user_id, question_text, difficulty_level) VALUES (?, ?, ?)",(user_id, q_text, difficulty))  

        # Commit changes and close the connection
        conn.commit()
        conn.close()

    success_response = {
        "message": "File successfully processed.",
        "redirect_url": "/results"  # This is the URL to which you want to redirect
    }
    
    return jsonify(success_response)

@app.route('/results')
def results():
    user_id = session.get('user_id')
    conn = sqlite3.connect('sqlite db/palpasadb.db')
    cursor = conn.cursor()
    cursor.execute("""
        SELECT MAX(created_at) FROM classified_questions
        WHERE user_id = ?
    """, (user_id,))
    latest_time = cursor.fetchone()[0]

    # Step 2: Select all rows with the latest created_at timestamp
    cursor.execute("""
        SELECT * FROM classified_questions
        WHERE user_id = ? AND created_at = ?
    """, (user_id, latest_time))
    rows = cursor.fetchall()
    conn.close()
    return render_template('display_result.html', rows=rows)

@app.route('/history')
def history():
    user_id = session.get('user_id')
    conn = sqlite3.connect('sqlite db/palpasadb.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM classified_questions WHERE user_id = ?", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return render_template('history.html', rows=rows)

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# Admin Login Route
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        admin = conn.execute('SELECT * FROM admin WHERE username = ?', (username,)).fetchone()
        conn.close()
        if admin and password:
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid username or password. Please try again.', 'error')
            return render_template('admin_login.html')
    return render_template('admin_login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    # Connect to SQLite database
    conn = get_db_connection()

    # Get stats from the database
    num_users = conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]
    num_questions = conn.execute('SELECT COUNT(*) FROM classified_questions').fetchone()[0]
    conn.close()

    # Read accuracy from classification_report.json
    try:
        with open("classification_report.json", "r") as f:
            report_data = json.load(f)
            model_accuracy = round(report_data.get("accuracy", 0) * 100, 2)  # Convert to percentage and round
    except (FileNotFoundError, json.JSONDecodeError):
        model_accuracy = 0  # Default value if file doesn't exist or is invalid

    # Pass the data to the template
    return render_template(
        'admin_dashboard.html',
        num_users=num_users,
        num_questions=num_questions,
        model_accuracy=model_accuracy
    )


@app.route('/admin/users')
def admin_users():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    conn = get_db_connection()
    users = conn.execute('SELECT * FROM users').fetchall()
    conn.close()
    return render_template('admin_users.html', users=users)


# Delete User
@app.route('/admin/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    conn = get_db_connection()
    conn.execute('DELETE FROM users WHERE user_id = ?', (user_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_users'))


# Admin Logout
@app.route('/admin/logout')
def admin_logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('admin_login'))   


# Analytics Page
@app.route('/admin/analytics')
def admin_analytics():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    # Load the classification report from JSON
    try:
        with open("classification_report.json", "r") as f:
            classification_report = json.load(f)
    except FileNotFoundError:
        classification_report = None
    
    # Define the path to the saved confusion matrix image
    cm_path = "static/confusion_matrix.png"

    return render_template('admin_analytics.html', report=classification_report, cm_path=cm_path)
    

if __name__ == "__main__":
    app.run(debug=True)