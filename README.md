# 📊 GoReview Analytics

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red)
![AI Model](https://img.shields.io/badge/Model-Maestro-purple)
![Scikit-Learn](https://img.shields.io/badge/Library-Scikit--Learn-orange)

**GoReview Analytics** is an end-to-end sentiment analysis solution designed for the Food & Beverage industry (specifically **GoFood**). It automates the process of collecting customer reviews and analyzing them using an advanced Hybrid AI model.

Unlike traditional sentiment analysis that relies solely on star ratings, this tool uses the **Maestro Model** to detect the *true* sentiment of customers, uncovering hidden complaints even in 5-star reviews.

---

## 🧠 Powered by: Maestro Model AI

The core of this application is the **Maestro Model**, a custom-built sentiment classifier that acts as a conductor, harmonizing structured and unstructured data:

1.  **Hybrid Labeling Strategy:**
    * Instead of blindly trusting the Star Rating, the Maestro calculates a **weighted score**.
    * `Final Score = (0.6 * Star_Rating) + (0.4 * Text_Lexicon_Score)`
    * This allows the model to detect anomalies (e.g., sarcasm or "wrong click" 5-star ratings with negative text).
2.  **N-Gram LinearSVC:**
    * Uses **Linear Support Vector Classification (SVM)**.
    * Features **Bigrams** (n-gram range 1,2) to understand context (e.g., distinguishing "Enak" from "Tidak Enak").
3.  **High Accuracy:**
    * Current Model Accuracy: **~84.5%**
    * High Recall on Negative class (87%), ensuring no customer complaint goes unnoticed.

---

## ✨ Key Features

### 1. 🕵️‍♂️ Real-Time Scraping (Local Selenium)
* **Smart Load More:** Automates clicking the "Load More" button until all reviews are fetched.
* **Anti-Ghost Logic:** Automatically detects and fixes shifted CSV columns (e.g., when a user's name contains a comma).
* **Live Feedback:** Shows scraping progress and connects to the restaurant's page instantly.

### 2. 📊 Interactive Dashboard
* **AI vs. Star Rating:** visual comparison between what the customer *rated* vs. what they *wrote*.
* **Top Menu Analysis:** Extracts and visualizes the most ordered menu items based on review data.
* **Word Cloud:** Generates separate word clouds for Positive (Praise) and Negative (Complaints).
* **Sentiment Metrics:** Counts the exact number of satisfied vs. dissatisfied customers.

### 3. 📥 Data Export
* Download the scraped and analyzed data as a clean **CSV file** with an auto-generated filename based on the restaurant's name.

---

## 🛠️ Installation & Usage

Since this application uses Selenium for scraping, it is best run **Locally** to avoid IP blocking issues common with cloud servers.

### Prerequisites
* Python 3.8+
* Google Chrome Browser

### Steps
1.  **Clone the Repository**
    ```bash
    git clone [https://github.com/your-username/goreview-analytics.git](https://github.com/your-username/goreview-analytics.git)
    cd goreview-analytics
    ```

2.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the Application**
    ```bash
    streamlit run app.py
    ```

4.  **Start Analyzing**
    * The app will open in your browser (`http://localhost:8501`).
    * Paste a GoFood Restaurant URL.
    * Click **"Mulai Analisis 🚀"**.

---

## 📂 Project Structure

```text
├── app.py                      # Main Streamlit Application
├── model_sentimen_hybrid.pkl   # The trained Maestro Model
├── requirements.txt            # Python dependencies
├── README.md                   # Project Documentation
└── notebooks/                  # (Optional) Jupyter Notebooks used for training
    ├── 01_Data_Cleaning.ipynb
    └── 02_Model_Training_Hybrid.ipynb

---

# 🤝 Contribution

Feel free to open an issue or submit a pull request if you have ideas to improve the Maestro Model or the scraper logic!