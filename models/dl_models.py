from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from tensorflow.keras.callbacks import EarlyStopping

def reshape(X):
    return X.reshape((X.shape[0], 1, X.shape[1]))

def build_lstm(input_shape):
    model = Sequential([
        LSTM(64, input_shape=input_shape),
        Dense(1, activation='sigmoid')
    ])
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    return model

def train_lstm(model, X_train, y_train):
    model.fit(X_train, y_train, epochs=10, batch_size=32, verbose=0,
              callbacks=[EarlyStopping(monitor='loss', patience=3)])
    return model
