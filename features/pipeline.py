from features.indicators import add_indicators
from features.labeling import create_labels
from features.preprocessing import preprocess
from models.ml_models import train_ml_models
from models.dl_models import build_lstm, train_lstm, reshape
from models.ensemble import vote_ensemble

def run_prediction_pipeline(df):
    df = add_indicators(df)
    df = create_labels(df)
    (X_train, X_test, y_train, y_test), _ = preprocess(df)
    rf, svm, xgb = train_ml_models(X_train, y_train)
    X_train_rnn, X_test_rnn = reshape(X_train), reshape(X_test)
    lstm = train_lstm(build_lstm(X_train_rnn.shape[1:]), X_train_rnn, y_train)
    models = {"RF": rf, "SVM": svm, "XGB": xgb, "LSTM": lstm}
    return vote_ensemble(models, X_test, X_test_rnn, y_test)
