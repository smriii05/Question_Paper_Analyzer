# Question Classifier 🚀

Question Classifier is an automated question classification system that classifies questions into **easy, moderate, and hard** using a **Decision Tree** classifier. The project aims to assist teachers in creating balanced question papers and help students gauge question difficulty for better preparation.

## Features ✨
- **Decision Tree Classifier**: Determines the difficulty level of questions.
- **Various NLP Techniques**: Utilizes tokenization, lemmatization, and stemming for feature engineering.
- **Feature Engineering**: Incorporates features like `keyword_tfidf`, `avg_question_length`, `sentence_count`, and more.
- **Automated Classification**: Efficiently categorizes questions as easy 🟢, moderate 🟡, or hard 🔴.
- **User Authentication**: Includes a login system for secure access.
- **User History Tracking**: Maintains a record of classified questions for each user.

## Tech Stack 🛠
- **Backend**: Python (Flask)
- **Machine Learning**: Scikit-learn, NLTK, Numpy, Pandas
- **Database**: SQLite
- **Frontend**: HTML, CSS, JavaScript

## Installation ⚙️

1. Clone the repository:
   ```bash
   git clone https://github.com/smriii05/Question_Paper_Analyzer.git
   cd Question_Paper_Analyzer
   ```
2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the application:
   ```bash
   python app.py
   ```
5. Open your browser and go to `http://127.0.0.1:5000/`

## Usage 🏆
- 🔑 **Login/Register** to access the system.
- 📂 Upload a `.txt` file containing correctly formatted questions. Incorrect formats will result in validation errors.
- 🎯 Click the **Classify** button to determine difficulty levels.
- 📊 View results with **difficulty labels** (Easy 🟢, Moderate 🟡, Hard 🔴).
- 🕒 Check the **history** of classified questions at any time.

## Future Enhancements 🚀
- 🏆 Implementing more classification models (e.g., Random Forest, SVM)
- 📝 Adding support for multiple-choice and long-form questions
- 🎨 Improving UI/UX for better user experience


## License 📜
This project is licensed under the **MIT License**- see the [LICENSE](LICENSE) file for details.


---

