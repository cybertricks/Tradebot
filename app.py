from flask import Flask, request, jsonify
import straddles  # Your trading bot module
from apscheduler.schedulers.background import BackgroundScheduler
import datetime
import json

app = Flask(__name__)
scheduler = BackgroundScheduler()
scheduler.start()

@app.route('/')
def index():
    # HTML form for setting configurations
    return '''
    <form method="POST" action="/set_config">
      API Key: <input type="text" name="key"><br>
      API Secret: <input type="text" name="secret"><br>
      Sell Time: <input type="text" name="sell_time"><br>
      Quantity: <input type="number" name="quantity"><br>
      <input type="submit" value="Set Configuration">
    </form>
    '''

@app.route('/set_config', methods=['POST'])
def set_config():
    config = {
        'API': {
            'key': request.form['key'],
            'secret': request.form['secret']
        },
        'Strategy': {
            'sell_time': request.form['sell_time'],
            'quantity': request.form['quantity']
        }
    }
    with open('config.json', 'w') as file:
        json.dump(config, file)

    sell_time_str = config['Strategy']['sell_time']
    sell_time = datetime.datetime.strptime(sell_time_str, '%H:%M').time()
    now = datetime.datetime.now()
    scheduled_time = datetime.datetime.combine(now.date(), sell_time)
    if scheduled_time < now:
        scheduled_time += datetime.timedelta(days=1)

    scheduler.add_job(straddles.place_order, 'date', run_date=scheduled_time)
    return jsonify({"success": True, "message": "Configuration set and trade scheduled"})

if __name__ == '__main__':
    app.run(debug=True)
