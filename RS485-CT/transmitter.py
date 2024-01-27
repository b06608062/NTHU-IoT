from flask import Flask, render_template, request, jsonify
import serial
from datetime import datetime
import uuid
import db

app = Flask(__name__)

ser = serial.Serial()
ser.port = "/dev/cu.usbserial-1140"
ser.baudrate = 115200
ser.bytesize = serial.EIGHTBITS
ser.parity = serial.PARITY_NONE
ser.stopbits = serial.STOPBITS_ONE
ser.timeout = 5
ser.writeTimeout = 5
ser.xonxoff = False
ser.rtscts = False
ser.dsrdtr = False

try:
    ser.open()
except Exception as ex:
    print("Error opening serial port: " + str(ex))

table_name = "grass_2_dataRate_20s_100kb "


def initialize_database():
    app.db = db.Database("IoT")
    app.db.create_table(table_name)


@app.route("/")
def index():
    return render_template("index.html")


with open("100kbits.txt", "r") as file:
    large_data = file.read()


@app.route("/send", methods=["POST"])
def send():
    if ser.isOpen():
        try:
            content = request.json
            unique_id = str(uuid.uuid4())
            data = content.get("data")
            coordinates = content.get("coordinates")
            latitude_c = coordinates["latitude"]
            longitude_c = coordinates["longitude"]
            floor = content.get("floor")
            mode = content.get("mode")
            data_rate_mode = content.get("data_rate_mode")
            send_t = datetime.now().isoformat()

            app.db.insert_data(
                table_name,
                unique_id,
                data,
                latitude_c,
                longitude_c,
                floor,
                mode,
                send_t,
            )

            if data_rate_mode:
                data_to_send = (
                    f"{unique_id},{large_data},{latitude_c},{longitude_c},{floor}\n"
                )
            else:
                data_to_send = (
                    f"{unique_id},{data},{latitude_c},{longitude_c},{floor}\n"
                )
                print(data_to_send)
            ser.write(data_to_send.encode("utf-8"))

            return jsonify({"success": True, "message": "Data sent successfully."})

        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500
    else:
        return jsonify({"success": False, "message": "Serial port is not open."}), 503


if __name__ == "__main__":
    initialize_database()
    app.run(port=7414, debug=True)
