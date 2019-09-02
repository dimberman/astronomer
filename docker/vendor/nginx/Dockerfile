#
# Copyright 2018 Astronomer Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

FROM quay.io/kubernetes-ingress-controller/nginx-ingress-controller:0.25.1
LABEL maintainer="Astronomer <humans@astronomer.io>"

ARG BUILD_NUMBER=-1
LABEL io.astronomer.docker=true
LABEL io.astronomer.docker.build.number=$BUILD_NUMBER

USER root
RUN apt-get update \
    && apt-get install -y build-essential \
    && curl -L https://github.com/nghttp2/nghttp2/releases/download/v1.39.2/nghttp2-1.39.2.tar.gz --output nghttp2-1.39.2.tar.gz \
    && tar xf nghttp2-1.39.2.tar.gz \
    && cd nghttp2-1.39.2 \
    && ./configure \
    && make install
RUN apt-get update && apt-get dist-upgrade -y && apt-get clean && apt-get autoremove -y && apt-get --purge remove -y gdb libnghttp2-14
# respect original Dockerfile https://github.com/kubernetes/ingress-nginx/blob/master/rootfs/Dockerfile
USER www-data
