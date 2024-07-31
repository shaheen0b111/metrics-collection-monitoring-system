# Makefile for setting up the monitoring stack

# Variables - Docker Image 
DOCKER_IMAGE_METRICS = shaheensayyed/metrics-monitor:appV3
DOCKER_IMAGE_PROMETHEUS = shaheensayyed/metrics-monitor:prometheusV1
DOCKER_IMAGE_GRAFANA = grafana/grafana-oss:latest
DOCKER_IMAGE_ALERTMANAGER = shaheensayyed/metrics-monitor:alertmanagerV1
PYTHON_INTERPRETER = python3

.PHONY: all start-metrics-monitoring start-prometheus start-alertmanager start-grafana clean_all clean_metrics_monitoring clean_prometheus clean_alertmanager clean_alertmanager clean_grafana

all: start-metrics-monitoring start-prometheus start-alertmanager start-grafana

# target that will remove all containers
clean_all: clean_metrics_monitoring clean_prometheus clean_alertmanager clean_alertmanager clean_grafana

# target - remove prometheus container
clean_prometheus:
	@echo "Removing existing containers of prometheus"
	@if [ $(shell docker ps -a -q -f name=prometheus) ]; then docker rm -f prometheus; fi

# target - remove grafana container
clean_grafana:
	@echo "Removing existing containers of grafana"
	@if [ $(shell docker ps -a -q -f name=grafana) ]; then docker rm -f grafana; fi

# target - remove alertmanager container
clean_alertmanager:
	@echo "Removing existing containers of alertmanager"
	@if [ $(shell docker ps -a -q -f name=alertmanager) ]; then docker rm -f alertmanager; fi

# target - remove flask app - metrics-monitoring container
clean_metrics_monitoring:
	@echo "Removing existing containers of flask app"
	@if [ $(shell docker ps -a -q -f name=metrics-monitoring) ]; then docker rm -f metrics-monitoring; fi


# target - start 
start-metrics-monitoring: clean_metrics_monitoring
	@echo "Starting metrics collector and Flask app..."
	docker run -d --name metrics-monitoring --network host $(DOCKER_IMAGE_METRICS)
	@echo "\nMetrics collector started at : http://localhost:8080/"
	@echo "\nFlask app started at : http://localhost:5000/"

# target - start prometheus container
start-prometheus: clean_prometheus create-prometheus-volume
	@echo "Starting Prometheus server..."
	docker run -d --name prometheus --network host -v prometheus-data:/prometheus $(DOCKER_IMAGE_PROMETHEUS)
	@echo "\nPrometheus server started at : http://localhost:9090/"

# target - create volume for prometheus
create-prometheus-volume:
	@echo "Creating persistent volume for Prometheus data..."
	docker volume create prometheus-data
	chmod -R 777 /var/lib/docker/volumes/prometheus-data

# target - start grafana container
start-grafana: clean_grafana create-grafana-volume
	@echo "Starting Grafana server..."
	docker run -d --name grafana --network host -v grafana-data:/var/lib/grafana $(DOCKER_IMAGE_GRAFANA)
	@echo "\nGrafana started at : http://localhost:3000/"
	@echo "\nInitial username/password : admin/admin"

# target - create volume for grafana
create-grafana-volume:
	@echo "Creating persistent volume for Grafana data..."
	docker volume create grafana-data

# target - start alertmanager container
start-alertmanager: clean_alertmanager
	@echo "Starting Alert Manager..."
	docker run -d --name alertmanager --network host $(DOCKER_IMAGE_ALERTMANAGER)
	@echo "\nAlert Manager started at : http://localhost:9093/"

# target - execute unit test
test:
	@echo "Running unit tests..."
	pip3 install --no-cache-dir -r requirements.txt
	$(PYTHON_INTERPRETER) "tests/unit_test.py"