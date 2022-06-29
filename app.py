from flask import Flask, request, jsonify
import json

app = Flask(__name__)

@app.route('/')
def return_blank():
    return 0


@app.route('/current')
def return_current_sensor_data():  # put application's code here
    with open('sensorlog.json', 'r') as f:
        data = f.read()
    sensor_data = json.loads(data)
    return jsonify(sensor_data)


if __name__ == '__main__':
    app.run()
