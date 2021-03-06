# raspi-bme680-stackdriver-monitoring-python
Air quality polling script with BME680

## Prerequisites
### Hardware
* Raspberry Pi
* [BME680](https://shop.pimoroni.com/products/bme680-breakout)

### Software
* Python 3.5+
* `python3-smbus`, `i2c-tools`, `read-edid`, `libi2c-dev` (In the case of Raspbian 9 Stretch)

## References
### BME680
* https://learn.pimoroni.com/tutorial/sandyj/getting-started-with-bme680-breakout
* https://pypi.org/user/pimoroni/
* https://github.com/pimoroni
  * https://github.com/pimoroni/bme680-python
* https://cdn-shop.adafruit.com/product-files/3660/BME680.pdf
  * https://github.com/BoschSensortec/BME680_driver

### Stackdriver Monitoring V3
* https://github.com/GoogleCloudPlatform/python-docs-samples/blob/master/monitoring/api/v3/cloud-client/snippets.py
* https://cloud.google.com/monitoring/api/resources
* https://github.com/googleapis/google-cloud-python/tree/master/monitoring/google/cloud/monitoring_v3/proto
* https://github.com/googleapis/googleapis/tree/master/google/api
