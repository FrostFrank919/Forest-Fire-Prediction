import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from custom_log_reg import CustomLogisticRegression
import pickle
import json
import os

def main():
    df = pd.read_csv('data/forestfire.csv', low_memory=False)
    
    if 'Temp_2m' in df.columns:
        df['Temp_2m'] = pd.to_numeric(df['Temp_2m'], errors='coerce')
        df['RH_2m'] = pd.to_numeric(df['RH_2m'], errors='coerce')
        df['Precip'] = pd.to_numeric(df['Precip'], errors='coerce')
        df['WindSpeed_10m'] = pd.to_numeric(df['WindSpeed_10m'], errors='coerce')
        
        df = df.dropna(subset=['Temp_2m', 'RH_2m', 'Precip'])
        df['fire'] = ((df['Temp_2m'] > 28) & (df['RH_2m'] < 45) & (df['Precip'] == 0)).astype(int)
        
        df = df.rename(columns={
            'District': 'location',
            'Temp_2m': 'temp',
            'RH_2m': 'RH',
            'WindSpeed_10m': 'wind'
        })
    elif 'latitude' in df.columns and 'temp' in df.columns:
        df['temp'] = pd.to_numeric(df['temp'], errors='coerce')
        df['RH'] = pd.to_numeric(df['RH'], errors='coerce')
        df['wind'] = pd.to_numeric(df['wind'], errors='coerce')
        
        df['temp'] = df['temp'].fillna(df['temp'].median() if not df['temp'].isnull().all() else 30.0)
        df['RH'] = df['RH'].fillna(df['RH'].median() if not df['RH'].isnull().all() else 40.0)
        df['wind'] = df['wind'].fillna(df['wind'].median() if not df['wind'].isnull().all() else 5.0)
        df['location'] = 'Unknown'
        df['fire'] = 1
        
        synthetic_0s = df.copy()
        synthetic_0s['fire'] = 0
        synthetic_0s['temp'] -= 10
        synthetic_0s['RH'] += 30
        df = pd.concat([df, synthetic_0s])
    
    df = df.dropna(subset=['location', 'temp', 'RH', 'wind', 'fire'])
    
    le = LabelEncoder()
    df['location_encoded'] = le.fit_transform(df['location'].astype(str))
    
    locations_list = sorted(df['location'].unique().tolist())
    locations_dict = {loc: int(encoded) for loc, encoded in zip(le.classes_, le.transform(le.classes_))}
    
    os.makedirs('model', exist_ok=True)
    with open('model/locations.json', 'w') as f:
        json.dump(locations_dict, f)
        
    X = df[['location_encoded', 'temp', 'RH', 'wind']]
    y = df['fire']
    
    if len(X) > 200000:
        X, _, y, _ = train_test_split(X, y, train_size=200000, stratify=y, random_state=42)
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = CustomLogisticRegression(learning_rate=0.05, num_iterations=3000)
    model.fit(X_train, y_train)
    
    accuracy = model.score(X_test, y_test)
    print(f"Accuracy: {accuracy * 100:.2f}%")
    
    with open('model/model.pkl', 'wb') as f:
        pickle.dump({'model': model, 'label_encoder': le}, f)
        
if __name__ == '__main__':
    main()
