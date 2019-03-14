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
import os
import socket
import time

import bme680
from google.cloud import monitoring_v3


def init_sensor(sensor):
    """Sensor configuration flow is documented in p.16 of BME680 datasheet.

    :param sensor: An instance of BME680
    :type sensor: bme680.BME680
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


class MissingProjectIdError(Exception):
    pass


def get_project_id():
    """Retrieves the project id from the environment variable.

    :returns: The Google Cloud Project ID
    :rtype: str
    :raises MissingProjectIdError: When a project id is not set in OS enrionment variables.
    """
    project_id = os.environ['GOOGLE_CLOUD_PROJECT']
    if not project_id:
        raise MissingProjectIdError(
            "Set the environment varialbe " +
            "GOOGLE_CLOUD_PROJECT to your Google Cloud Project ID.")
    return project_id


def custom_metric(metric_type):
    """Generate custom metric name.

    :param metric_type: name of the metric.
    :type metric_type: str
    :returns: Stacdriver Monitoring custome metric name.
    :rtype: str
    """
    return f"custom.googleapis.com/{metric_type}"


def resource_name(metric_type):
    """Generate resource name of metric_type based.
    See details in the official document.
    https://cloud.google.com/monitoring/custom-metrics/creating-metrics?hl=ja#custom_metric_names

    :param metric_type: name of the metric.
    :type metric_type: str
    :returns: Stackdriver Monitoring resource name for metric_type.
    :rtype: str
    """
    project_id = get_project_id()
    custom_type = custom_metric(metric_type)
    return f"projects/{project_id}/metricDescriptors/{custom_type}"


def create_double_guage_metrics(host, metric_name, description):
    """Create guage metrics in Stackdriver Monitoring.
    The value type of it is double.

    :param host: Hostname of running instance.
    :type host: str
    :param metric_name: name of the metric.
    :type metric_name: str
    :param description: description of the metric.
    :type description: str
    """
    client = monitoring_v3.MetricServiceClient()
    project_name = client.project_path(get_project_id())
    descriptor = monitoring_v3.types.MericDescriptor()
    descriptor.type = custom_metric(metric_name)
    descriptor.metric_kind = (
        monitoring_v3.enums.MetricDescriptor.MetricKind.GAUGE)
    descriptor.value_type = (
        monitoring_v3.enums.MetricDescriptor.ValueType.DOUBLE)
    descriptor.description = description
    descriptor = client.create_metric_descriptor(project_name, descriptor)


def main():
    hostname = socket.gethostname()
    t_descriptor = create_double_guage_metrics(
        hostname, 'temperature', "air temperature")
    p_descriptor = create_double_guage_metrics(
        hostname, 'pressure', "barometric pressure")
    h_descriptor = create_double_guage_metrics(
        hostname, 'humidity', "air humidity")
    r_descriptor = create_double_guage_metrics(
        hostname, 'gas_resistance', "indicator of air quality")
    gi_descriptor = create_double_guage_metrics(
        hostname, 'gas_index', "")
    mi_descriptor = create_double_guage_metrics(
        hostname, 'meas_index', "")
    hs_descriptor = create_double_guage_metrics(
        hostname, 'heat_stable', "")
    
    try:
        sensor = bme680.BME680(bme680.I2C_ADDR_PRIMARY)
    except IOError:
        sensor = bme680.BME680(bme680.I2C_ADDR_SECONDARY)
    init_sensor(sensor)
    try:
        counter = 1
        while True:
            if counter == 0:
                # TODO(ymotongpoo): create TimeSeries for all descriptors.
                pass

            if sensor.get_sensor_data():

                data = {
                    'host': socket.gethostname(),
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