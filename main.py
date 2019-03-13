# Copyright 2019 Yoshi Yamaguchi
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import time

import bme680

try:
    sensor = bme680.BME680(bme680.I2C_ADDR_PRIMARY)
except IOError:
    sensor = bme680.BME680(bme680.I2C_ADDR_SECONDARY)

def init_sensor():
    """Sensor configuration flow is documented in p.16 of BME680 datasheet.
    """
    sensor.set_humidity_oversample(bme680.OS_2X)
    sensor.set_pressure_oversample(bme680.OS_2X)
    sensor.set_temperature_oversample(bme680.OS_2X)
    sensor.set_filter(bme680.FILTER_SIZE_3)
    sensor.set_gas_status(bme680.ENABLE_GAS_MEAS)
    sensor.set_gas_heater_duration(150)
    sensor.set_gas_heater_temperature(320)
    sensor.select_gas_heater_profile(0)
    sensor.set_power_mode(bme680.FORCED_MODE)

def main():
    init_sensor()
    try:
        while True:
            if sensor.get_sensor_data():
                data = {
                    'temperature': sensor.data.temperature,
                    'pressure': sensor.data.pressure,
                    'humidity': sensor.data.humidity,
                    'gas_resistance': sensor.data.gas_resistance,
                    'gas_index': sensor.data.gas_index,
                    'meas_index': sensor.data.meas_index,
                    'heat_stable': sensor.data.heat_stable
                }
                print(json.dumps(data))
            time.sleep(1)
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()