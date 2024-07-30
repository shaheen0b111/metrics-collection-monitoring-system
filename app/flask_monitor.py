from flask import Flask, request, jsonify, render_template
from datetime import datetime, timedelta, timezone
from tzlocal import get_localzone
from prometheus_client import Gauge, start_http_server
import pytz
import psutil, time
import sys,requests
import argparse,threading
import logging

# Set up logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler("server.log"),
                              logging.StreamHandler()])

app = Flask(__name__)


def flask_app():
    logging.info("Starting Flask app")
    app.run(port=5000)

def prometheus_monitor(interval_gap):
    # Define prometheus gauge metrics object 
    gauge_cpu_usage = Gauge("gauge_cpu_usage","System CPU Usage in percent",['type'])
    gauge_memory_usage = Gauge("gauge_mem_usage","System Memory Usage in percent",['type'])
    gauge_disk_usage = Gauge("gauge_disk_usage","System Disk Usage in percent",['type'])
    logging.info("Starting Prometheus server")
    #start prometheus HTTP client on port 8080 that will be serving runtime metrics
    print("Staring Prometheus clinet on 8080 : http://localhost:8080/metrics")
    start_http_server(8080)
    # Infinitely Starts the metrics collection
    while True:
        fetch_metrics(interval_gap,gauge_cpu_usage,gauge_memory_usage,gauge_disk_usage)

#Function that collect metrics
def fetch_metrics(interval_gap,gauge_cpu_usage,gauge_memory_usage,gauge_disk_usage):
    print(f"{datetime.now()} : Fetching Metrics - CPU, Memory, Disk")
    #fetch cpu/mem/disk usage in percentage using psutil
    cpu_usage_percent = psutil.cpu_percent()
    mem_usage_percent =  psutil.virtual_memory().percent
    disk_usage_percent =  psutil.disk_usage('/').percent

    # Set the prometheus gauge object with the metrics value fetched
    gauge_cpu_usage.labels(type='CPU').set(cpu_usage_percent)
    gauge_memory_usage.labels(type='Memory').set(mem_usage_percent)
    gauge_disk_usage.labels(type='Disk').set(disk_usage_percent)
    time.sleep(interval_gap)


# def local_to_utc(local_time):
#     """
#     Convert a local time string to UTC datetime.
    
#     Parameters:
#     - local_time: The local time as a string in ISO 8601 format (e.g., "2024-07-27T15:00:00").
#     Returns:
#     - A datetime object in UTC timezone.
#     """
#     try:
#         # Parse the local time string into a naive datetime object
#         local_time = datetime.fromisoformat(local_time) if type(local_time) is str else local_time

#         # Determine timezone
#         local_tz = get_localzone()
#         print(local_tz)
#         # Localize the naive datetime to the determined local timezone
#         print(local_time)
#         localized_local_time = local_time.replace(tzinfo=local_tz)
#         print(localized_local_time)
#         # Convert the localized time to UTC
#         utc_time = localized_local_time.astimezone(pytz.utc)
#         print(utc_time)
#         return utc_time
#     except ValueError:
#         raise ValueError("Invalid date format. Use ISO 8601 format (e.g., 2024-07-27T15:00:00).")
#     except LookupError:
#         raise ValueError("Unknown timezone. Please provide a valid timezone string.")


# def utc_to_local(utc_time):
#     """
#     Convert a UTC time string to local datetime.
    
#     Parameters:
#     - utc_time_str: The UTC time as a string in ISO 8601 format (e.g., "2024-07-27T15:00:00").
    
#     Returns:
#     - A datetime object in local timezone.
#     """
#     try:
#         print(utc_time)
#         # Assume the time is in UTC, so localize the naive datetime to UTC
#         utc_tz = pytz.utc
#         utc_time = utc_tz.localize(utc_time)
#         print(utc_time)
#         # Get the local timezone
#         local_tz = get_localzone()
#         print(local_tz)
        
#         # Convert the UTC time to local timezone
#         local_time = utc_time.astimezone(local_tz)
#         print(local_time)
        
#         return local_time
#     except ValueError:
#         raise ValueError("Invalid date format. Use ISO 8601 format (e.g., 2024-07-27T15:00:00).")
#     except LookupError:
#         raise ValueError("Unknown timezone. Please provide a valid timezone string.")


# To be called when time_range is given and either of start_time or end_time is given
def calculate_time_range(start_time, end_time, time_range):
    """ Calculate start and end times based on provided parameters and time range. """
    print(start_time,end_time,time_range)
    if end_time and time_range:
        end_time = datetime.fromisoformat(end_time)
        start_time = end_time - timedelta(hours=time_range)
    elif start_time and time_range:
        start_time = datetime.fromisoformat(start_time)
        end_time = start_time + timedelta(hours=time_range)
    elif time_range:
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=time_range)
    
    else:
        raise ValueError("Insufficient parameters provided.")

    return start_time, end_time # datetime object will be return Eg: datetime.datetime(2024, 7, 27, 15, 0)

# Querying to prometheus server on port 9090
def query_prometheus(start_time, end_time, type):
    """ Query Prometheus with required metrics type and return results. """
    prom_url = 'http://localhost:9090/api/v1/query_range'
    
    # Convert datetime objects to Unix timestamps - which default used for querying prometheus
    start_timestamp = int(start_time.timestamp())
    end_timestamp = int(end_time.timestamp())
    
    query = f'avg_over_time(gauge_{type}_usage[1m])'  # Adjust the range interval as needed
    
    response = requests.get(prom_url, params={
        'query': query,
        'start': start_timestamp,
        'end': end_timestamp,
        'step': '60'  # Scrape interval, adjust as necessary
    })
    
    data = response.json()
    
    if data['status'] == 'success':
        results = data['data']['result']
        if results:
            return results[0]['values']  # Assuming there’s at least one result
        else:
            return None
    else:
        raise Exception("Error querying Prometheus API")

@app.route('/')
def index():
    return render_template('index.html')
    
@app.route('/avg_usage', methods=['GET'])
def avg_usage():
    try:
        start_time_str = request.args.get('start')
        end_time_str = request.args.get('end')
        time_range = request.args.get('range', type=int)  # Time range in hours
        resource = request.args.get('resource') # type can be mem/cpu/disk
        #is_utc = request.args.get('utc',default='false') #Expected default to be passed as local
        
        if not resource:
            return jsonify({"error": "Please provide one of the metrics type - mem/cpu/disk"}), 400
        
        if time_range is None and (start_time_str is None or end_time_str is None):
            return jsonify({"error": "Please provide both start and end times or a time range."}), 400


        # Calculate start and end times based on the provided parameters and time range
        if not (start_time_str and end_time_str):       
            start_time, end_time = calculate_time_range(start_time_str, end_time_str, time_range)
        else:
            start_time = datetime.fromisoformat(start_time_str)
            end_time = datetime.fromisoformat(end_time_str)
        
        # if is_utc == "true" and (start_time_str or end_time_str): # start and end which is coming as an input
        #     '''
        #     when start and end time is not given and only time_range is given -> it should not go for utc conversion
        #     '''
        #     print("Doing UTC conversion")
        #     start_time = utc_to_local(start_time)
        #     end_time = utc_to_local(end_time)

        if start_time >= end_time:
            return jsonify({"error": "Start time must be before end time."}), 400

        # Make q query request to Prometheus
        result = query_prometheus(start_time, end_time, resource)

        # if result is empty - the time range is not having data points
        if result is None:
            return jsonify({"error": "No data available for the given time range."}), 404
        
        # Calculate average from Prometheus results
        values = [float(value[1]) for value in result]
        average_value = sum(values) / len(values) if values else 0
        return jsonify({f"average_{resource}_usage": average_value})    


    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/metrics_usage', methods=['GET'])
def metrics_usage():
    try:
        start_time_str = request.args.get('start')
        end_time_str = request.args.get('end')
        time_range = request.args.get('range', type=int)  # Time range in hours
        resource = request.args.get('resource') # type can be mem/cpu/disk
        #is_utc = request.args.get('utc',default='false') #Expected default to be passed as local
        
        if not resource:
            return jsonify({"error": "Please provide one of the metrics type - mem/cpu/disk"}), 400

        if time_range is None and (start_time_str is None or end_time_str is None):
            return jsonify({"error": "Please provide both start and end times or a time range."}), 400


        # Calculate start and end times based on the provided parameters and time range
        if not (start_time_str and end_time_str):       
            start_time, end_time = calculate_time_range(start_time_str, end_time_str, time_range)
        else:
            start_time = datetime.fromisoformat(start_time_str)
            end_time = datetime.fromisoformat(end_time_str)
        
        # if is_utc == "true" and (start_time_str or end_time_str): # start and end which is coming as an input
        #     '''
        #     when start and end time is not given and only time_range is given -> it should not go for utc conversion
        #     '''
        #     print("Doing UTC conversion")
        #     start_time = utc_to_local(start_time)
        #     end_time = utc_to_local(end_time)

        if start_time >= end_time:
            return jsonify({"error": "Start time must be before end time."}), 400

        # Make q query request to Prometheus
        result = query_prometheus(start_time, end_time, resource)

        # if result is empty - the time range is not having data points
        if result is None:
            return jsonify({"error": "No data available for the given time range."}), 404
        
        # return all metrics values fetched
        #values = [{datetime.fromtimestamp(value[0]).strftime('%Y-%m-%d %H:%M:%S'):float(value[1])} if is_utc == "false" else {local_to_utc(datetime.fromtimestamp(value[0])).strftime('%Y-%m-%d %H:%M:%S'):float(value[1])} for value in result]
        values = [{datetime.fromtimestamp(value[0]).strftime('%Y-%m-%d %H:%M:%S'):float(value[1])} for value in result]
        return jsonify({f"{resource}_usage": values})

    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/alert', methods=['POST'])
def receive_alert():
    alert_data = request.json
    print("Received alert:", alert_data)
    # Process the alert as needed
    # For example, you could log it
    with open("alert.log", 'a+') as fp:
        fp.write(str(alert_data))
    return jsonify({"status": "success"}), 200

if __name__ == '__main__':
    # Initialize parser
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--interval", help = "Pass interval time that metrics collction should take", required=True)
    # Read arguments from command line
    args = parser.parse_args()
    interval_gap = int(args.interval) # convert the interval time into int
    prometheus_monitor_thread = threading.Thread(target=prometheus_monitor,args=(interval_gap,))
    flask_app_thread = threading.Thread(target=flask_app)
    
    # Start cpu/memory/disk percentage metrics collection and expose it at port 8080
    prometheus_monitor_thread.start()
    
    # Start the flask app which provide the enpoint at 5000 to query the prometheus back end at 9090
    flask_app_thread.start()