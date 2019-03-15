#!/bin/bash
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

# Installing `smbus` via pip in venv doesn't work well in Raspbian Stretch.
# Using `python3-smbus` here instaed.
python3 -m venv --system-site-packages .venv
.venv/bin/pip install -r requirements.txt -c constraints.txt

# Run main.py
export GOOGLE_APPLICATION_CREDENTIALS="$HOME/credentials.json"
export GOOGLE_CLOUD_PROJECT="yoshifumi-cloud-demo"
.venv/bin/python3 main.py