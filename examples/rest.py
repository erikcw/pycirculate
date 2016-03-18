"""
Example of using pycirculate with a simple Flask RESTful API.
"""
from flask import Flask, request
from pycirculate.anova import AnovaController
import json
app = Flask(__name__)

ANOVA_MAC_ADDRESS = "78:A5:04:38:B3:FA"

@app.route('/', methods=["GET"])
def index():
    with AnovaController(ANOVA_MAC_ADDRESS) as ctrl:
        output = {"anova_status": ctrl.anova_status()}

    return json.dumps(output)

@app.route('/temp', methods=["GET"])
def get_temp():
    with AnovaController(ANOVA_MAC_ADDRESS) as ctrl:
        output = {"current_temp": ctrl.read_temp()}

    return json.dumps(output)

@app.route('/temp', methods=["POST"])
def set_temp():
    # using standard form posts right now, might want to switch to json
    temp = request.form['temp']
    print temp
    temp = float(temp)
    with AnovaController(ANOVA_MAC_ADDRESS) as ctrl:
        output = {"current_temp": ctrl.set_temp(temp)}

    return json.dumps(output)

@app.route('/stop', methods=["POST"])
def stop_anova():
    with AnovaController(ANOVA_MAC_ADDRESS) as ctrl:
        output = {"status": ctrl.stop_anova()}

    return json.dumps(output)

if __name__ == '__main__':
    app.run(host='0.0.0.0')
