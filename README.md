# metrics-collection-monitoring-system
Create a metrics collection and monitoring system in python that captures system metrics, stores them, and provides a way to query and visualize the metrics

## Features

- Metrics Collection
- Data Storage
- API Endpoint
- Alerting Mechanism
- Visualization

## Metrics Collection:

- **CPU Usage**: The system's CPU usage is monitored and collected using `psutil`.
- **Memory Usage**: The system's memory usage is tracked and collected using `psutil`.
- **Disk Usage**: The system's disk usage is observed and collected using `psutil`.
- **Prometheus Metrics**: The metrics are exposed to Prometheus using the `prometheus_client` library on the `/metrics` endpoint.

## Data Storage:

- **Prometheus**: The collected metrics are stored in Prometheus, a time-series database that allows for efficient querying and alerting based on the metrics data.

## API Endpoint:

- **Flask Application**: A Flask web application provides API endpoints for interacting with the collected metrics.
  - **Average Usage Endpoint**: `/avg_usage` - Provides the **average** usage of CPU, memory, or disk over a specified time range.
  - **Metrics Usage Endpoint**: `/metrics_usage` - Returns the **metrics** data points for CPU, memory, or disk over a specified time range.
  - **Alert Endpoint**: `/alert` - Receives alerts from Prometheus Alertmanager via HTTP POST.

## Alerting Mechanism:

- **Prometheus Alertmanager**: Configured to send alerts based on predefined rules when certain thresholds are met.
- **Custom Alerts**: Alerts for high CPU, memory, or disk usage are configured with specific thresholds and sent to Alertmanager.
- **HTTP POST Receiver**: Alerts are received by the Flask application via the `/alert` endpoint.

## Visualization:

- **Grafana**: A visualization tool that can be used to create dashboards for monitoring the collected metrics in real-time.
- **Prometheus Web UI**: Provides a basic visualization and querying interface for the collected metrics.
- **Custom Dashboards**: Dashboards can be created in Grafana to visualize CPU, memory, and disk usage trends over time.

# Setup Guide

- This guide will help you set up the Python metrics collector, Prometheus, Grafana, and Alertmanager using Docker containers.
- Steps to Execute the Shell Script
    1. Find the [setup.sh](https://github.com/shaheen0b111/metrics-collection-monitoring-system/tree/main/setup.sh) in root directory of the repository
    2. Make the shell script executable by running and execute with `sudo`
    ```sh
    chmod +x setup.sh
    ./setup
    ```

# Services Overview
## Metrics Collection
- Metrics Collector: The Python application collects system metrics such as CPU, memory, and disk usage.
    - Metrics Endpoint: Available at http://localhost:8080/metrics.
- Flask Application: Provides API endpoints to fetch metrics and average metrics.
    - API Endpoint: Available at http://localhost:5000/.
## Data Storage
- Prometheus: Stores collected metrics data.
    - Prometheus Server: Accessible at http://localhost:9090/.
## Visualization
- Grafana: Visualizes the metrics data collected by Prometheus.
    - Grafana Dashboard: Accessible at http://localhost:3000/.
    - Default Credentials: Username: admin, Password: admin.
    - Sample [json](https://github.com/shaheen0b111/metrics-collection-monitoring-system/blob/main/config/grafana/default.json) can be referred or imported to setup the dashboard
## Alerting Mechanism
- Alertmanager: Manages alerts sent by Prometheus.
- Alertmanager: Accessible at http://localhost:9093/.