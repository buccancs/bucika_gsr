# Web-based Real-time Monitoring Dashboard

## Overview

The Multi-Sensor Recording System now includes a modern web-based dashboard that complements the existing PyQt5 desktop application. This web interface provides real-time monitoring, device management, and session control capabilities accessible from any device with a web browser.

## Features

### 🌐 **Cross-Platform Accessibility**
- Access from any device (desktop, tablet, smartphone)
- Responsive design that adapts to different screen sizes
- No additional software installation required

### 📊 **Real-time Monitoring**
- Live sensor data visualization with interactive charts
- Real-time device status updates
- WebSocket-based communication for instant updates
- Animated status indicators with visual feedback

### 🎛️ **Device Management**
- Monitor Android devices, USB webcams, and Shimmer sensors
- View detailed device information and capabilities
- Device connection status and configuration options
- System resource monitoring (CPU, memory, disk usage)

### 📝 **Session Management**
- Start and stop recording sessions from the web interface
- View current session progress and statistics
- Session history with detailed information
- Data collection metrics and file management

### 🎨 **Modern User Interface**
- Clean, professional design inspired by modern dashboard applications
- Bootstrap-based responsive layout
- Font Awesome icons for clear visual communication
- Color-coded status indicators and animations

## Architecture

### Components

1. **Web Dashboard Server** (`web_dashboard.py`)
   - Flask-based web server with SocketIO for real-time communication
   - RESTful API endpoints for device and session management
   - WebSocket handlers for live data streaming

2. **Integration Layer** (`integration.py`)
   - Bridge between web dashboard and existing desktop application
   - Device status synchronization
   - Real-time data broadcasting

3. **Web Templates**
   - `dashboard.html` - Main monitoring interface
   - `devices.html` - Device management page
   - `sessions.html` - Session history and management

4. **Standalone Launcher** (`web_launcher.py`)
   - Independent web server launcher
   - Command-line configuration options
   - Demo data generation for testing

## Installation and Setup

### Prerequisites

The web UI requires additional Python packages:

```bash
pip install flask flask-socketio eventlet
```

### Running the Web Dashboard

#### Option 1: Standalone Web Server

```bash
# Basic usage
cd PythonApp/src
python web_launcher.py

# Custom port and host
python web_launcher.py --port 8080 --host 0.0.0.0

# Enable debug mode
python web_launcher.py --debug

# Disable demo data
python web_launcher.py --no-demo-data
```

#### Option 2: Integrated with Desktop Application

```python
from web_ui.integration import WebDashboardIntegration

# Create integration instance
web_integration = WebDashboardIntegration(
    enable_web_ui=True,
    web_port=5000
)

# Start web dashboard
if web_integration.start_web_dashboard():
    print(f"Dashboard available at: {web_integration.get_web_dashboard_url()}")
```

#### Option 3: Enhanced Desktop Application

```bash
cd PythonApp/src
python enhanced_main_with_web.py
```

This runs both the desktop PyQt5 application and the web dashboard simultaneously.

## Usage

### Accessing the Web Interface

Once the server is running, access the dashboard at:
- **Main Dashboard**: `http://localhost:5000/`
- **Device Management**: `http://localhost:5000/devices`
- **Session History**: `http://localhost:5000/sessions`

### Main Dashboard Features

1. **Session Control Panel**
   - Start/stop recording sessions
   - View current session status and duration
   - Monitor active recording devices

2. **System Overview Cards**
   - Device count summaries
   - Connection status indicators
   - System health metrics

3. **Device Status Grids**
   - Android devices with battery and temperature info
   - USB webcams with resolution and frame rate details
   - PC controller system resources

4. **Real-time Data Visualization**
   - GSR sensor data charts with multiple device support
   - Thermal data visualization
   - Live updating charts with smooth animations

### Device Management

- **Android Devices**: Connection status, battery level, temperature monitoring
- **USB Webcams**: Resolution settings, frame rate configuration, recording status
- **Shimmer Sensors**: Bluetooth connectivity, battery status, signal strength
- **PC Controller**: CPU usage, memory consumption, system status

### Session Management

- **Start New Sessions**: Configure devices and recording parameters
- **Monitor Progress**: Real-time session statistics and data collection metrics
- **Session History**: Browse past sessions with detailed information
- **Data Export**: Access recorded data and session logs

## API Endpoints

### Device Status
- `GET /api/status` - Overall system status
- `GET /api/devices` - All device information

### Session Management
- `GET /api/session` - Current session info
- `POST /api/session/start` - Start new recording session
- `POST /api/session/stop` - Stop current session

### Real-time Data
- `GET /api/data/realtime` - Recent sensor data for visualization

## WebSocket Events

### Client to Server
- `connect` - Client connection
- `request_device_status` - Request current device status
- `request_session_info` - Request session information

### Server to Client
- `status_update` - Complete system status update
- `device_status_update` - Individual device status change
- `sensor_data_update` - Real-time sensor data point
- `session_info_update` - Session information change

## Integration with Existing System

The web UI is designed to complement, not replace, the existing PyQt5 desktop application. Integration options include:

### 1. Minimal Integration
Add web dashboard as an optional feature:

```python
from web_ui.integration import get_web_integration

# In your main application
web_integration = get_web_integration(enable_web_ui=True)
web_integration.start_web_dashboard()
```

### 2. Status Synchronization
Keep web dashboard updated with desktop application state:

```python
# Update device status
web_integration.update_device_status('android_devices', 'device_1', {
    'status': 'connected',
    'battery': 85,
    'recording': True
})

# Update session information
web_integration.update_session_info({
    'active': True,
    'session_id': 'session_123',
    'start_time': datetime.now().isoformat()
})

# Send real-time sensor data
web_integration.update_sensor_data('android_1', 'gsr', 1.23)
```

### 3. Menu Integration
Add web dashboard controls to desktop application menus (see `enhanced_main_with_web.py` for example).

## Configuration

### Server Settings
- **Host**: Default `0.0.0.0` (all interfaces)
- **Port**: Default `5000`
- **Debug Mode**: Disabled by default

### Demo Data
The web dashboard includes demo data generation for testing:
- Simulated device status updates
- Real-time sensor data streams
- Mock session information

Disable demo data with `--no-demo-data` flag.

## Security Considerations

- The web server binds to all interfaces (`0.0.0.0`) by default for network access
- Consider firewall rules for production deployments
- HTTPS not implemented - use reverse proxy if needed
- No authentication system - intended for trusted network environments

## Browser Compatibility

The web interface supports modern browsers with:
- Bootstrap 5.3.0 for responsive design
- Font Awesome 6.4.0 for icons
- Chart.js 4.3.0 for data visualization
- Socket.IO 4.7.2 for real-time communication

Tested on:
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Performance

- Real-time updates every 2 seconds
- Chart data limited to last 50 points for performance
- WebSocket connections automatically managed
- Responsive design optimized for mobile devices

## Troubleshooting

### Common Issues

1. **Port already in use**
   ```
   Error: [Errno 98] Address already in use
   ```
   Solution: Use different port with `--port` option

2. **Import errors**
   ```
   ImportError: No module named 'flask'
   ```
   Solution: Install dependencies with `pip install flask flask-socketio eventlet`

3. **Connection refused**
   - Check if server is running
   - Verify port number
   - Check firewall settings

### Debug Mode

Enable debug mode for detailed error information:
```bash
python web_launcher.py --debug
```

### Logs

Check application logs in `PythonApp/logs/` directory for detailed troubleshooting information.

## Development

### Adding New Features

1. **New API Endpoints**: Add routes to `web_dashboard.py`
2. **WebSocket Events**: Add handlers in `_setup_socket_handlers()`
3. **Frontend Features**: Modify HTML templates and JavaScript
4. **Integration**: Update `integration.py` for desktop app connectivity

### Testing

Test the web interface:
```bash
# Start with demo data
python web_launcher.py --debug

# Test API endpoints
curl http://localhost:5000/api/status

# Test WebSocket connection in browser console
var socket = io();
socket.on('connect', () => console.log('Connected'));
```

## Future Enhancements

Planned improvements include:
- User authentication and access control
- Data export functionality
- Advanced visualization options
- Mobile application integration
- Cloud deployment options
- Real-time collaboration features

## Summary

The web-based dashboard provides a modern, accessible interface for monitoring and controlling the Multi-Sensor Recording System. It complements the existing desktop application while offering new capabilities for remote monitoring and cross-platform access.

Key benefits:
- **Accessibility**: Use from any device with a web browser
- **Real-time Updates**: Live data visualization and status monitoring
- **Modern Interface**: Clean, responsive design with professional appearance
- **Easy Integration**: Minimal changes required to existing codebase
- **Standalone Operation**: Can run independently or integrated with desktop app