def trading_signal(rsi):
    if rsi < 30:
        return "BUY 🟢"
    elif rsi > 70:
        return "SELL 🔴"
    else:
        return "HOLD ⚪"
