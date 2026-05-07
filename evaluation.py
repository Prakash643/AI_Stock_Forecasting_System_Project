import numpy as np
from sklearn.metrics import mean_squared_error

def rmse(actual, predicted):
    return np.sqrt(mean_squared_error(actual, predicted))
