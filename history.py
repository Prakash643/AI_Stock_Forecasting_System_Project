import pandas as pd
import os

FILE = "history.csv"

if not os.path.exists(FILE):
    df = pd.DataFrame(columns=["user","stock","prediction","date"])
    df.to_csv(FILE,index=False)

def save_history(user, stock, prediction):
    df = pd.read_csv(FILE)
    new = pd.DataFrame([[user,stock,prediction,pd.Timestamp.now()]],
                       columns=["user","stock","prediction","date"])
    df = pd.concat([df,new],ignore_index=True)
    df.to_csv(FILE,index=False)

def get_history(user):
    df = pd.read_csv(FILE)
    return df[df['user']==user]
