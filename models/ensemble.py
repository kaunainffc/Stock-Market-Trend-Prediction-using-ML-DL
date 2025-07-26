import numpy as np
from sklearn.metrics import accuracy_score

def get_prediction(model, X_test, y_test=None, deep=False):
    y_pred = model.predict(X_test)
    if deep:
        y_pred = y_pred.flatten()
    y_pred = (y_pred > 0.5).astype(int)
    acc = accuracy_score(y_test, y_pred) if y_test is not None else 1
    return y_pred[-1], acc

def vote_ensemble(models_dict, X_test, X_test_rnn, y_test):
    predictions = {
        name: get_prediction(model, X_test_rnn if name == "LSTM" else X_test,
                             y_test, deep=(name == "LSTM"))
        for name, model in models_dict.items()
    }
    votes, weights = zip(*predictions.values())
    final_vote = int(np.average(votes, weights=weights) >= 0.5)
    return final_vote
