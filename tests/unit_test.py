import unittest
from flask import Flask, request, jsonify, render_template
from datetime import datetime, timedelta, timezone
from tzlocal import get_localzone
from prometheus_client import Gauge, start_http_server
import pytz
import psutil, time
import sys, requests, os
import argparse, threading
import logging

# Add the parent directory of 'app' 
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.flask_monitor import app, query_prometheus, calculate_time_range, fetch_metrics

# Inherit the TestCase as base class from unitest framework
class FlaskAppTests(unittest.TestCase):
    '''
    setUp: This method is called before each test method to set up any state that is shared across tests.
    '''
    def setUp(self):
        # Create a test client using the Flask application configured for testing
        self.app = app.test_client()
        self.app.testing = True
    
    #setUp: This method is called before each test method to set up any state that is shared across tests.
    
    # Test Cases for `/avg_usage`
    # Tests the /avg_usage endpoint without the `resource` parameter
    def test_avg_usage_missing_resource(self):
        response = self.app.get('/avg_usage')
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"Please provide one of the metrics type - mem/cpu/disk", response.data)
    
    # Tests the /avg_usage endpoint without `start`, `end`, or `range` parameters
    def test_avg_usage_missing_time_parameters(self):
        response = self.app.get('/avg_usage?resource=mem')
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"Please provide both start and end times or a time range.", response.data)
    
    # Tests the /avg_usage endpoint with an invalid time range
    def test_avg_usage_invalid_time_range(self):
        response = self.app.get('/avg_usage?resource=mem&start=2024-07-30T14:00:00&end=2024-07-29T15:00:00')
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"Start time must be before end time.", response.data)
    
    # Tests the /avg_usage endpoint with valid parameters
    def test_avg_usage_success(self):
        response = self.app.get('/avg_usage?resource=mem&range=1')
        self.assertEqual(response.status_code, 200)
    
    # Test Cases for `/metrics_usage`
    # Tests the /metrics_usage endpoint without the `resource` parameter
    def test_metrics_usage_missing_resource(self):
        response = self.app.get('/metrics_usage')
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"Please provide one of the metrics type - mem/cpu/disk", response.data)
    
    #  Tests the /metrics_usage endpoint without `start`, `end`, or `range` parameters
    def test_metrics_usage_missing_time_parameters(self):
        response = self.app.get('/metrics_usage?resource=mem')
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"Please provide both start and end times or a time range.", response.data)

    # Tests the /metrics_usage endpoint with an invalid time range
    def test_metrics_usage_invalid_time_range(self):
        response = self.app.get('/metrics_usage?resource=mem&start=2024-07-30T14:00:00&end=2024-07-29T15:00:00')
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"Start time must be before end time.", response.data)
    
    # Tests the /metrics_usage endpoint with valid parameters
    def test_metrics_usage_success(self):
        response = self.app.get('/metrics_usage?resource=mem&range=1')
        self.assertEqual(response.status_code, 200)
    
    # Tests the /alert endpoint to ensure it handles POST requests correctly
    def test_alert(self):
        response = self.app.post('/alert', json={"alert": "test"})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"status", response.data)
        
    # Test fetch_metrics
    def test_fetch_metrics(self):
        # Define prometheus gauge metrics object 
        gauge_cpu_usage = Gauge("gauge_cpu_usage","System CPU Usage in percent",['type'])
        gauge_memory_usage = Gauge("gauge_mem_usage","System Memory Usage in percent",['type'])
        gauge_disk_usage = Gauge("gauge_disk_usage","System Disk Usage in percent",['type'])
        fetch_metrics(1,gauge_cpu_usage,gauge_memory_usage,gauge_disk_usage)
        
    # Test Calculation range when time_range is provided
    def test_calculate_time_range(self):
        # when only time_range is only provided
        start_time, end_time = calculate_time_range(None, None, 1)
        self.assertTrue(start_time < end_time)
        # when start and time_range is provided
        start_time, end_time = calculate_time_range('2024-07-29T15:00:00', None, 1)
        self.assertTrue(start_time < end_time)
        # when end and time_range is provided
        start_time, end_time = calculate_time_range(None, '2024-07-29T15:00:00', 1)
        self.assertTrue(start_time < end_time)
        
if __name__ == '__main__':
    unittest.main()
