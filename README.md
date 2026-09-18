# Forest Fire Prediction System

A web-based machine learning application built with Flask that predicts the likelihood of forest fires based on meteorological and geographical data.

## Features
- **Fire Prediction:** Uses a Custom Logistic Regression model (built from scratch) to predict forest fire probability based on:
  - District Location
  - Temperature (°C)
  - Relative Humidity (%)
  - Wind Speed (km/h)
- **User Authentication:** Secure user registration and login system.
- **Prediction History:** Authenticated users can view their past predictions.
- **Admin Dashboard:** Admins can view all registered users and their prediction histories.

## Tech Stack
- **Backend:** Python, Flask
- **Machine Learning:** Custom Logistic Regression, NumPy, Pandas, Scikit-Learn
- **Database:** MySQL
- **Frontend:** HTML, CSS (via Flask templates)

## Prerequisites
To run this project locally, make sure you have the following installed:
- Python 3.x
- MySQL Server

## Installation

1. **Clone the repository:**
   (Or simply navigate to your project directory in the terminal).

2. **Install dependencies:**
   Install the required Python packages using `pip`:
   ```bash
   pip install -r requirements.txt
   ```

3. **Database Setup:**
   - Open your MySQL server.
   - Create a database named `forestfire`.
   - Ensure the following tables are created (you may need to configure the schema if provided, but generally `users` and `prediction_history` are required).

4. **Train the Model (Optional):**
   If you wish to retrain the machine learning model with your own dataset, you can run the training script:
   ```bash
   python train.py
   ```
   This will train the custom logistic regression model and save the updated weights to `model/model.pkl` and update `model/locations.json`.

## Usage
1. Start the Flask server:
   ```bash
   python app.py
   ```
2. Open your web browser and go to `http://localhost:560`.
3. Register for an account, log in, and navigate to the prediction page to test the system!

## File Structure
- `app.py`: The main Flask web server routing and logic.
- `train.py`: Script to train the model and save it as a pickle file.
- `custom_log_reg.py`: The custom-built logistic regression ML algorithm.
- `model/`: Directory containing the trained ML model (`model.pkl`) and location encoder (`locations.json`).
- `templates/`: HTML files for the web interface.
- `static/`: CSS and client-side scripts.
- `data/`: Datasets used for training the model.
