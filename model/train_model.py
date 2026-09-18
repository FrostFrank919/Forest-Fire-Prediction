import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report



data = pd.read_csv('C:\\Users\\HP\\OneDrive\\Desktop\\ML_Model\\scrap_ex_project\\data\\forestfires.csv')

data['month'] = data['month'].astype('category').cat.codes
data['day'] = data['day'].astype('category').cat.codes


data['fire'] = np.where(data['area'] > 0, 1, 0)


features = ['temp', 'RH', 'wind']
target = 'fire'

X = data[features]
y = data[target]


X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)


class CustomLogisticRegression:
    def __init__(self, learning_rate=0.01, num_iterations=1000):
        self.learning_rate = learning_rate
        self.num_iterations = num_iterations
        self.weights = None
        self.bias = None

    def sigmoid(self, z):
        z = np.clip(z, -250, 250)
        return 1 / (1 + np.exp(-z))

    def fit(self, X, y):
        X_arr = X.values if hasattr(X, 'values') else X
        y_arr = y.values if hasattr(y, 'values') else y
        
        num_samples, num_features = X_arr.shape
        self.weights = np.zeros(num_features)
        self.bias = 0

        for _ in range(self.num_iterations):
            linear_model = np.dot(X_arr, self.weights) + self.bias
            y_predicted = self.sigmoid(linear_model)

            dw = (1 / num_samples) * np.dot(X_arr.T, (y_predicted - y_arr))
            db = (1 / num_samples) * np.sum(y_predicted - y_arr)

            self.weights -= self.learning_rate * dw
            self.bias -= self.learning_rate * db

    def predict_prob(self, X):
        X_arr = X.values if hasattr(X, 'values') else X
        linear_model = np.dot(X_arr, self.weights) + self.bias
        return self.sigmoid(linear_model)

    def predict(self, X, threshold=0.5):
        y_predicted = self.predict_prob(X)
        return np.array([1 if i > threshold else 0 for i in y_predicted])

    def score(self, X, y):
        y_pred = self.predict(X)
        y_arr = y.values if hasattr(y, 'values') else y
        return np.mean(y_pred == y_arr)


