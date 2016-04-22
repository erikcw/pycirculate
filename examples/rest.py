"""
Example of using pycirculate with a simple Flask RESTful API.

Make sure to send requests with the HTTP header "Content-Type: application/json".

NOTE: Only a single BlueTooth connection can be open to the Anova at a time.  So
if you want to scale this API with multi-processing, keep that in mind to prevent errors
such as:
    `BTLEException: Failed to connect to peripheral 78:A5:04:38:B3:FA, addr type: public`
"""
from flask import Flask, request, jsonify, abort, make_response
from pycirculate.anova import AnovaController
from threading import Timer
import datetime
import logging
import sys

app = Flask(__name__)

ANOVA_MAC_ADDRESS = "78:A5:04:38:B3:FA"


class RESTAnovaController(AnovaController):
    """
    This version of the Anova Controller will keep a connection open over bluetooth
    until the timeout has been reach.

    NOTE: Only a single BlueTooth connection can be open to the Anova at a time.
    """

    TIMEOUT = 1 * 60 # Keep the connection open for this many seconds.
    TIMEOUT_HEARTBEAT = 20

    def __init__(self, mac_address, connect=True, logger=None):
        self.last_command_at = datetime.datetime.now()
        if logger:
            self.logger = logger
        else:
            self.logger = logging.getLogger()
        super(RESTAnovaController, self).__init__(mac_address, connect=connect)

    def timeout(self, seconds=None):
        if not seconds:
            seconds = self.TIMEOUT
        timeout_at = self.last_command_at + datetime.timedelta(seconds=seconds)
        if datetime.datetime.now() > timeout_at:
            self.close()
            self.logger.info('Timeout bluetooth connection. Last command ran at {0}'.format(self.last_command_at))
        else:
            self._timeout_timer = Timer(self.TIMEOUT_HEARTBEAT, lambda: self.timeout())
            self._timeout_timer.setDaemon(True)
            self._timeout_timer.start()
            self.logger.debug('Start connection timeout monitor. Will idle timeout in {0} seconds.'.format(
                (timeout_at - datetime.datetime.now()).total_seconds())) 

    def connect(self):
        super(RESTAnovaController, self).connect()
        self.last_command_at = datetime.datetime.now()
        self.timeout()

    def close(self):
        super(RESTAnovaController, self).close()
        try:
            self._timeout_timer.cancel()
        except AttributeError:
            pass

    def _send_command(self, command):
        if not self.is_connected:
            self.connect()
        self.last_command_at = datetime.datetime.now()
        return super(RESTAnovaController, self)._send_command(command)


# Error handlers

@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({'error': 'Bad request.'}), 400)

@app.errorhandler(404)
def timeout_atnot_found(error):
    return make_response(jsonify({'error': 'Not found.'}), 404)

@app.errorhandler(500)
def server_error(error):
    return make_response(jsonify({'error': 'Server error.'}), 500)

def make_error(status_code, message, sub_code=None, action=None, **kwargs):
    """
    Error with custom message.
    """
    data = {
        'status': status_code,
        'message': message,
    }
    if action:
        data['action'] = action
    if sub_code:
        data['sub_code'] = sub_code
    data.update(kwargs)
    response = jsonify(data)
    response.status_code = status_code
    return response

# REST endpoints

@app.route('/', methods=["GET"])
def index():
    try:
        output = {"anova_status": app.anova_controller.anova_status()}
    except Exception as exc:
        app.logger.error(exc)
        return make_error(500, "{0}: {1}".format(repr(exc), str(exc)))

    return jsonify(output)

@app.route('/temp', methods=["GET"])
def get_temp():
    try:
        output = {"current_temp": app.anova_controller.read_temp(), "set_temp": app.anova_controller.read_set_temp(), "unit": app.anova_controller.read_unit(),}
    except Exception as exc:
        app.logger.error(exc)
        return make_error(500, "{0}: {1}".format(repr(exc), str(exc)))

    return jsonify(output)

@app.route('/temp', methods=["POST"])
def set_temp():
    try:
        temp = request.get_json()['temp']
    except (KeyError, TypeError):
        abort(400)
    temp = float(temp)
    output = {"set_temp": app.anova_controller.set_temp(temp)}

    return jsonify(output)

@app.route('/stop', methods=["POST"])
def stop_anova():
    output = {"status": app.anova_controller.stop_anova()}

    return jsonify(output)

@app.route('/start', methods=["POST"])
def start_anova():
    output = {"status": app.anova_controller.start_anova()}

    return jsonify(output)

if __name__ == '__main__':
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)

    app.anova_controller = RESTAnovaController(ANOVA_MAC_ADDRESS, logger=app.logger)

    app.run(host='0.0.0.0', port=5000, ssl_context='adhoc')
