

from flask import Flask, request, jsonify
import requests

app = Flask(__name__)
API_KEY = '0f1668dbad7345958c0eebd73784b93d'

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return jsonify({
            "message": "Send a POST request with JSON like: { 'queryResult': { 'parameters': { 'unit-currency': { 'currency': 'USD', 'amount': 100 }, 'currency-name': 'EUR' }}}"
        })

    # POST request handling
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid or missing JSON in request'}), 400

    try:
        src = data['queryResult']['parameters']['unit-currency']['currency']
        amt = data['queryResult']['parameters']['unit-currency']['amount']
        tgt = data['queryResult']['parameters']['currency-name']
    except KeyError:
        return jsonify({'error': 'Missing required parameters in JSON'}), 400

    rate = fetch_conversion_factor(src, tgt)
    if rate is None:
        return jsonify({'error': f"Cannot convert {src} to {tgt}"}), 400

    converted = round(amt * rate, 2)
    response={
        'fulfillmentText':"{} {} is {} {}".format(amt,src,converted,tgt)
    }
    # print(converted)
    return jsonify(response)

def fetch_conversion_factor(source, target):
    try:
        resp = requests.get(
            "https://api.currencyfreaks.com/v2.0/rates/latest",
            params={'apikey': API_KEY}
        )
        resp.raise_for_status()
        rates = resp.json().get('rates', {})

        usd_to_src = float(rates[source])
        usd_to_tgt = float(rates[target])
        return usd_to_tgt / usd_to_src

    except Exception as e:
        print("Fetch error:", e)
        return None

if __name__ == "__main__":
    app.run(debug=True)
