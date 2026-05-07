def add_indicators(df):
    df['SMA_20'] = df['Close'].rolling(20).mean()
    df['EMA_20'] = df['Close'].ewm(span=20).mean()

    delta = df['Close'].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()

    rs = avg_gain / avg_loss
    df['RSI'] = 100 - (100 / (1 + rs))

    return df
