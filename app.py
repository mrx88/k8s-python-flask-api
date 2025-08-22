#!/usr/bin/env python
"""Flask Python API example"""

import os
from flask import Flask, jsonify

app = Flask(__name__)

# Configure app based on environment
app.config['DEBUG'] = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
app.config['ENV'] = os.environ.get('FLASK_ENV', 'production')


@app.route('/')
def success_message():
    """Endpoint / for success message"""
    return jsonify({'message': 'Success!', 'status': 'ok'})


@app.route('/ping')
def ok_message():
    """Endpoint /ping for health check"""
    return jsonify({'message': 'Ok', 'status': 'healthy'})


@app.route('/health')
def health_check():
    """Endpoint /health for Kubernetes health checks"""
    return jsonify({
        'status': 'healthy',
        'service': 'flask-api',
        'version': '1.0.0'
    })


if __name__ == '__main__':
    # Get configuration from environment variables
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = int(os.environ.get('FLASK_PORT', '5000'))
    
    app.run(debug=debug_mode, host=host, port=port)
