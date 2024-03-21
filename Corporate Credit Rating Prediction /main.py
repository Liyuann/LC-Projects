# -*- coding: utf-8 -*-
"""prediction.py

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/163nIY1CAQGMslzjO81mIGYqwvok28xNd
"""

### The seed program was adopted from "Machine Learning for Stock Market Prediction with Step-by-Step Implementation" by Prashant Sharma on October 13, 2021.
### It was retrieved from https://www.analyticsvidhya.com/blog/2021/10/machine-learning-for-stock-market-prediction-with-step-by-step-implementation/ on November 12, 2021.

# Importing the Libraries

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
from sklearn.model_selection import train_test_split
import keras
import tensorflow as tf
from keras.layers.core import Activation, Dense, Dropout
from keras.models import Sequential
from keras.layers import Dense, Embedding
from keras.layers import LSTM
from keras.utils.vis_utils import plot_model
import seaborn as sns
import pywt
from sklearn.ensemble import RandomForestRegressor
from sklearn.feature_selection import SelectFromModel
from sklearn import svm, datasets
import sklearn.model_selection as model_selection
from sklearn.metrics import accuracy_score
from sklearn.metrics import f1_score

# Import raw data file: "corporateCreditRatingWithFinancialRatios.csv"
from google.colab import files
uploaded = files.upload()

import io
df_raw = pd.read_csv(io.BytesIO(uploaded['corporateCreditRatingWithFinancialRatios.csv']))

# import corporate rating conversion: "Ratings.csv"
uploaded = files.upload()
df_rating = pd.read_csv(io.BytesIO(uploaded['Ratings.csv']))

# add rating conversion to dr_raw
df = pd.merge(left=df_raw, right=df_rating, left_on="Rating",
    right_on="Rating", how="left")

# Print the shape of Dataframe and Check for Null Values
print("Dataframe Shape: ", df.shape)
print("Null Value Present: ", df.isnull().values.any())
if df.isnull().values.any() == True:
  print('The number of missing values is ', df.isnull().sum().sum())

# Preview data
print(df.columns)

def svm_model(X,Y):
  X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.3)

  rbf = svm.SVC(kernel='rbf', gamma=0.5, C=0.1).fit(X_train, y_train)
  poly = svm.SVC(kernel='poly', degree=3, C=1).fit(X_train, y_train)

  poly_pred = poly.predict(X_test)
  rbf_pred = rbf.predict(X_test)

  poly_accuracy = accuracy_score(y_test, poly_pred)
  poly_f1 = f1_score(y_test, poly_pred, average='weighted')
  print('Accuracy (Polynomial Kernel): ', "%.2f" % (poly_accuracy*100))
  print('F1 (Polynomial Kernel): ', "%.2f" % (poly_f1*100))

  rbf_accuracy = accuracy_score(y_test, rbf_pred)
  rbf_f1 = f1_score(y_test, rbf_pred, average='weighted')
  print('Accuracy (RBF Kernel): ', "%.2f" % (rbf_accuracy*100))
  print('F1 (RBF Kernel): ', "%.2f" % (rbf_f1*100))
  return [poly_accuracy*100, poly_f1*100, rbf_accuracy*100, rbf_f1*100]

X = df.drop(["Rating", "Ranking", "Rating Agency", "Corporation", "CIK", "SIC Code",
              "Rating Date", "Binary Rating", "Sector", "Ticker"], axis=1)
Y = df["Ranking"]
svm_model(X,Y)

# Random Forest
def randomForest(X,Y):
  X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.3)

  rf = RandomForestRegressor(n_estimators = 100)
  rf.fit(X_train, y_train)
  sel = SelectFromModel(rf)
  sel.fit(X_train, y_train)

  sel.get_support()
  selected_feat= X_train.columns[(sel.get_support())]
  #pd.series(sel.estimator_,feature_importances_,.ravel()).hist()

  feature_names = X_train.columns
  rf.feature_importances_
  plt.barh(feature_names, rf.feature_importances_)
  plt.xlabel("Importance")
  print("Features with greatest importances are ", selected_feat, ".")
  return(selected_feat)

# Splitting to Training set and Test set
X = df.drop(["Rating", "Ranking", "Rating Agency", "Corporation", "CIK", "SIC Code",
            "Rating Date", "Binary Rating", "Sector", "Ticker"], axis=1)
Y = df["Ranking"]
selected_feat = randomForest(X,Y)

# Test using new X and Y
X = df[selected_feat]
Y = df["Ranking"]
svm_model(X,Y)

# Split the data by rating agencies since different agencies may have different
# rating criteria/standards
rateAge_list = df['Rating Agency'].unique()
d = dict()
accuracyPoly_list = []; F1Poly_list = []; accuracyRBF_list = []; F1RBF_list = []
r_accuracyPoly_list = []; r_F1Poly_list = []; r_accuracyRBF_list = []; r_F1RBF_list = []
selectFeat_list = []; data_list = []
for i in range(0,len(rateAge_list)):
  agency = rateAge_list[i]
  print(agency)
  df_new = df.loc[df['Rating Agency'] == agency]
  data_list.append(len(df_new))

  X = df_new.drop(["Rating", "Ranking", "Rating Agency", "Corporation", "CIK", "SIC Code",
              "Rating Date", "Binary Rating", "Sector", "Ticker"], axis=1)
  Y = df_new["Ranking"]
  [poly_accuracy, poly_f1, rbf_accuracy, rbf_f1] = svm_model(X,Y)
  accuracyPoly_list.append(poly_accuracy); F1Poly_list.append(poly_f1)
  accuracyRBF_list.append(rbf_accuracy); F1RBF_list.append(rbf_f1)

  # Random Forest
  selected_feat = randomForest(X,Y)
  selectFeat_list.append(selected_feat)
  X = df_new[selected_feat]
  Y = df_new["Ranking"]
  [poly_accuracy, poly_f1, rbf_accuracy, rbf_f1] = svm_model(X,Y)
  r_accuracyPoly_list.append(poly_accuracy); r_F1Poly_list.append(poly_f1)
  r_accuracyRBF_list.append(rbf_accuracy); r_F1RBF_list.append(rbf_f1)

# Print result into Excel
'''
col = ["Accuracy (Polynomial Kernel)", "F1 (Polynomial Kernel)", 
       "Accuracy (RBF Kernel)", "F1 (RBF Kernel)",
       "RF: Accuracy (Polynomial Kernel)", "RF: F1 (Polynomial Kernel)", 
       "RF: Accuracy (RBF Kernel)", "RF: F1 (RBF Kernel)",
       "Selected Feature"]
df_result = pd.DataFrame(columns=col)
'''
df_result = pd.DataFrame()

df_result["Agency"] = rateAge_list
df_result["No. of Samples"] = data_list
df_result["Accuracy (Polynomial Kernel)"] = accuracyPoly_list
df_result["F1 (Polynomial Kernel)"] = F1Poly_list
df_result["Accuracy (RBF Kernel)"] = accuracyRBF_list
df_result["F1 (RBF Kernel)"] = F1RBF_list
df_result["RF: Accuracy (Polynomial Kernel)"] = r_accuracyPoly_list
df_result["RF: F1 (Polynomial Kernel)"] = r_F1Poly_list
df_result["RF: Accuracy (RBF Kernel)"] = r_accuracyRBF_list
df_result["RF: F1 (RBF Kernel)"] = r_F1RBF_list
df_result["Selected Feature"] = selectFeat_list

import openpyxl
df_result.to_excel('result.xlsx', index=False)

from sklearn.preprocessing import LabelEncoder
from keras.wrappers.scikit_learn import KerasClassifier
from keras.utils import np_utils

# for modeling
from keras.models import Sequential
from keras.layers import Dense, Dropout
from keras.callbacks import EarlyStopping

X = df.drop(["Rating", "Rating Agency", "Corporation", "CIK", "SIC Code",
              "Rating Date", "Binary Rating", "Sector", "Ticker"], axis=1)
Y = df["Rating"]
X = np.asarray(X)

# encode class values as integers
encoder = LabelEncoder()
encoder.fit(Y)
encoded_Y = encoder.transform(Y)
# convert integers to dummy variables (i.e. one hot encoded)
dummy_y = np_utils.to_categorical(encoded_Y)


# build a model
model = Sequential()
model.add(Dense(16, input_shape=(X.shape[1],), activation='relu')) # input shape is (features,)
model.add(Dense(23, activation='softmax'))
model.summary()

# compile the model
model.compile(optimizer='rmsprop', 
              loss='categorical_crossentropy', # this is different instead of binary_crossentropy (for regular classification)
              metrics=['accuracy'])


import keras
from keras.callbacks import EarlyStopping

# early stopping callback
# This callback will stop the training when there is no improvement in  
# the validation loss for 10 consecutive epochs.  
es = keras.callbacks.EarlyStopping(monitor='val_loss', 
                                   mode='min',
                                   patience=10, 
                                   restore_best_weights=True) # important - otherwise you just return the last weigths...

# now we just update our model fit call
history = model.fit(X,
                    dummy_y,
                    callbacks=[es],
                    epochs=8000, # you can set this to a big number!
                    batch_size=10,
                    shuffle=True,
                    validation_split=0.2,
                    verbose=1)

history_dict = history.history

# learning curve
# accuracy
acc = history_dict['accuracy']
val_acc = history_dict['val_accuracy']

# loss
loss = history_dict['loss']
val_loss = history_dict['val_loss']

# range of X (no. of epochs)
epochs = range(1, len(acc) + 1)

# plot
# "r" is for "solid red line"
plt.plot(epochs, acc, 'r', label='Training accuracy')
# b is for "solid blue line"
plt.plot(epochs, val_acc, 'b', label='Validation accuracy')
plt.title('Training and validation accuracy')
plt.xlabel('Epochs')
plt.ylabel('Accuracy')
plt.legend()
plt.show()

from sklearn.metrics import confusion_matrix
from sklearn.metrics import classification_report

preds = model.predict(X) # see how the model did!
print(preds[0]) # i'm spreading that prediction across three nodes and they sum to 1
print(np.sum(preds[0])) # sum it up! Should be 1

# Almost a perfect prediction
# actual is left, predicted is top
# names can be found by inspecting Y
matrix = confusion_matrix(dummy_y.argmax(axis=1), preds.argmax(axis=1))
matrix


# more detail on how well things were predicted
print(classification_report(dummy_y.argmax(axis=1), preds.argmax(axis=1)))