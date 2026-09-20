import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from custom_log_reg import CustomLogisticRegression
import pickle
import os

def main():
    print("Loading dataset...")
    df = pd.read_csv('data/merged_cleaned_new.csv', low_memory=False)
    
    print("Preprocessing data...")
    # Map features
    df = df.rename(columns={
        'temperature_2m': 'temp',
        'relative_humidity_2m': 'RH',
        'wind_speed_10m': 'wind'
    })
    
    # Map target ('Y' -> 1, 'N' -> 0)
    df['fire'] = df['forest_fire'].map({'Y': 1, 'N': 0})
    
    # Drop missing values in crucial columns
    df = df.dropna(subset=['temp', 'RH', 'wind', 'fire'])
    
    # We only use weather features now, location is dropped from ML layer
    X = df[['temp', 'RH', 'wind']]
    y = df['fire']
    
    print(f"Dataset shape: {X.shape}")
    print(f"Class distribution: {y.value_counts().to_dict()}")
    
    # Stratified split to ensure both sets have proportional fires
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
    
    print("Training custom logistic regression model...")
    model = CustomLogisticRegression(learning_rate=0.05, num_iterations=3000)
    model.fit(X_train, y_train)
    
    print("\nEvaluating model...")
    y_pred = model.predict(X_test)
    accuracy = model.score(X_test, y_test)
    print(f"\nAccuracy: {accuracy * 100:.2f}%\n")
    print("Detailed Classification Report:")
    print(classification_report(y_test, y_pred, target_names=["No Fire", "Fire"]))
    
    os.makedirs('model', exist_ok=True)
    with open('model/model.pkl', 'wb') as f:
        pickle.dump({'model': model}, f) # No longer need to save label_encoder
    print("Model saved to model/model.pkl")
        
if __name__ == '__main__':
    main()
