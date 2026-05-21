# AI-Powered Smart Travel Planner ✈️

[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/)
[![Streamlit App](https://img.shields.io/badge/Streamlit-1.35+-FF4B4B.svg)](https://streamlit.io/)
[![NLP Engine](https://img.shields.io/badge/NLP-spaCy-8A2BE2.svg)](https://spacy.io/)
[![AI Model](https://img.shields.io/badge/Gemini%20AI-1.5%20Flash-0F9D58.svg)](https://ai.google.dev/)

An intelligent travel planning web application where users can input travel requirements in plain English, and the system generates a highly personalized, structured trip itinerary. The application features **advanced NLP extraction**, **structured AI Generation using Gemini**, a **smart budgeting engine**, **hotel recommendations**, **local SQLite logging**, and **instant PDF compilation**.

---

## 🌟 Key Features

1. **Natural Language Processing (NLP):**
   Extracts details from free-form queries (e.g. *“Plan a 4-day Goa trip under ₹20,000 with beaches and nightlife”*) including Destination, Duration (Days), Budget, and Preferences. Uses **spaCy Named Entity Recognition** and highly robust fallbacks.
2. **AI-Powered Itinerary Generation:**
   Calls the **Google Gemini API** with modern structured JSON formats to create a logical, day-by-day plan including timings, activities, descriptions, exact locations, and culinary suggestions.
3. **Smart Budget Estimator:**
   Tailors expense allocations (Hotel, Food, Transport, Sightseeing, Miscellaneous) matching the calculated budget comfort tier (Budget, Mid-Range, Luxury).
4. **Hotel Recommendation System:**
   Matches accommodations based on destination, budget range, and trip vibe (Solo, Friends, Family, Romantic). Includes a high-quality local catalog for popular Indian destinations and calls Gemini dynamically for any other city worldwide.
5. **Interactive UI/UX:**
   Stunning glassmorphic custom CSS styling with hover effects, timeline schedules, progress bars, metric cards, and sidebar configuration.
6. **SQLite Storage:**
   Enables users to save generated itineraries locally and reload or delete them on the "Saved Trips" page.
7. **Programmatic PDF Exporter:**
   Downloads the entire trip plan including the budget tables and hotel cards in a beautifully styled, print-ready PDF using `fpdf2`.
8. **Offline Demo Mode:**
   Includes a smart offline backup generator so anyone can test the full functionality of the application immediately without configuring an API key.

---

## 📂 Project Structure

```text
AI_Trip_Planner/
│
├── app.py                      # Main Streamlit Frontend entrypoint
├── requirements.txt            # Python Dependencies
├── utils/
│   ├── nlp_processor.py        # Natural Language Parsing (spaCy + Regex)
│   ├── itinerary_generator.py  # Gemini AI Itinerary logic (fallback mock included)
│   ├── budget_calculator.py    # Cost Allocation & formatting helpers
│   ├── hotel_recommender.py    # Pre-baked catalog & dynamic recommendation system
│   ├── db_manager.py           # SQLite trip logging database operations
│   └── pdf_generator.py        # Dynamic PDF Generation blueprint (fpdf2)
│
├── database/
│   └── trips.db                # SQLite Database (generated programmatically)
│
├── assets/                     # UI graphics & media assets
│
└── README.md                   # Setup & Documentation
```

---

## 🚀 Setup and Installation

Follow these quick steps to set up and run the application locally on your machine:

### 1. Prerequisite
Ensure you have **Python 3.9** or higher installed on your computer.

### 2. Download and Enter Directory
Open your terminal/command prompt and navigate to the project directory:
```bash
cd "AI Trip Planner"
```

### 3. Create a Virtual Environment (Recommended)
Keep your packages isolated and clean:
* **Windows (PowerShell):**
  ```powershell
  python -m venv venv
  .\venv\Scripts\Activate.ps1
  ```
* **macOS / Linux:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

### 4. Install Dependencies
Install all required libraries at once:
```bash
pip install -r requirements.txt
```

### 5. Download spaCy English Model (Optional)
The application will try to download this automatically on its first run, but you can do it manually to ensure zero delay:
```bash
python -m spacy download en_core_web_sm
```

### 6. Set Up Environment Variables (Optional)
Create a `.env` file in the root folder of the project:
```env
GEMINI_API_KEY=your_google_gemini_api_key_here
```
*(Alternatively, you can paste the API Key directly inside the app's sidebar UI!)*

### 7. Run the Web Application
Launch the Streamlit server:
```bash
streamlit run app.py
```
The app will launch automatically in your web browser at `http://localhost:8501`.

---

## 🧠 System Architecture and Workflow

The system is designed with a highly decoupled, modular pipeline to ensure performance and reliability:

1. **User input:** The user types a free-form trip description.
2. **NLP Extraction:** `nlp_processor.py` analyzes the text using GPE/LOC token analysis and matches budget/duration numerical patterns.
3. **Form Verification:** Parameters are shown in editable inputs, letting the user verify or adjust items before submitting.
4. **AI Generation:** The prompt is sent to `gemini-1.5-flash` with a JSON-enforced schema, ensuring rapid and parseable outputs.
5. **Decoupled Enrichment:** Category budgets are allocated and hotel listings are attached based on the selected trip style.
6. **Actions:** The user saves the plan to `trips.db` or exports it as a PDF.

---

## 🛡️ License

This project is built for B.Tech project showcases, educational portfolios, and personal travel planning. Feel free to modify and expand!
