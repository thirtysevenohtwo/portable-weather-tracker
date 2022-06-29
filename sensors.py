import time
import board
import adafruit_gps
import adafruit_lsm303_accel
import adafruit_lis2mdl
import adafruit_bme680
import math
import json

# Many of the basic components to this code are taken/adapted from the URL below.
# https://github.com/adafruit/Adafruit_Learning_System_Guides
# The code used is licenced under the MIT License, see below for details.
# https://github.com/adafruit/Adafruit_Learning_System_Guides/blob/main/LICENSE

i2c = board.I2C()

gps = adafruit_gps.GPS_GtopI2C(i2c, debug=False)

accel = adafruit_lsm303_accel.LSM303_Accel(i2c)
mag = adafruit_lis2mdl.LIS2MDL(i2c)

environment = adafruit_bme680.Adafruit_BME680_I2C(i2c)

gps.send_command(b"PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0")
gps.send_command(b"PMTK220,1000")

last_print = time.monotonic()
while True:
    gps.update()
    x_mag, y_mag, z_mag = mag.magnetic

    current = time.monotonic()
    if current - last_print >= 1.0:
        last_print = current
        if not gps.has_fix:
            continue

        sensor_data = {
            "dateandtime": {
                "year": gps.timestamp_utc.tm_year,
                "month": gps.timestamp_utc.tm_mon,
                "day": gps.timestamp_utc.tm_mday,
                "hour": gps.timestamp_utc.tm_hour,
                "minutes": gps.timestamp_utc.tm_min,
                "seconds": gps.timestamp_utc.tm_sec
            },
            "position": {
                "latitude": gps.latitude,
                "longitude": gps.longitude,
                "latitude_precise": [gps.latitude_degrees, gps.latitude_minutes],
                "longitude_precise": [gps.longitude_degrees, gps.longitude_minutes],
                "altitude": "null",
                "x_microteslas": x_mag,
                "y_microteslas": y_mag,
                "bearing": "0"
            },
            "environment": {
                "temperature": environment.temperature,
                "humidity": environment.humidity,
                "pressure": environment.pressure
            }
        }

        if gps.altitude_m is not None:
            sensor_data["position"]["altitude"] = gps.altitude_m

        bearing = (math.atan2(x_mag, y_mag) * 180) / math.pi

        if bearing < 0:
            bearing += 360

        sensor_data["position"]["bearing"] = bearing

        with open('sensorlog.json', 'w') as f:
            json.dump(sensor_data, f, ensure_ascii=False, indent=4)
