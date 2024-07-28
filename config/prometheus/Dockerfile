FROM prom/prometheus

USER root
ADD prometheus.yml /etc/prometheus/
RUN chown nobody:nobody /etc/prometheus/prometheus.yml
RUN chmod 554 /etc/prometheus/prometheus.yml
USER nobody 

#the base image - user nobody
## Create persistent volume for your data
#docker volume create prometheus-data
#docker build -t custom_prom:v2 . -> Create a custom image
#docker run -d --network host -v prometheus-data:/prometheus custom_prom:v2 -> Start container with custom image

