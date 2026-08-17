# SmartCare-Patient-Readmission-Prediction
This project develops and evaluates machine learning models to predict 30-day patient readmission using the SmartCare Hospital dataset. The project includes data preprocessing, exploratory data analysis (EDA), feature engineering, model comparison, explainable AI (SHAP/LIME), and a Streamlit-based prediction prototype.

# The Process of Running the Files
Data_Understanding_Preprocessing
EDA
Model_Development
Model_Evaluation
Explainable_AI

## Features

* Patient readmission prediction
* Patient ID-based prediction
* Batch patient processing
* Readmission probability
* Machine learning model comparison
* Model performance visualization
* Explainable AI using SHAP
* Interactive Streamlit dashboard

## Technologies Used

* Python
* Streamlit
* Pandas
* NumPy
* Scikit-learn
* Plotly
* SHAP
* Joblib

## Project Structure

```text
smartcare-readmission-app/
│
├── app/
│   └── app.py
│
├── data/
│   └── ...
│
├── models/
│   └── ...
│
├── notebooks/
│   └── ...
│
├── requirements.txt
├── README.md
└── .gitignore
```

## Installation and Setup

### 1. Clone the Repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
```

### 2. Navigate to the Project Directory

```bash
cd smartcare-readmission-app
```

### 3. Create a Virtual Environment

Windows:

```bash
python -m venv .venv
```

### 4. Activate the Virtual Environment

Windows:

```bash
.venv\Scripts\activated
```

### 5. Install Required Dependencies

```bash
pip install -r requirements.txt
```

If `requirements.txt` is not available, install the required packages manually:

```bash
pip install streamlit pandas numpy scikit-learn plotly shap joblib
```

## Running the Application

From the project root directory, run:

```bash
streamlit run app/app.py
```

The application will normally be available at:

```text
http://localhost:8501
```

Open the URL in a web browser to access SmartCareAI.

## Stopping the Application

To stop the Streamlit application, press:

```text
Ctrl + C
```

## Requirements

* Python 3.10 or newer
* pip
* Git

Make sure all required model files and datasets are available in their expected project directories before running the application.

## Troubleshooting

### Streamlit is not recognized

Run:

```bash
python -m streamlit run app/app.py
```

### ModuleNotFoundError

Install the missing dependency:

```bash
pip install package-name
```

Or reinstall all dependencies:

```bash
pip install -r requirements.txt
```

### Port 8501 is already in use

Run Streamlit on another port:

```bash
streamlit run app/app.py --server.port 8502
```

Then open:

```text
http://localhost:8502
```