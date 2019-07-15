#
# Copyright 2019 Astronomer Inc.
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

ARG APT_DEPS_IMAGE="airflow-apt-deps"
ARG PYTHON_BASE_IMAGE="python:3.6-slim"
ARG PIP_VERSION="19.0.1"
ARG ORG="astronomer"
ARG VERSION="1.10.3-1"
ARG SUBMODULES="all, statsd, elasticsearch"
ARG ASTRONOMER_USER="astro"
ARG ASTRONOMER_GROUP="astro"


FROM ${PYTHON_BASE_IMAGE} as airflow-apt-deps

LABEL maintainer="Astronomer <humans@astronomer.io>"

ARG BUILD_NUMBER=-1
LABEL io.astronomer.docker.build.number=$BUILD_NUMBER
LABEL io.astronomer.docker=true
LABEL io.astronomer.docker.module="airflow"
LABEL io.astronomer.docker.component="airflow"
LABEL io.astronomer.docker.airflow.version="1.10.3"


ENV AIRFLOW_REPOSITORY="https://github.com/astronomer/airflow"
ENV AIRFLOW_MODULE="git+https://github.com/astronomer/airflow@1.10.3-1#egg=apache-airflow[all, statsd, elasticsearch]"
ENV AIRFLOW_HOME="/usr/local/airflow"
ENV PYMSSQL_BUILD_WITH_BUNDLED_FREETDS=1
ENV PYTHONPATH=${PYTHONPATH:+${PYTHONPATH}:}${AIRFLOW_HOME}
ENV AIRFLOW_GPL_UNIDECODE="True"
ENV PIP_VERSION=${PIP_VERSION}

# Optimizing installation of Cassandra driver
# Speeds up building the image - cassandra driver without CYTHON saves around 10 minutes
ARG CASS_DRIVER_NO_CYTHON="1"
# Build cassandra driver on multiple CPUs
ARG CASS_DRIVER_BUILD_CONCURRENCY="8"

ENV CASS_DRIVER_BUILD_CONCURRENCY=${CASS_DRIVER_BUILD_CONCURRENCY}
ENV CASS_DRIVER_NO_CYTHON=${CASS_DRIVER_NO_CYTHON}

ENV ASTRONOMER_USER=${ASTRONOMER_USER}
ENV ASTRONOMER_GROUP=${ASTRONOMER_GROUP}


# Need to repeat the empty argument here otherwise it will not be set for this stage
# But the default value carries from the one set before FROM
ARG PYTHON_BASE_IMAGE
ENV PYTHON_BASE_IMAGE=${PYTHON_BASE_IMAGE}
# Print versions
RUN echo "Base image: ${PYTHON_BASE_IMAGE}"
RUN echo "Airflow version: ${AIRFLOW_VERSION}"

# Make sure noninteractie debian install is used and language variables set
ENV DEBIAN_FRONTEND=noninteractive LANGUAGE=C.UTF-8 LANG=C.UTF-8 LC_ALL=C.UTF-8 \
    LC_CTYPE=C.UTF-8 LC_MESSAGES=C.UTF-8

# By increasing this number we can do force build of all dependencies
ARG DEPENDENCIES_EPOCH_NUMBER="1"
# Increase the value below to force renstalling of all dependencies
ENV DEPENDENCIES_EPOCH_NUMBER=${DEPENDENCIES_EPOCH_NUMBER}


# Install curl and gnupg2 - needed to download nodejs in the next step
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
           curl gnupg2 \
    && apt-get autoremove -yqq --purge \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*




# Install basic apt dependencies
RUN curl -sL https://deb.nodesource.com/setup_10.x | bash - \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
           # Packages to install \
           libsasl2-dev \
           freetds-bin \
           build-essential \
           sasl2-bin \
           libsasl2-2 \
           libsasl2-dev \
           libsasl2-modules \
           default-libmysqlclient-dev \
           apt-utils \
           curl \
           rsync \
           netcat \
           locales  \
           freetds-dev \
           libkrb5-dev \
           libssl-dev \
           libffi-dev \
           libpq-dev \
           git \
           nodejs \
           nodejs npm \
           gosu \
           sudo \
           dumb-init \
    && apt-get autoremove -yqq --purge \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*


RUN pip install --upgrade pip==19.0.1

RUN useradd --uid 1000 astro

COPY include/sudoers /etc/sudoers.d/astro
RUN visudo --check --file=/etc/sudoers.d/astro

# From the airflow image on master

#######################################################
######## Installed dependencies - now installing Airflow
#######################################################

FROM ${APT_DEPS_IMAGE} as main
SHELL ["/bin/bash", "-o", "pipefail", "-e", "-u", "-x", "-c"]

# Pip install airflow and astro security manager
RUN pip install --no-cache-dir --no-use-pep517 "${AIRFLOW_MODULE}" \
  && pip install --no-cache-dir "https://github.com/astronomer/astronomer-fab-securitymanager/releases/download/v1.0.2/astronomer_fab_security_manager-1.0.2-py3-none-any.whl"


####################
# Installing node node_modules
###############

## move this to same layer as airflow because its from tag.

FROM main


# Install scripts
RUN cd usr/local/lib/python3.6/site-packages/airflow/www_rbac \
  && npm install \
  && npm run build \
  && rm -rf node_modules \
  && ln -sf /usr/bin/python3 /usr/bin/python \
  && ln -sf /usr/bin/pip3 /usr/bin/pip

RUN apt-get update \
    && apt-get upgrade -y --no-install-recommends \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*



# Additional python deps to install
ARG ADDITIONAL_PYTHON_DEPS=""


# Create logs directory so we can own it when we mount volumes
RUN install --directory --owner=astro "${AIRFLOW_HOME}" \
    && install --directory --owner=astro "${AIRFLOW_HOME}/logs"

# Copy entrypoint to root
COPY include/entrypoint /

# Though this is set here we currently override this in the helm template, so
# this _might_ not have any effect once deployed. The /entrypoint script copes
# with this
USER astro

# Switch to AIRFLOW_HOME
WORKDIR ${AIRFLOW_HOME}

ENTRYPOINT ["/usr/bin/dumb-init", "--", "/entrypoint"]
CMD ["airflow", "--help"]
