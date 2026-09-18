import numpy as np

class CustomLogisticRegression:
    def __init__(self, learning_rate=0.05, num_iterations=3000):
        self.learning_rate = learning_rate
        self.num_iterations = num_iterations
        self.weights = None
        self.bias = None
        self.mean = None
        self.std = None

    def sigmoid(self, z):
        z = np.clip(z, -250, 250)
        return 1 / (1 + np.exp(-z))

    def fit(self, X, y):
        X_arr = X.values if hasattr(X, 'values') else np.array(X, dtype=float)
        y_arr = y.values if hasattr(y, 'values') else np.array(y, dtype=float)
        
        self.mean = np.mean(X_arr, axis=0)
        self.std = np.std(X_arr, axis=0)
        self.std[self.std == 0] = 1
        X_scaled = (X_arr - self.mean) / self.std

        num_samples, num_features = X_scaled.shape
        self.weights = np.zeros(num_features)
        self.bias = 0

        for i in range(self.num_iterations):
            linear_model = np.dot(X_scaled, self.weights) + self.bias
            y_predicted = self.sigmoid(linear_model)
            dw = (1 / num_samples) * np.dot(X_scaled.T, (y_predicted - y_arr))
            db = (1 / num_samples) * np.sum(y_predicted - y_arr)
            self.weights -= self.learning_rate * dw
            self.bias -= self.learning_rate * db
            
            if (i + 1) % (self.num_iterations // 100) == 0 or (i + 1) == self.num_iterations:
                progress = int(((i + 1) / self.num_iterations) * 100)
                print(f"\rTraining Progress: {progress}% Complete", end="", flush=True)
        print()

    def predict_proba(self, X):
        X_arr = X.values if hasattr(X, 'values') else np.array(X, dtype=float)
        X_scaled = (X_arr - self.mean) / self.std
        linear_model = np.dot(X_scaled, self.weights) + self.bias
        prob = self.sigmoid(linear_model)
        if prob.ndim == 1:
            return np.vstack((1 - prob, prob)).T
        return np.hstack((1 - prob, prob))

    def predict(self, X, threshold=0.5):
        probs = self.predict_proba(X)[:, 1]
        return np.array([1 if i > threshold else 0 for i in probs])

    def score(self, X, y):
        y_pred = self.predict(X)
        y_arr = y.values if hasattr(y, 'values') else np.array(y, dtype=float)
        return np.mean(y_pred == y_arr)
