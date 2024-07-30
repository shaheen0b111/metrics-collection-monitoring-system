#!/bin/sh

## Setup Python metrics collector on port 8080
## Flask app for exposing end-point on port 5000 to fetch the metrics and average metrics
docker run -d --name metrics-monitoring --network host shaheensayyed/metrics-monitor:appV3
echo "\nMetrics collector started at : http://localhost:8080/"
echo "\nFlask app started at : http://localhost:5000/"

## Create persistent volume for prometheus data
docker volume create prometheus-data
chmod -R 777 /var/lib/docker/volumes/prometheus-data

## Run prometheus container with port 9090 on Host
docker run -d --name prometheus --network host -v prometheus-data:/prometheus shaheensayyed/metrics-monitor:prometheusV1
echo "\nPrometheus server started at : http://localhost:9090/"

## Create persistent volume for grafana data
docker volume create grafana-data

## Run grafana container with port 3000 on Host
docker run -d --name grafana --network host -v grafana-data:/var/lib/grafana grafana/grafana-oss:latest
echo "\nGrafana started at : http://localhost:3000/"
echo "\nInitial username/password : admin/admin"

## Run alertmanager container with port 9093 on Host
docker run -d --name alertmanager --network host shaheensayyed/metrics-monitor:alertmanagerV1
echo "\nAlert Manager started at : http://localhost:9093/"
