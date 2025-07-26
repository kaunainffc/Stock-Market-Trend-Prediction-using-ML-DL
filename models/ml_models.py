from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from xgboost import XGBClassifier

def train_ml_models(X_train, y_train):
    rf = RandomForestClassifier()
    svm = SVC(probability=True)
    xgb = XGBClassifier(use_label_encoder=False, eval_metric='logloss')
    rf.fit(X_train, y_train)
    svm.fit(X_train, y_train)
    xgb.fit(X_train, y_train)
    return rf, svm, xgb
