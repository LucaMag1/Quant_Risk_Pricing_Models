# predicts how likely someone is to default when paying back their loan
import pandas as pd

df = pd.read_excel("Task_3_Loan_Data.xlsx")

print(df.head())

print(df.columns)

X = df.drop(columns=["customer_id", "default"]) #inputs
y = df["default"]  #what we want to predict

print(X.head())
print(y.head())

#We split the data so the model can learn on some borrowers and prove it works on new borrowers.
from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42
)

print(X_train.shape)
print(X_test.shape)

from sklearn.linear_model import LogisticRegression

model = LogisticRegression(max_iter=1000) #model leanrs relationships

model.fit(X_train, y_train)  #model learns
#this lets the model learn patterns from the data

#Use the model to predict defaults for the 2000 test borrowers
#the model doesnt look at the past defaults for these 2000 borrowers only its features
# and predicts defaultness based on the other 8000 used to train the model
y_pred = model.predict(X_test)
print(y_pred[:10])

#now predict probabilities of default rather than just yes or no

y_prob = model.predict_proba(X_test)

print(y_prob[:10])

PD = y_prob[:,1]

# loan amount for the same 2000 borrowers
loan_amount = X_test["loan_amt_outstanding"]

# recovery rate given in the task
recovery_rate = 0.1

# expected loss calculation
expected_loss = PD * loan_amount * (1 - recovery_rate)

print(expected_loss.head().round(2))          #row index          expected loss














