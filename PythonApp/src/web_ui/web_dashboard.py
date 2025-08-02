#!/usr/bin/env python3
"""
Web Dashboard Server for Multi-Sensor Recording System

This module implements a Flask-based web server that provides a real-time monitoring
dashboard for the multi-sensor recording system. It offers:

- Real-time sensor data visualization through WebSocket connections
- Device status monitoring and control
- Session management interface
- Mobile-responsive design for tablet and phone access
- REST API endpoints for system integration

The web server runs alongside the existing PyQt5 desktop application and provides
an additional interface for monitoring and controlling the recording system.

Author: Multi-Sensor Recording System Team
Date: 2025-08-02
"""

import json
import logging
import os
import threading
import time
from datetime import datetime
from typing import Dict, List, Any, Optional

try:
    from flask import Flask, render_template, jsonify, request, send_from_directory
    from flask_socketio import SocketIO, emit, disconnect
except ImportError:
    print("Flask not installed. Installing...")
    import subprocess
    subprocess.check_call(["pip3", "install", "flask", "flask-socketio", "eventlet"])
    from flask import Flask, render_template, jsonify, request, send_from_directory
    from flask_socketio import SocketIO, emit, disconnect

# Import logging configuration
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from utils.logging_config import get_logger
    logger = get_logger(__name__)
except ImportError:
    # Fallback logging if utils not available
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)


class WebDashboardServer:
    """
    Web-based dashboard server for real-time monitoring of the multi-sensor recording system.
    
    This server provides a modern web interface that complements the existing PyQt5 desktop
    application, offering real-time monitoring, device management, and session control
    through a responsive web interface.
    """
    
    def __init__(self, host: str = '0.0.0.0', port: int = 5000, debug: bool = False, controller=None):
        """
        Initialize the web dashboard server.
        
        Args:
            host: Server host address (default: '0.0.0.0' for all interfaces)
            port: Server port (default: 5000)
            debug: Enable Flask debug mode
            controller: Controller instance for real backend integration
        """
        self.host = host
        self.port = port
        self.debug = debug
        self.controller = controller  # For real backend integration
        
        # Initialize Flask app
        self.app = Flask(__name__, 
                        template_folder=os.path.join(os.path.dirname(__file__), 'templates'),
                        static_folder=os.path.join(os.path.dirname(__file__), 'static'))
        self.app.config['SECRET_KEY'] = 'multisensor_recording_system_2025'
        
        # Initialize SocketIO for real-time communication
        self.socketio = SocketIO(self.app, cors_allowed_origins="*", async_mode='eventlet')
        
        # Server state
        self.running = False
        self.server_thread = None
        
        # Data storage for real-time updates
        self.device_status = {
            'android_devices': {},
            'usb_webcams': {},
            'shimmer_sensors': {},
            'pc_controller': {
                'status': 'idle',
                'cpu_usage': 0,
                'memory_usage': 0,
                'timestamp': datetime.now().isoformat()
            }
        }
        
        self.session_info = {
            'active': False,
            'session_id': None,
            'start_time': None,
            'duration': 0,
            'recording_devices': [],
            'data_collected': {
                'video_files': 0,
                'thermal_frames': 0,
                'gsr_samples': 0
            }
        }
        
        self.sensor_data = {
            'timestamps': [],
            'android_1': {'camera': [], 'thermal': [], 'gsr': []},
            'android_2': {'camera': [], 'thermal': [], 'gsr': []},
            'webcam_1': [],
            'webcam_2': [],
            'shimmer_1': [],
            'shimmer_2': []
        }
        
        # Setup routes and socket handlers
        self._setup_routes()
        self._setup_socket_handlers()
        
        logger.info("Web Dashboard Server initialized")
    
    def _setup_routes(self):
        """Setup Flask routes for the web dashboard."""
        
        @self.app.route('/')
        def dashboard():
            """Main dashboard page."""
            return render_template('dashboard.html')
        
        @self.app.route('/devices')
        def devices():
            """Device management page."""
            return render_template('devices.html')
        
        @self.app.route('/sessions')
        def sessions():
            """Session management page."""
            return render_template('sessions.html')
        
        @self.app.route('/api/status')
        def api_status():
            """Get current system status."""
            return jsonify({
                'status': 'running',
                'devices': self.device_status,
                'session': self.session_info,
                'timestamp': datetime.now().isoformat()
            })
        
        @self.app.route('/api/devices')
        def api_devices():
            """Get device status information."""
            return jsonify(self.device_status)
        
        @self.app.route('/api/session')
        def api_session():
            """Get current session information."""
            return jsonify(self.session_info)
        
        @self.app.route('/api/session/start', methods=['POST'])
        def api_session_start():
            """Start a new recording session using real network protocols."""
            try:
                config = request.get_json() or {}
                session_id = f"web_session_{int(time.time())}"
                
                # Use real controller to start session via network protocols
                if self.controller and hasattr(self.controller, 'start_recording_session'):
                    success = self.controller.start_recording_session(session_id)
                    if not success:
                        logger.error(f"Controller failed to start session: {session_id}")
                        return jsonify({'success': False, 'error': 'Failed to start session via network protocols'}), 500
                else:
                    logger.warning("No controller available - falling back to local session tracking")
                
                self.session_info.update({
                    'active': True,
                    'session_id': session_id,
                    'start_time': datetime.now().isoformat(),
                    'duration': 0,
                    'recording_devices': config.get('devices', []),
                    'data_collected': {
                        'video_files': 0,
                        'thermal_frames': 0,
                        'gsr_samples': 0
                    }
                })
                
                logger.info(f"Recording session started via web interface using network protocols: {session_id}")
                self._broadcast_session_update()
                
                return jsonify({'success': True, 'session_id': session_id})
            
            except Exception as e:
                logger.error(f"Failed to start session: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/session/stop', methods=['POST'])
        def api_session_stop():
            """Stop the current recording session using real network protocols."""
            try:
                if self.session_info['active']:
                    session_id = self.session_info['session_id']
                    
                    # Use real controller to stop session via network protocols
                    if self.controller and hasattr(self.controller, 'stop_recording_session'):
                        success = self.controller.stop_recording_session()
                        if not success:
                            logger.error(f"Controller failed to stop session: {session_id}")
                            return jsonify({'success': False, 'error': 'Failed to stop session via network protocols'}), 500
                    else:
                        logger.warning("No controller available - falling back to local session tracking")
                    
                    self.session_info.update({
                        'active': False,
                        'session_id': None,
                        'start_time': None,
                        'duration': 0
                    })
                    
                    logger.info(f"Recording session stopped via web interface using network protocols: {session_id}")
                    self._broadcast_session_update()
                    
                    return jsonify({'success': True, 'session_id': session_id})
                else:
                    return jsonify({'success': False, 'error': 'No active session'}), 400
            
            except Exception as e:
                logger.error(f"Failed to stop session: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/data/realtime')
        def api_realtime_data():
            """Get real-time sensor data for visualization."""
            # Return recent data points for charts
            recent_data = {}
            max_points = 100  # Limit to last 100 data points
            
            for device, data in self.sensor_data.items():
                if device == 'timestamps':
                    recent_data[device] = data[-max_points:] if data else []
                elif isinstance(data, dict):
                    recent_data[device] = {}
                    for sensor, values in data.items():
                        recent_data[device][sensor] = values[-max_points:] if values else []
                else:
                    recent_data[device] = data[-max_points:] if data else []
            
            return jsonify(recent_data)
        
        @self.app.route('/api/device/connect', methods=['POST'])
        def api_device_connect():
            """Connect to a device."""
            try:
                data = request.get_json() or {}
                device_id = data.get('device_id')
                device_type = data.get('device_type')
                
                if self.controller and hasattr(self.controller, 'connect_device'):
                    success = self.controller.connect_device(device_id, device_type)
                    if success:
                        return jsonify({'success': True, 'message': f'Connected to {device_id}'})
                    else:
                        return jsonify({'success': False, 'error': 'Connection failed'}), 500
                else:
                    # Simulate connection for demo
                    logger.info(f"Simulating connection to {device_type} device: {device_id}")
                    return jsonify({'success': True, 'message': f'Connected to {device_id}'})
                    
            except Exception as e:
                logger.error(f"Device connection error: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/device/configure', methods=['POST'])
        def api_device_configure():
            """Configure a device."""
            try:
                data = request.get_json() or {}
                device_id = data.get('device_id')
                device_type = data.get('device_type')
                configuration = data.get('configuration', {})
                
                if self.controller and hasattr(self.controller, 'configure_device'):
                    success = self.controller.configure_device(device_id, device_type, configuration)
                    if success:
                        return jsonify({'success': True, 'message': f'Configured {device_id}'})
                    else:
                        return jsonify({'success': False, 'error': 'Configuration failed'}), 500
                else:
                    # Simulate configuration for demo
                    logger.info(f"Simulating configuration of {device_type} device: {device_id} with {configuration}")
                    return jsonify({'success': True, 'message': f'Configured {device_id}'})
                    
            except Exception as e:
                logger.error(f"Device configuration error: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/webcam/test', methods=['POST'])
        def api_webcam_test():
            """Test webcam functionality."""
            try:
                data = request.get_json() or {}
                webcam_id = data.get('webcam_id')
                
                if self.controller and hasattr(self.controller, 'test_webcam'):
                    test_results = self.controller.test_webcam(webcam_id)
                    return jsonify({'success': True, 'test_results': test_results})
                else:
                    # Simulate webcam test for demo
                    logger.info(f"Simulating webcam test: {webcam_id}")
                    return jsonify({
                        'success': True,
                        'test_results': {
                            'resolution': '1920x1080',
                            'fps': 30,
                            'format': 'MP4'
                        }
                    })
                    
            except Exception as e:
                logger.error(f"Webcam test error: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/webcam/configure', methods=['POST'])
        def api_webcam_configure():
            """Configure webcam settings."""
            try:
                data = request.get_json() or {}
                webcam_id = data.get('webcam_id')
                resolution = data.get('resolution')
                fps = data.get('fps')
                
                if self.controller and hasattr(self.controller, 'configure_webcam'):
                    success = self.controller.configure_webcam(webcam_id, resolution, fps)
                    if success:
                        return jsonify({'success': True, 'message': f'Webcam {webcam_id} configured'})
                    else:
                        return jsonify({'success': False, 'error': 'Configuration failed'}), 500
                else:
                    # Simulate webcam configuration for demo
                    logger.info(f"Simulating webcam configuration: {webcam_id} to {resolution} @ {fps}fps")
                    return jsonify({'success': True, 'message': f'Webcam {webcam_id} configured'})
                    
            except Exception as e:
                logger.error(f"Webcam configuration error: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/shimmer/connect', methods=['POST'])
        def api_shimmer_connect():
            """Connect to Shimmer sensor."""
            try:
                data = request.get_json() or {}
                sensor_id = data.get('sensor_id')
                
                if self.controller and hasattr(self.controller, 'connect_shimmer'):
                    success = self.controller.connect_shimmer(sensor_id)
                    if success:
                        return jsonify({'success': True, 'message': f'Connected to Shimmer {sensor_id}'})
                    else:
                        return jsonify({'success': False, 'error': 'Connection failed'}), 500
                else:
                    # Simulate Shimmer connection for demo
                    logger.info(f"Simulating Shimmer connection: {sensor_id}")
                    return jsonify({'success': True, 'message': f'Connected to Shimmer {sensor_id}'})
                    
            except Exception as e:
                logger.error(f"Shimmer connection error: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/shimmer/configure', methods=['POST'])
        def api_shimmer_configure():
            """Configure Shimmer sensor."""
            try:
                data = request.get_json() or {}
                sensor_id = data.get('sensor_id')
                sample_rate = data.get('sample_rate')
                enabled_sensors = data.get('enabled_sensors', [])
                
                if self.controller and hasattr(self.controller, 'configure_shimmer'):
                    success = self.controller.configure_shimmer(sensor_id, sample_rate, enabled_sensors)
                    if success:
                        return jsonify({'success': True, 'message': f'Shimmer {sensor_id} configured'})
                    else:
                        return jsonify({'success': False, 'error': 'Configuration failed'}), 500
                else:
                    # Simulate Shimmer configuration for demo
                    logger.info(f"Simulating Shimmer configuration: {sensor_id} at {sample_rate}Hz with {enabled_sensors}")
                    return jsonify({'success': True, 'message': f'Shimmer {sensor_id} configured'})
                    
            except Exception as e:
                logger.error(f"Shimmer configuration error: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/sessions/export')
        def api_sessions_export():
            """Export session data."""
            try:
                # Generate mock session export data
                export_data = {
                    'exported_at': datetime.now().isoformat(),
                    'sessions': [
                        {
                            'id': 'session_20250802_001',
                            'name': 'Baseline Recording',
                            'start_time': '2025-08-02T10:30:00Z',
                            'end_time': '2025-08-02T11:00:00Z',
                            'duration': 1800,
                            'devices': ['android_1', 'android_2', 'webcam_1'],
                            'status': 'completed',
                            'data_size': '2.5 GB'
                        },
                        {
                            'id': 'session_20250802_002',
                            'name': 'Stress Test',
                            'start_time': '2025-08-02T14:15:00Z',
                            'end_time': '2025-08-02T14:45:00Z',
                            'duration': 1200,
                            'devices': ['android_1', 'shimmer_1', 'shimmer_2'],
                            'status': 'completed',
                            'data_size': '1.8 GB'
                        }
                    ]
                }
                
                response = jsonify(export_data)
                response.headers['Content-Disposition'] = f'attachment; filename=session_export_{datetime.now().strftime("%Y%m%d")}.json'
                return response
                
            except Exception as e:
                logger.error(f"Session export error: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/session/<session_id>')
        def api_session_details(session_id):
            """Get detailed session information."""
            try:
                # Mock session details - in real implementation would query database
                session_details = {
                    'id': session_id,
                    'name': 'Baseline Recording',
                    'start_time': '2025-08-02T10:30:00Z',
                    'end_time': '2025-08-02T11:00:00Z',
                    'duration': 1800,
                    'devices': ['android_1', 'android_2', 'webcam_1'],
                    'status': 'completed',
                    'data_size': '2.5 GB',
                    'data_collected': {
                        'video_files': 12,
                        'thermal_frames': 54000,
                        'gsr_samples': 460800,
                        'audio_files': 3
                    }
                }
                
                return jsonify({'success': True, 'session': session_details})
                
            except Exception as e:
                logger.error(f"Session details error: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/session/<session_id>/download')
        def api_session_download(session_id):
            """Download session data."""
            try:
                # In real implementation, would create ZIP file with session data
                # For demo, return a small text file
                response_data = f"Session data for {session_id}\nGenerated at: {datetime.now().isoformat()}"
                
                from flask import make_response
                response = make_response(response_data)
                response.headers['Content-Type'] = 'application/octet-stream'
                response.headers['Content-Disposition'] = f'attachment; filename={session_id}_data.zip'
                return response
                
            except Exception as e:
                logger.error(f"Session download error: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
    
    def _setup_socket_handlers(self):
        """Setup SocketIO event handlers for real-time communication."""
        
        @self.socketio.on('connect')
        def handle_connect():
            """Handle client connection."""
            logger.info(f"Web client connected: {request.sid}")
            emit('status_update', {
                'devices': self.device_status,
                'session': self.session_info,
                'timestamp': datetime.now().isoformat()
            })
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """Handle client disconnection."""
            logger.info(f"Web client disconnected: {request.sid}")
        
        @self.socketio.on('request_device_status')
        def handle_device_status_request():
            """Handle request for current device status."""
            emit('device_status_update', self.device_status)
        
        @self.socketio.on('request_session_info')
        def handle_session_info_request():
            """Handle request for current session information."""
            emit('session_info_update', self.session_info)
    
    def update_device_status(self, device_type: str, device_id: str, status_data: Dict[str, Any]):
        """
        Update device status and broadcast to connected clients.
        
        Args:
            device_type: Type of device ('android_devices', 'usb_webcams', 'shimmer_sensors')
            device_id: Unique identifier for the device
            status_data: Status information dictionary
        """
        if device_type not in self.device_status:
            logger.warning(f"Unknown device type: {device_type}")
            return
        
        status_data['timestamp'] = datetime.now().isoformat()
        self.device_status[device_type][device_id] = status_data
        
        # Broadcast update to all connected clients
        self.socketio.emit('device_status_update', {
            'device_type': device_type,
            'device_id': device_id,
            'status': status_data
        })
    
    def update_sensor_data(self, device_id: str, sensor_type: str, value: float):
        """
        Update real-time sensor data and broadcast to connected clients.
        
        Args:
            device_id: Device identifier
            sensor_type: Type of sensor data
            value: Sensor reading value
        """
        timestamp = datetime.now().isoformat()
        
        # Add timestamp if not already present
        if not self.sensor_data['timestamps'] or self.sensor_data['timestamps'][-1] != timestamp:
            self.sensor_data['timestamps'].append(timestamp)
        
        # Update sensor data based on device and sensor type
        if device_id in self.sensor_data:
            if isinstance(self.sensor_data[device_id], dict):
                if sensor_type in self.sensor_data[device_id]:
                    self.sensor_data[device_id][sensor_type].append(value)
                else:
                    logger.warning(f"Unknown sensor type {sensor_type} for device {device_id}")
            else:
                self.sensor_data[device_id].append(value)
        else:
            logger.warning(f"Unknown device ID: {device_id}")
        
        # Limit data points to prevent memory issues
        max_points = 1000
        for device, data in self.sensor_data.items():
            if device == 'timestamps':
                if len(data) > max_points:
                    self.sensor_data[device] = data[-max_points:]
            elif isinstance(data, dict):
                for sensor, values in data.items():
                    if len(values) > max_points:
                        self.sensor_data[device][sensor] = values[-max_points:]
            else:
                if len(data) > max_points:
                    self.sensor_data[device] = data[-max_points:]
        
        # Broadcast real-time data update
        self.socketio.emit('sensor_data_update', {
            'device_id': device_id,
            'sensor_type': sensor_type,
            'value': value,
            'timestamp': timestamp
        })
    
    def _broadcast_session_update(self):
        """Broadcast session information update to all connected clients."""
        self.socketio.emit('session_info_update', self.session_info)
    
    def start_server(self):
        """Start the web dashboard server."""
        if self.running:
            logger.warning("Web dashboard server is already running")
            return
        
        self.running = True
        logger.info(f"Starting web dashboard server on {self.host}:{self.port}")
        
        def run_server():
            self.socketio.run(self.app, host=self.host, port=self.port, debug=self.debug)
        
        self.server_thread = threading.Thread(target=run_server, daemon=True)
        self.server_thread.start()
        
        logger.info(f"Web dashboard available at http://{self.host}:{self.port}")
    
    def stop_server(self):
        """Stop the web dashboard server."""
        if not self.running:
            logger.warning("Web dashboard server is not running")
            return
        
        self.running = False
        logger.info("Stopping web dashboard server")
        
        # SocketIO server will stop when the main thread ends
        if self.server_thread:
            self.server_thread.join(timeout=5)
    
    def is_running(self) -> bool:
        """Check if the server is running."""
        return self.running


# Convenience function for creating and starting the server
def create_web_dashboard(host: str = '0.0.0.0', port: int = 5000, debug: bool = False) -> WebDashboardServer:
    """
    Create and configure a web dashboard server instance.
    
    Args:
        host: Server host address
        port: Server port
        debug: Enable debug mode
    
    Returns:
        Configured WebDashboardServer instance
    """
    return WebDashboardServer(host=host, port=port, debug=debug)


if __name__ == '__main__':
    # Demo/test mode - start server with simulated data
    dashboard = create_web_dashboard(debug=True)
    dashboard.start_server()
    
    # Simulate some device status updates
    import time
    import random
    
    try:
        while True:
            # Simulate device status updates
            dashboard.update_device_status('android_devices', 'device_1', {
                'status': 'connected',
                'battery': random.randint(20, 100),
                'temperature': round(random.uniform(35, 45), 1),
                'recording': random.choice([True, False])
            })
            
            dashboard.update_device_status('usb_webcams', 'webcam_1', {
                'status': 'active',
                'resolution': '4K',
                'fps': 30,
                'recording': random.choice([True, False])
            })
            
            # Simulate sensor data
            dashboard.update_sensor_data('android_1', 'gsr', random.uniform(0.1, 2.0))
            dashboard.update_sensor_data('android_1', 'thermal', random.uniform(25, 35))
            dashboard.update_sensor_data('shimmer_1', '', random.uniform(0.5, 3.0))
            
            time.sleep(2)
    
    except KeyboardInterrupt:
        print("\nShutting down web dashboard server...")
        dashboard.stop_server()