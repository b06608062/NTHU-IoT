import serial
import time
from threading import Thread
from flask import Flask, request, jsonify, render_template
import db
from datetime import datetime
import math
from werkzeug.serving import make_server

app = Flask(__name__)


class ServerThread(Thread):
    def __init__(self, app):
        Thread.__init__(self)
        self.srv = make_server("127.0.0.1", 5000, app)
        self.ctx = app.app_context()
        self.ctx.push()

    def run(self):
        self.srv.serve_forever()

    def shutdown(self):
        self.srv.shutdown()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/send", methods=["POST"])
def get_location():
    global latitude_p, longitude_p
    data = request.json
    latitude_p = data["latitude"]
    longitude_p = data["longitude"]
    print(
        f"Received coordinates: Latitude = {latitude_p}, Longitude = {longitude_p}",
        flush=True,
    )

    server.shutdown()

    return jsonify({"status": "success"})


def haversine(lat1, lon1):
    global latitude_p, longitude_p
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, latitude_p, longitude_p])

    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.asin(math.sqrt(a))

    r = 6371

    return c * r * 1000


def read_serial():
    ser = serial.Serial("/dev/cu.usbserial-110", 115200)
    ser.bytesize = serial.EIGHTBITS
    ser.parity = serial.PARITY_NONE
    ser.stopbits = serial.STOPBITS_ONE
    ser.timeout = 20
    ser.writeTimeout = 20
    ser.xonxoff = False
    ser.rtscts = False
    ser.dsrdtr = False

    table_name = "DELTA_3_stable"
    mydb = db.Database("IoT")
    global latitude_p, longitude_p

    buffer = ""
    while True:
        try:
            if ser.in_waiting:
                try:
                    data = ser.read(ser.in_waiting).decode("utf-8")
                except UnicodeDecodeError as e:
                    print(f"Decoding error: {e}")
                buffer += data
                if "\n" in buffer:
                    complete_data = buffer.split("\n")[0]
                    buffer = buffer.split("\n")[1]
                    parts = complete_data.split(",")
                    print(parts)
                    unique_id = parts[0]
                    data = parts[1]
                    latitude_c = float(parts[2])
                    longitude_c = float(parts[3])
                    floor = int(parts[4])
                    distance = haversine(latitude_c, longitude_c)
                    if floor > 1:
                        distance = math.sqrt(distance**2 + (3.8 * (floor - 1)) ** 2)
                    print(distance)
                    get_t = datetime.now().isoformat()
                    mydb.update_data(
                        table_name, unique_id, latitude_p, longitude_p, distance, get_t
                    )

            time.sleep(0.1)
        except serial.SerialException as e:
            print(f"Serial exception: {e}")
        except ValueError as e:
            print(f"Value error: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")


if __name__ == "__main__":
    serial_thread = Thread(target=read_serial)
    serial_thread.start()

    server = ServerThread(app)
    server.start()
