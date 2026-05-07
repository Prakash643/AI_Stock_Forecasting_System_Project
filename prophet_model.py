from prophet import Prophet
import pandas as pd
import numpy as np

def prophet_forecast(df, days):
    data = df[['Date', 'Close']]
    data.columns = ['ds', 'y']
    data['y'] = np.log(data['y'])

    model = Prophet()
    model.fit(data)

    future = model.make_future_dataframe(periods=days)
    forecast = model.predict(future)

    forecast[['yhat','yhat_lower','yhat_upper']] = \
        forecast[['yhat','yhat_lower','yhat_upper']].apply(np.exp)

    return forecast
