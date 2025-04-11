
from flask import Flask, render_template, jsonify
from bot import fetch_data, get_signal, get_account_data, get_open_positions, get_price, ask_ai

app = Flask(__name__)

@app.route('/')
def dashboard():
    df = fetch_data()
    signal = get_signal(df)
    balance = get_account_data()
    price = get_price()
    positions = get_open_positions()
    ai_decision = ask_ai(signal, balance, price, positions) if signal else "NO TRADE"

    return render_template('dashboard.html', signal=signal, balance=balance, price=price,
                           positions=positions, ai_decision=ai_decision)

@app.route('/api/data')
def api_data():
    return jsonify({
        "balance": get_account_data(),
        "price": get_price(),
        "positions": get_open_positions()
    })

if __name__ == '__main__':
    app.run(debug=True)
