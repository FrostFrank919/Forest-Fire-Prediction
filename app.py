from flask import Flask, request, jsonify, render_template, session, redirect, url_for, flash
import pickle
import numpy as np
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
import json
from custom_log_reg import CustomLogisticRegression

app = Flask(__name__)   
app.secret_key = 'super_secret_key_forest_fire'

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="forestfire"
    )

with open('./model/model.pkl', 'rb') as f:
    model = pickle.load(f)

with open('./model/locations.json', 'r') as f:
    locations_dict = json.load(f)

@app.route('/')
def home():
    return render_template('index.html', user_id=session.get('user_id'), user_name=session.get('user_name'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        
        hashed_password = generate_password_hash(password)
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)", (name, email, hashed_password))
            conn.commit()
            cursor.close()
            conn.close()
            flash("Registration successful. Please login.")
            return redirect(url_for('login'))
        except mysql.connector.Error as err:
            flash(f"Error: {err}")
            return redirect(url_for('register'))
            
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['role'] = user.get('role', 'user')
            return redirect(url_for('home'))
        else:
            flash("Invalid email or password")
            return redirect(url_for('login'))
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user_name', None)
    session.pop('role', None)
    return redirect(url_for('home'))

@app.route('/history')
def history():
    if 'user_id' not in session:
        flash("Please login to view history.")
        return redirect(url_for('login'))
        
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM prediction_history WHERE user_id = %s ORDER BY created_at DESC", (session['user_id'],))
        history_records = cursor.fetchall()
        cursor.close()
        conn.close()
    except mysql.connector.Error as err:
        flash(f"Error fetching history: {err}")
        history_records = []
        
    return render_template('history.html', history=history_records)

@app.route('/get_locations', methods=['GET'])
def get_locations():
    return jsonify(list(locations_dict.keys()))

@app.route('/predict', methods=['POST'])
def predict():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized', 'redirect': '/login'}), 401
        
    try:
        data = request.get_json(force=True)

        location_str = data.get('location', 'Unknown')
        location_encoded = locations_dict.get(location_str, 0)

        features = [location_encoded, data['temp'], data['RH'], data['wind']]
        features_array = np.array(features).reshape(1, -1)

        model_obj = model['model']
        prediction = model_obj.predict(features_array)
        prediction_proba = model_obj.predict_proba(features_array)[0]
        
        if np.sum(prediction_proba) > 0:
            prediction_proba = prediction_proba / np.sum(prediction_proba)

        result = {
            'fire': bool(prediction[0]),
            'probability': prediction_proba.tolist(),
            'accuracy': model_obj.score(features_array, [prediction[0]])
        }

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            query = """
            INSERT INTO prediction_history (user_id, district, temperature, humidity, wind_speed, prediction, prediction_probability) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            prediction_label = "Fire" if prediction[0] else "No Fire"
            max_prob = float(max(prediction_proba)) * 100
            
            cursor.execute(query, (
                session['user_id'], 
                location_str, 
                float(data['temp']), 
                float(data['RH']), 
                float(data['wind']), 
                prediction_label, 
                max_prob
            ))
            conn.commit()
            cursor.close()
            conn.close()
        except mysql.connector.Error as err:
            print(f"Error saving prediction: {err}")

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/admin/users')
def admin_users():
    if session.get('role') != 'admin':
        return redirect(url_for('home'))
        
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, name, email, role FROM users ORDER BY id DESC")
        users = cursor.fetchall()
        cursor.close()
        conn.close()
    except mysql.connector.Error as err:
        users = []
        
    return render_template('admin_users.html', users=users)

@app.route('/admin/users/<int:target_user_id>/history')
def admin_user_history(target_user_id):
    if session.get('role') != 'admin':
        return redirect(url_for('home'))
        
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT name, email FROM users WHERE id = %s", (target_user_id,))
        target_user = cursor.fetchone()
        
        if not target_user:
            cursor.close()
            conn.close()
            return redirect(url_for('admin_users'))
            
        cursor.execute("SELECT * FROM prediction_history WHERE user_id = %s ORDER BY created_at DESC", (target_user_id,))
        history_records = cursor.fetchall()
        cursor.close()
        conn.close()
    except mysql.connector.Error as err:
        target_user = None
        history_records = []
        
    return render_template('admin_user_history.html', target_user=target_user, history=history_records)

if __name__ == '__main__':
    app.run(debug=True, port=560)
