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
    return "custom.googleapis.com/{}".format(metric_type)


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
    return "projects/{}/metricDescriptors/{}".format(project_id, custom_type)


def create_double_guage_metrics(metric_name, description):
    """Create guage metrics in Stackdriver Monitoring.
    The value type of it is double.

    :param metric_name: name of the metric.
    :type metric_name: str
    :param description: description of the metric.
    :type description: str
    :returns: new descriptor just created
    :rtype: 
    """
    client = monitoring_v3.MetricServiceClient()
    project_name = client.project_path(get_project_id())
    descriptor = monitoring_v3.types.MetricDescriptor()
    descriptor.type = custom_metric(metric_name)
    descriptor.metric_kind = (
        monitoring_v3.enums.MetricDescriptor.MetricKind.GAUGE)
    descriptor.value_type = (
        monitoring_v3.enums.MetricDescriptor.ValueType.DOUBLE)
    descriptor.description = description
    descriptor = client.create_metric_descriptor(project_name, descriptor)
    return descriptor


def create_sensor_metrics(metric_dict):
    """Creates metrics in Stackdriver Monitoring based on the contents
    in metric_dict.

    :param metric_dict: dictionary of metric type and its description. 
    :type metric_dict: dict[str, str]
    """
    for mtype, mdesc in metric_dict.items():
        descriptor = create_double_guage_metrics(mtype, mdesc)
        print("Created {}.".format(descriptor.name))


def create_time_series(hostname, metric_dict):
    """Creates TimeSeries data for Stackdriver Monitoring based on 
    the contents in metric_dict.

    :param hostname: hostname of running instance.
    :type hostname: str
    :param metric_dict: dictionary of metric type and its description. 
    :type metric_dict: dict[str, str]
    :returns: dictionary of metric type and time series data.
    :rtype: dict[str, monitoring_v3.types.TimeSeries]
    """
    hostname = socket.gethostname()
    series_dict = {}
    for typ in metric_dict.keys():
        series = monitoring_v3.types.TimeSeries()
        series.resource.type = custom_metric(typ)
        series.resource.labels['hostname'] = hostname
        series_dict[typ] = series

    return series_dict


def main():
    metric_dict = {
        'temperature': "air temperature",
        'pressure': "barometric pressure",
        'humidity': "air humidity",
        'gas_resistance': "indicator of air quality",
        'gas_index': "",
        'meas_index': "",
        'heat_stable': ""
    }    
    create_sensor_metrics(metric_dict)
    
    try:
        sensor = bme680.BME680(bme680.I2C_ADDR_PRIMARY)
    except IOError:
        sensor = bme680.BME680(bme680.I2C_ADDR_SECONDARY)
    init_sensor(sensor)

    hostname = socket.gethostname()
    try:
        counter = 0
        series_dict = {}
        while True:
            if counter == 0:
                series_dict = create_time_series(hostname, metric_dict)

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
                for typ, value in data.items():
                    series = series_dict[typ]
                    point = series.points.add()
                    point.value.double_value = value
                    now = time.time()
                    point.interval.end_time.seconds = int(now)
                    point.interval.end_time.nano = int(
                        (now - point.interval.end_time.seconds) * 10**9)
                counter += 1

            if counter == 20:
                client = monitoring_v3.MetricServiceClient()
                project_name = client.project_path(get_project_id())
                for series in series_dict.values():
                    client.create_time_series(project_name, [series])
                counter = 0
            time.sleep(1)

    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()