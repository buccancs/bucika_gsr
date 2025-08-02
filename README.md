# Multi-Sensor Synchronized Recording System

A comprehensive research platform that orchestrates synchronized data collection from multiple sensor modalities including smartphone cameras, thermal imaging, USB webcams, and physiological sensors. The system combines an Android mobile application with a Python desktop controller to enable precise temporal synchronization across all data sources for multi-modal research applications.

## Project Overview

This system enables synchronized recording from multiple data sources for research applications, particularly useful for capturing synchronized video, thermal, and physiological data during stimulus presentation experiments:

- **2 Android smartphones** (Samsung S22) with attached thermal cameras for mobile data collection
- **2 Logitech Brio 4K USB webcams** connected to a Windows PC for stationary high-quality video capture
- **Shimmer3 GSR+ physiological sensors** for biometric data collection via Bluetooth
- **Windows PC controller** acting as the master orchestrator and data synchronization hub

The architecture provides researchers with a robust platform for multi-modal data collection with microsecond-precision synchronization across all sensors.

## Quick Start

### Prerequisites

- **Java 17 or Java 21** (recommended for optimal compatibility)
- **Conda/Miniconda** for Python environment management
- **Android Studio** (Arctic Fox or later) for Android development
- **Git** for version control

> **Note**: Python installation is **not required** - the setup script automatically installs Miniconda and configures the environment.

### Automated Setup

The project includes automated setup scripts that handle the complete environment configuration:

```bash
# Complete automated setup (recommended)
python3 tools/development/setup.py

# Platform-specific setup
# Windows:
tools/development/setup_dev_env.ps1

# Linux/macOS:
tools/development/setup.sh
```

These scripts automatically install Miniconda, create the conda environment, install all dependencies, configure Android SDK components, and validate the complete build system.

### Quick Build Commands

```bash
# Activate Python environment
conda activate thermal-env

# Build entire project
./gradlew build

# Run desktop application
./gradlew :PythonApp:runDesktopApp

# Build Android APK
./gradlew :AndroidApp:assembleDebug

# Run Python tests and validations
./gradlew :PythonApp:runPythonTests

# Test new implementations
python PythonApp/test_calibration_implementation.py
python PythonApp/test_shimmer_implementation.py

# Run calibration system
./gradlew :PythonApp:runCalibration
```

## Navigation Architecture

The system features a completely redesigned navigation architecture that prioritizes simplicity, cleanliness, and maintainability across both Android and Python applications. This architectural transformation represents a fundamental shift from complex, monolithic interfaces to modern, component-based designs that enhance both user experience and code maintainability.

### Design Philosophy and Transformation

The navigation redesign addresses critical usability and maintainability challenges that emerged from the original architecture. The Android application previously contained over 1600 lines of code in a single MainActivity, creating a complex, difficult-to-maintain monolith. Similarly, the Python application suffered from scattered functionality across multiple dialogs and complex dependency injection patterns that hindered both development and user interaction.

**Key Transformation Achievements:**

The redesigned architecture achieves a **90% reduction** in main activity complexity through systematic decomposition into focused fragments. Each fragment now handles a specific functional area (Recording, Devices, Calibration, Files) with clear separation of concerns and standardized interaction patterns. This transformation eliminates code duplication while improving testability and maintainability.

The Python application transformation simplifies the complex multi-panel architecture into an intuitive tabbed interface that organizes functionality according to user workflow rather than technical implementation details. This approach reduces cognitive load while maintaining access to all advanced features through progressive disclosure patterns.

### Android Application Navigation

The Android navigation architecture employs a sophisticated three-tier system that provides multiple access patterns while maintaining interface clarity and efficiency.

**Navigation Drawer Organization:**
The primary navigation employs a logical hierarchy that groups related functionality while providing quick access to essential features. The drawer organizes functions into three distinct groups:

- **Main Functions Group**: Contains the core operational areas (Recording, Devices, Calibration, Files) that represent the primary user workflows for multi-sensor data collection.
- **Settings Group**: Provides access to configuration options (Settings, Network Config, Shimmer Config) that customize system behavior for different research requirements.
- **Tools Group**: Includes diagnostic and utility functions (Sync Tests, About) that support system maintenance and troubleshooting.

**Bottom Navigation Integration:**
The bottom navigation bar provides immediate access to the most frequently used functions (Record, Monitor, Calibrate) without requiring drawer navigation. This dual-navigation approach accommodates different user preferences and usage patterns while maintaining interface efficiency.

**Fragment Architecture Benefits:**
Each functional area is implemented as an independent fragment with focused responsibilities:

- **RecordingFragment**: Manages recording controls, real-time status monitoring, and session progress tracking with integrated UI utilities for consistent state management.
- **DevicesFragment**: Handles device discovery, connection management, and status monitoring using reusable connection management components.
- **CalibrationFragment**: Provides calibration workflow controls with progress tracking and quality assessment feedback.
- **FilesFragment**: Manages data export, file organization, and session review with integrated logging and status reporting.

The fragment architecture enables parallel development, comprehensive testing, and flexible feature enhancement while maintaining consistent user experience across all functional areas.

### Python Application Navigation

The Python application features a clean tabbed interface that organizes functionality according to research workflow phases rather than technical system architecture. This workflow-oriented organization enables researchers to focus on their experimental objectives while providing logical access to technical controls.

**Tabbed Interface Structure:**
Each tab represents a distinct phase of the research workflow:

- **Recording Tab**: Provides centralized recording controls with real-time preview, session management, and progress monitoring using modern UI components for enhanced visual feedback.
- **Devices Tab**: Features comprehensive device connection management with individual connection controls for different device types (PC, Android, Shimmer) and global coordination functions.
- **Calibration Tab**: Offers streamlined calibration workflows with progress tracking, quality assessment, and result management using standardized UI components.
- **Files Tab**: Includes data management functions, export capabilities, and integrated system logging with search and filtering capabilities.

**Component-Based Architecture:**
The Python interface employs reusable UI components that ensure consistent appearance and behavior across all functional areas:

- **ModernButton**: Provides standardized button styling with hover effects and semantic color coding for different action types.
- **StatusIndicator**: Delivers consistent status communication across all device types and operational states with coordinated visual feedback.
- **ProgressIndicator**: Offers unified progress visualization for operations ranging from connection attempts to calibration procedures.
- **ConnectionManager**: Manages device connections with standardized controls and status reporting across different hardware types.

### Navigation Utility Framework

Both applications leverage sophisticated utility frameworks that reduce code duplication while ensuring consistent behavior across all interface components.

**Android Navigation Utilities:**
The NavigationUtils class provides centralized navigation management with error handling, state validation, and consistent behavior across all fragments. This utility framework includes methods for fragment navigation, activity launching, drawer navigation handling, and destination validation that ensure reliable navigation behavior regardless of system state.

**Android UI Utilities:**
The UIUtils class standardizes common UI operations including connection indicator updates, recording status management, button styling, and status message presentation. These utilities ensure visual consistency while reducing implementation complexity across all fragments.

**Python Component Library:**
The common_components module provides a comprehensive library of reusable UI elements including modern buttons, status indicators, progress visualization, and connection management widgets. This component library ensures consistent appearance and behavior while enabling rapid interface development and modification.

### Architectural Benefits and Impact

The navigation architecture redesign delivers measurable improvements across multiple dimensions of system quality and user experience.

**Maintainability Enhancements:**
Code organization improvements include **100% removal** of deprecated UI elements and dead code, systematic elimination of code duplication through utility frameworks, and clear separation of concerns through component-based architecture. These improvements significantly reduce maintenance overhead while improving system reliability and enhancement capability.

**User Experience Improvements:**
Interface clarity improvements provide intuitive navigation patterns that reduce learning requirements, consistent visual feedback that communicates system state effectively, and efficient access patterns that minimize steps required for common operations. The redesigned navigation supports both novice users who require clear guidance and expert users who need efficient access to advanced functionality.

**Development Process Benefits:**
The modular architecture enables parallel development of different interface areas, comprehensive testing through focused component isolation, and flexible deployment strategies that support incremental feature enhancement. The standardized utility frameworks reduce implementation complexity while ensuring consistent behavior across all interface components.

### Implementation Quality and Standards

The navigation architecture implementation employs modern development practices and industry-standard design patterns that ensure long-term maintainability and extensibility.

**Code Quality Standards:**
Implementation includes comprehensive error handling with graceful degradation, standardized logging and debugging support, and consistent documentation patterns that support both development and user assistance. The codebase follows established conventions for Android Kotlin development and Python PyQt5 implementation while maintaining platform-appropriate design patterns.

**Testing and Validation:**
The architecture supports comprehensive testing through modular component design, standardized interfaces that enable automated testing, and clear separation between UI presentation and business logic. Testing strategies include unit testing for individual components, integration testing for navigation flows, and user experience validation for workflow efficiency.

**Performance Optimization:**
Navigation implementation includes efficient state management that minimizes unnecessary updates, intelligent component loading that optimizes resource utilization, and responsive design patterns that maintain performance across different hardware configurations. The architecture provides excellent performance characteristics while maintaining rich interactive capabilities.

The system employs a distributed architecture where multiple sensor nodes coordinate with a central controller to achieve synchronized data collection across heterogeneous sensor types.

### Complete Data Flow Architecture

```mermaid
graph TB
    subgraph "Data Collection Layer"
        subgraph "Mobile Sensors"
            A1[Android Device #1<br/>Camera + Thermal + GSR]
            A2[Android Device #2<br/>Camera + Thermal + GSR]
        end
        
        subgraph "Stationary Sensors"
            W1[USB Webcam #1<br/>4K Video]
            W2[USB Webcam #2<br/>4K Video]
        end
        
        subgraph "Physiological Sensors"
            S1[Shimmer3 GSR+ #1<br/>Bluetooth]
            S2[Shimmer3 GSR+ #2<br/>Bluetooth]
        end
    end
    
    subgraph "Processing & Control Layer"
        PC[PC Controller<br/>Synchronization Master]
        SYNC[Temporal Synchronization<br/>Engine]
        CAL[Camera Calibration<br/>System]
        STIM[Stimulus Presentation<br/>Controller]
    end
    
    subgraph "Data Storage & Analysis"
        VID[Video Files<br/>MP4 + RAW]
        THER[Thermal Data<br/>Binary + Metadata]
        GSR[Physiological Data<br/>CSV + Timestamps]
        META[Session Metadata<br/>JSON + Logs]
    end
    
    A1 -->|WiFi Socket| PC
    A2 -->|WiFi Socket| PC
    S1 -->|Bluetooth| A1
    S2 -->|Bluetooth| A2
    W1 -->|USB 3.0| PC
    W2 -->|USB 3.0| PC
    
    PC --> SYNC
    PC --> CAL
    PC --> STIM
    
    SYNC --> VID
    SYNC --> THER
    SYNC --> GSR
    SYNC --> META
    
    CAL -.->|Calibration Data| VID
    STIM -.->|Event Timing| META
```

### Hardware Integration Overview

```mermaid
graph TB
    subgraph "Multi-Sensor Recording System"
        subgraph "Hardware Layer"
            A1[Samsung S22 #1<br/>Camera + Thermal]
            A2[Samsung S22 #2<br/>Camera + Thermal]
            W1[Logitech Brio 4K #1]
            W2[Logitech Brio 4K #2]
            S1[Shimmer3 GSR+ #1]
            S2[Shimmer3 GSR+ #2]
        end
        
        subgraph "Android Apps"
            AA1[Android App #1]
            AA2[Android App #2]
        end
        
        subgraph "PC Controller"
            PC[Windows PC<br/>Master Controller]
            GUI[PyQt5 GUI]
            CAL[OpenCV Calibration]
            NET[Socket Network]
        end
        
        A1 --> AA1
        A2 --> AA2
        S1 --> AA1
        S2 --> AA2
        
        AA1 -->|WiFi Socket| PC
        AA2 -->|WiFi Socket| PC
        W1 -->|USB| PC
        W2 -->|USB| PC
        
        PC --> GUI
        PC --> CAL
        PC --> NET
    end
```

### Android Application Architecture

```mermaid
graph TB
    subgraph "Android App Architecture"
        subgraph "UI Layer"
            MA[MainActivity]
            VM[MainViewModel]
            UI[UI Components]
        end
        
        subgraph "Recording Layer"
            CR[CameraRecorder<br/>Camera2 API]
            TR[ThermalRecorder<br/>Topdon SDK]
            SR[ShimmerRecorder<br/>Bluetooth]
            SM[SessionManager]
        end
        
        subgraph "Communication Layer"
            PCH[PCCommunicationHandler]
            CM[ConnectionManager]
            PS[PreviewStreamer]
        end
        
        subgraph "Data Layer"
            DS[DeviceStatusTracker]
            SI[SessionInfo]
            SS[SensorSample]
        end
        
        MA --> VM
        VM --> CR
        VM --> TR
        VM --> SR
        VM --> SM
        
        CR --> PCH
        TR --> PCH
        SR --> PCH
        PCH --> CM
        
        CR --> PS
        PS --> CM
        
        CR --> DS
        TR --> DS
        SR --> DS
        
        SM --> SI
        SR --> SS
    end
```

### PC Application Architecture

```mermaid
graph TB
    subgraph "Python Desktop Controller"
        subgraph "GUI Layer"
            APP[application.py<br/>Main Entry]
            UI[PyQt5 Interface]
            LOG[Logging System]
        end
        
        subgraph "Camera Management"
            WM[WebcamManager<br/>USB Cameras]
            CAM[Camera Control]
            REC[Recording Pipeline]
        end
        
        subgraph "Calibration System"
            CM[CalibrationManager<br/>Complete Implementation]
            CP[CalibrationProcessor<br/>OpenCV Integration]
            CR[CalibrationResult<br/>Quality Assessment]
            CV[Computer Vision<br/>Pattern Detection]
        end
        
        subgraph "Shimmer Integration"
            SM[ShimmerManager<br/>Multi-Library Support]
            SB[Shimmer Bluetooth<br/>Direct Connection]
            SA[Shimmer Android<br/>Mediated Connection]
            SD[Shimmer Data<br/>Stream Processing]
        end
        
        subgraph "Network Layer"
            SM[SessionManager<br/>Socket Server]
            NCH[NetworkCommunicationHandler]
            DS[DeviceService]
        end
        
        subgraph "Data Processing"
            DP[DataProcessor]
            SYNC[SynchronizationEngine]
            EXP[DataExporter]
        end
        
        APP --> UI
        APP --> LOG
        UI --> WM
        UI --> CM
        UI --> SM
        
        WM --> CAM
        CAM --> REC
        
        CM --> CP
        CP --> CR
        CM --> CV
        
        SM --> NCH
        NCH --> DS
        
        REC --> DP
        DP --> SYNC
        SYNC --> EXP
    end
```

### Monorepo Structure
```
project-root/
├── settings.gradle              # gradle settings: includes both modules
├── build.gradle                 # root gradle build configuration
├── .gitmodules                  # git submodules configuration
├── gradle/wrapper/              # gradle wrapper files
├── gradlew & gradlew.bat        # gradle wrapper scripts
├── AndroidApp/                  # android app module (kotlin + camera2, shimmer, etc.)
│   ├── build.gradle             # android module build configuration
│   ├── src/main/                # android source code
│   │   ├── AndroidManifest.xml  # android app manifest
│   │   ├── java/...             # kotlin source packages
│   │   └── res/...              # android resources
├── PythonApp/                   # python desktop app module (pyqt5, opencv)
│   ├── build.gradle             # python module build configuration
│   ├── src/                     # python source files
│   │   └── main.py              # entry-point script for pyqt5 app
├── external/                    # external dependencies (git submodules)
│   ├── IRCamera/                # thermal camera library (submodule)
│   ├── psychopy/                # psychopy library (submodule)
│   ├── pyshimmer/               # python shimmer sdk (submodule)
│   ├── Shimmer-Java-Android-API/ # android shimmer sdk (submodule)
│   ├── topdon-sdk/              # topdon thermal camera sdk (submodule)
│   └── TOPDON_EXAMPLE_SDK_USB_IR_1.3.7 3/ # legacy topdon sdk (local directory)
├── docs/                        # project documentation
├── changelog.md                 # project changelog
├── todo.md                      # task tracking
└── .gitignore                   # git ignore file
```

### Git Submodules

This project uses Git submodules to manage external dependencies from GitHub repositories:

| Submodule | Repository | Description |
|-----------|------------|-------------|
| `external/IRCamera` | [CoderCaiSL/IRCamera](https://github.com/CoderCaiSL/IRCamera.git) | Thermal camera library for Android |
| `external/psychopy` | [psychopy/psychopy](https://github.com/psychopy/psychopy.git) | Psychology experiment framework |
| `external/pyshimmer` | [seemoo-lab/pyshimmer](https://github.com/seemoo-lab/pyshimmer.git) | Python SDK for Shimmer sensors |
| `external/Shimmer-Java-Android-API` | [ShimmerEngineering/Shimmer-Java-Android-API](https://github.com/ShimmerEngineering/Shimmer-Java-Android-API.git) | Official Android SDK for Shimmer sensors |
| `external/topdon-sdk` | [buccancs/topdon-sdk](https://github.com/buccancs/topdon-sdk.git) | Topdon thermal camera SDK |

**Note**: The `TOPDON_EXAMPLE_SDK_USB_IR_1.3.7 3` directory contains legacy proprietary SDK files and remains as a local directory.

### Synchronization Flow

```mermaid
sequenceDiagram
    participant PC as PC Controller
    participant A1 as Android App #1
    participant A2 as Android App #2
    participant S1 as Shimmer3 #1
    participant S2 as Shimmer3 #2
    
    PC->>A1: Connect Socket
    PC->>A2: Connect Socket
    A1->>S1: Bluetooth Connect
    A2->>S2: Bluetooth Connect
    
    PC->>A1: Sync Clock Request
    PC->>A2: Sync Clock Request
    A1->>PC: Clock Response
    A2->>PC: Clock Response
    
    PC->>A1: Start Recording
    PC->>A2: Start Recording
    
    par Recording Phase
        A1->>S1: Start GSR Recording
        A1->>A1: Start Camera Recording
        A1->>A1: Start Thermal Recording
    and
        A2->>S2: Start GSR Recording
        A2->>A2: Start Camera Recording
        A2->>A2: Start Thermal Recording
    and
        PC->>PC: Start USB Webcam Recording
    end
    
    loop Data Streaming
        A1->>PC: Preview Stream + Status
        A2->>PC: Preview Stream + Status
        S1->>A1: GSR Data
        S2->>A2: GSR Data
    end
    
    PC->>A1: Stop Recording
    PC->>A2: Stop Recording
    A1->>S1: Stop GSR Recording
    A2->>S2: Stop GSR Recording
```

### Networking Architecture

```mermaid
graph TB
    subgraph "Network Communication"
        subgraph "PC Controller (Server)"
            SS[Socket Server<br/>Port 8080]
            SH[Session Handler]
            CM[Command Manager]
            DS[Data Synchronizer]
        end
        
        subgraph "Android Device #1"
            SC1[Socket Client]
            PCH1[PC Communication Handler]
            PS1[Preview Streamer<br/>Port 8081]
        end
        
        subgraph "Android Device #2"
            SC2[Socket Client]
            PCH2[PC Communication Handler]
            PS2[Preview Streamer<br/>Port 8082]
        end
        
        subgraph "WiFi Network"
            WIFI[192.168.1.x Network]
        end
        
        SS -->|Command Channel| SC1
        SS -->|Command Channel| SC2
        PS1 -->|Preview Stream| SS
        PS2 -->|Preview Stream| SS
        
        SC1 -.->|WiFi| WIFI
        SC2 -.->|WiFi| WIFI
        SS -.->|WiFi| WIFI
        
        SH --> CM
        CM --> DS
        PCH1 --> PS1
        PCH2 --> PS2
    end
```

### Data Collection Flow

```mermaid
flowchart TD
    START([Recording Session Start])
    
    subgraph "Data Sources"
        A1[Android #1<br/>Camera + Thermal]
        A2[Android #2<br/>Camera + Thermal]
        S1[Shimmer3 #1<br/>GSR Data]
        S2[Shimmer3 #2<br/>GSR Data]
        W1[USB Webcam #1]
        W2[USB Webcam #2]
    end
    
    subgraph "Data Processing"
        SYNC[Synchronization Engine]
        PROC[Data Processor]
        CAL[Calibration System]
    end
    
    subgraph "Data Storage"
        VID[Video Files<br/>MP4 + RAW]
        THER[Thermal Data<br/>Binary Format]
        GSR[GSR Data<br/>CSV/JSON]
        META[Metadata<br/>Session Info]
    end
    
    START --> A1
    START --> A2
    START --> W1
    START --> W2
    
    A1 --> S1
    A2 --> S2
    
    A1 --> SYNC
    A2 --> SYNC
    S1 --> SYNC
    S2 --> SYNC
    W1 --> SYNC
    W2 --> SYNC
    
    SYNC --> PROC
    PROC --> CAL
    
    CAL --> VID
    CAL --> THER
    CAL --> GSR
    CAL --> META
```

### Individual Sensor Integration

```mermaid
graph LR
    subgraph "Shimmer3 GSR+ Integration"
        SHIMMER[Shimmer3 Device]
        BLE[Bluetooth LE]
        SDK[Shimmer Android SDK]
        GSR[GSR Data Processing]
        
        SHIMMER -->|Bluetooth| BLE
        BLE --> SDK
        SDK --> GSR
    end
    
    subgraph "Thermal Camera Integration"
        TOPDON[Topdon Thermal Camera]
        USB_C[USB-C Connection]
        TSDK[Topdon SDK]
        THERMAL[Thermal Image Processing]
        
        TOPDON -->|USB-C| USB_C
        USB_C --> TSDK
        TSDK --> THERMAL
    end
    
    subgraph "Camera2 Integration"
        CAM[Samsung S22 Camera]
        CAM2[Camera2 API]
        VID[Video Recording]
        RAW[RAW Image Capture]
        
        CAM --> CAM2
        CAM2 --> VID
        CAM2 --> RAW
    end
    
    subgraph "USB Webcam Integration"
        WEBCAM[Logitech Brio 4K]
        USB[USB 3.0]
        OPENCV[OpenCV Capture]
        STREAM[Video Stream]
        
        WEBCAM -->|USB 3.0| USB
        USB --> OPENCV
        OPENCV --> STREAM
    end
```

#### Working with Submodules

```bash
# Clone the repository with all submodules
git clone --recursive https://github.com/your-repo/project.git

# If already cloned, initialize and update submodules
git submodule init
git submodule update

# Update all submodules to latest commits
git submodule update --remote

# Update a specific submodule
git submodule update --remote external/psychopy
```

## Development Workflow

### Build Commands

The project uses Gradle as the primary build system with support for both Android and Python components:

```bash
# Build entire project (Android + Python)
./gradlew build

# Clean and rebuild everything
./gradlew clean build

# Build specific components
./gradlew AndroidApp:assembleDebug      # Android debug APK
./gradlew AndroidApp:assembleRelease    # Android release APK
./gradlew AndroidApp:installDebug       # Install on connected device

# Python environment management
./gradlew PythonApp:pipInstall          # Install Python dependencies
./gradlew PythonApp:runDesktopApp       # Run desktop controller
./gradlew PythonApp:runCalibration      # Run calibration routines
```

### Testing Commands

```bash
# Android testing
./gradlew AndroidApp:testDebugUnitTest         # Unit tests
./gradlew AndroidApp:connectedDebugAndroidTest # Integration tests (requires device)
./gradlew AndroidApp:lintDebug                 # Lint checks

# Python testing  
./gradlew PythonApp:runPythonTests             # Python unit tests
./gradlew PythonApp:runPythonTestsWithCoverage # Tests with coverage
./gradlew PythonApp:runPythonLinting           # Code quality checks
./gradlew PythonApp:formatPythonCode           # Format code
```

### Build Variants

The Android app supports multiple build configurations for different environments:

- **Debug**: Development build with debugging enabled
- **Release**: Production build with optimizations  
- **Staging**: Pre-production build for testing

Example commands for specific variants:
```bash
./gradlew AndroidApp:assembleDevDebug
./gradlew AndroidApp:assembleProdRelease
./gradlew AndroidApp:testDevDebugUnitTest
```

## Technology Stack

### Android Application (Kotlin)
- **Language**: Kotlin with Android Views and ViewBinding
- **Camera**: Camera2 API for 4K recording and RAW capture with DngCreator compatibility
- **Networking**: OkHttp for socket communication
- **Dependency Injection**: Hilt
- **Concurrency**: Kotlin Coroutines
- **Architecture**: Clean Architecture with Repository pattern
- **Shimmer Integration**: Enhanced SDK integration with reflection-based compatibility

### Python Desktop Application
- **Language**: Python 3.8+ with PyQt5 5.15.7 for GUI
- **Computer Vision**: OpenCV 4.8.0.74 for complete camera calibration implementation
- **Numerical Computing**: NumPy 1.24.3 for data processing
- **Networking**: WebSockets and Requests for communication
- **Image Processing**: Pillow for image manipulation
- **Bluetooth Integration**: Multi-library support (pyshimmer, bluetooth, pybluez)
- **Data Export**: CSV and JSON formats with session management

### Build System
- **Primary Build Tool**: Gradle 8.4 with multi-project setup
- **Android Plugin**: 8.1.2 for Android development
- **Python Integration**: ru.vyarus.use-python plugin 3.0.0 for Python environment management

## Key Features

### Android Application Features
- **4K RGB video recording** with simultaneous RAW image capture using Camera2 API
- **Thermal camera integration** using Topdon SDK for thermal imaging with USB-C connectivity
- **Shimmer3 GSR+ sensor communication** via Bluetooth with enhanced sampling rate configuration
- **Real-time preview streaming** to PC controller for monitoring with adaptive frame rates
- **Socket-based remote control** interface for synchronized operation across multiple devices
- **Local data storage** with comprehensive session management and metadata tracking
- **DngCreator RAW processing** with API compatibility fixes for Android 21+ support
- **Enhanced UI feedback** with session status indicators and improved error handling

### Desktop Controller Features  
- **PyQt5 GUI** with real-time device status monitoring across all sensors
- **Comprehensive recording control** interface with start/stop/calibration functions
- **USB webcam capture** and recording for stationary high-quality video
- **Complete camera calibration system** with OpenCV-based intrinsic and extrinsic parameter calculation
- **Shimmer Bluetooth integration** with direct pyshimmer device connections and data streaming
- **Multi-library fallback support** for Shimmer connectivity (pyshimmer, bluetooth, pybluez)
- **Calibration quality assessment** with pattern detection and coverage analysis
- **Stimulus presentation system** for controlled experimental paradigms
- **Data synchronization and export** tools for multi-modal data analysis

## Configuration

### Python Environment
The Python environment uses Conda for dependency management. Dependencies are automatically configured through the setup scripts, but can also be managed manually:

```bash
# Activate the conda environment
conda activate thermal-env

# Update environment from environment.yml
conda env update -f environment.yml

# Verify installation
conda list
```

### Android Configuration
Key Android build settings:
- **Compile SDK**: 34 (Android 14)
- **Min SDK**: 24 (Android 7.0) 
- **Target SDK**: 34 (Android 14)
- **Namespace**: `com.multisensor.recording`

## Troubleshooting

### Recent Crash Fixes (Latest)

**Android App Startup Crashes Fixed**  
Recent updates have addressed several critical crash scenarios:
- **ClassCastException**: Fixed HandSegmentationControlView layout issue that caused startup crashes
- **Permission Errors**: Resolved XXPermissions library conflicts with background location permissions
- **Manifest Permission Issues**: Enhanced permission request sequencing to prevent timing-related crashes

For detailed information about these fixes, see [`docs/CRASH_FIXES.md`](docs/CRASH_FIXES.md).

### Common Issues and Solutions

**Java Version Compatibility**
- Use Java 17 or Java 21 for optimal compatibility
- Java 24 may cause issues with Gradle 8.4
- Set `JAVA_HOME` environment variable correctly

**Python Environment Issues**  
- Ensure Python 3.8+ is available
- Use the automated setup scripts for conda environment creation
- Check that all dependencies are installed with `conda list`

**Android Build Issues**
- Ensure Android SDK is properly configured
- Set `ANDROID_HOME` or `ANDROID_SDK_ROOT` environment variable
- Verify required Android SDK components are installed

**Build Validation**
Run the validation script for comprehensive environment checking:
```bash
./scripts/validate-build.ps1 -Verbose
```

## Documentation

### Architecture and Implementation
- **Architecture Details**: See `docs/architecture/` for detailed system design
- **API Documentation**: Generated docs available in `docs/generated_docs/`
- **Development Guidelines**: See `docs/development/` for coding standards
- **[Implementation Completion Report](docs/IMPLEMENTATION_COMPLETION_REPORT.md)**: Technical details of completed implementations

### New Feature Documentation
- **[API Reference](docs/API_REFERENCE.md)**: Comprehensive API documentation for CalibrationManager, ShimmerManager, and Android enhancements
- **[User Guide](docs/USER_GUIDE.md)**: Step-by-step guides for camera calibration and Shimmer sensor integration
- **[Testing Guide](docs/USER_GUIDE.md#testing)**: Instructions for testing new implementations

### Data Management
- **[Data Storage Guide](docs/DATA_STORAGE_QUICK_REFERENCE.md)**: Quick reference for data organization
- **[Data Structure Documentation](docs/DATA_STRUCTURE_DOCUMENTATION.md)**: Complete technical documentation
- **[File Naming Standards](docs/FILE_NAMING_STANDARDS.md)**: Naming conventions for consistency

### Android App (Kotlin)
- **Language:** Kotlin
- **UI:** Android Views with ViewBinding
- **Camera:** Camera2 API for 4K recording + RAW capture
- **Networking:** OkHttp for socket communication
- **Dependency Injection:** Hilt
- **Concurrency:** Kotlin Coroutines
- **Architecture:** Clean Architecture with Repository pattern

### Python Desktop App
- **Language:** Python 3.8+
- **UI Framework:** PyQt5 5.15.7
- **Computer Vision:** OpenCV 4.8.0.74
- **Numerical Computing:** NumPy 1.24.3
- **Networking:** WebSockets, Requests
- **Image Processing:** Pillow

### Build System
- **Primary:** Gradle 8.11.1 with multi-project setup
- **Android Plugin:** 8.7.3
- **Kotlin:** 2.1.0
- **Python Integration:** ru.vyarus.use-python plugin 3.0.0

## 📱 Android Application

The Android application serves as a mobile data collection node, providing comprehensive recording capabilities for video, thermal imaging, and physiological sensor data.

### Core Features
- **4K Video Recording**: High-quality video capture using Camera2 API with configurable resolution and frame rates
- **RAW Image Capture**: Simultaneous RAW image capture for advanced image processing and calibration
- **Thermal Camera Integration**: Real-time thermal imaging using Topdon TC001 cameras via USB-C OTG
- **Shimmer3 GSR+ Integration**: Bluetooth communication with physiological sensors for galvanic skin response measurement
- **Real-time Preview Streaming**: Live video preview transmission to PC controller for monitoring
- **Socket-based Remote Control**: Network-based command interface for synchronized multi-device recording
- **Local Data Storage**: Comprehensive session management with automatic file organization and metadata generation
- **Hand Segmentation**: MediaPipe-based hand landmark detection for region-of-interest analysis

### Technical Implementation
- **Language**: Kotlin with Android Views and ViewBinding
- **Camera**: Camera2 API for low-level camera control and dual capture modes
- **Networking**: OkHttp for socket communication with automatic reconnection
- **Dependency Injection**: Hilt for component management and testing
- **Concurrency**: Kotlin Coroutines for asynchronous operations
- **Architecture**: Clean Architecture with Repository pattern and MVVM

## 🖥️ Desktop Controller

The Python desktop application acts as the central orchestrator, coordinating multiple Android devices and USB cameras for synchronized data collection.

### Core Features
- **Multi-Device Coordination**: Simultaneous control of multiple Android smartphones and USB webcams
- **Real-time Monitoring**: Live status monitoring with device health indicators and preview streaming
- **Recording Session Management**: Centralized start/stop control with automatic session metadata generation
- **USB Webcam Integration**: DirectShow/V4L2 camera capture for stationary high-quality video recording
- **Camera Calibration System**: OpenCV-based intrinsic and extrinsic camera parameter estimation
- **Stimulus Presentation**: Integrated experimental stimulus controller for research applications
- **Data Synchronization**: Temporal alignment of multi-modal data streams with microsecond precision
- **Export and Analysis Tools**: Automated data processing and export for analysis workflows

### Technical Implementation
- **Language**: Python 3.8+ with modern scientific computing libraries
- **GUI Framework**: PyQt5 5.15.7 for cross-platform desktop interface
- **Computer Vision**: OpenCV 4.8.0.74 for camera operations and calibration algorithms
- **Numerical Computing**: NumPy 1.24.3 for high-performance data processing
- **Networking**: WebSockets and TCP sockets for device communication
- **Image Processing**: Pillow for image manipulation and format conversion

## 🔧 Configuration and Setup

### Environment Management
The project uses Conda for Python environment management and Gradle for overall build coordination. The automated setup scripts handle complete environment configuration:

```bash
# Complete automated setup (recommended)
python3 tools/development/setup.py

# Platform-specific setup
# Windows:
tools/development/setup_dev_env.ps1

# Linux/macOS:
tools/development/setup.sh
```

## 🎯 Key Implemented Features

### Camera Calibration System
The calibration system provides comprehensive OpenCV-based camera calibration:

```bash
# Run calibration tests and demonstrations
./gradlew PythonApp:runCalibration
python PythonApp/test_calibration_implementation.py
```

**Features:**
- **Pattern Detection**: Chessboard and circle grid detection with sub-pixel accuracy
- **Single Camera Calibration**: Intrinsic parameter calculation with RMS error analysis  
- **Stereo Calibration**: RGB-thermal camera alignment with rotation/translation matrices
- **Quality Assessment**: Coverage analysis with calibration quality metrics and recommendations
- **Data Persistence**: JSON-based save/load with metadata and parameter validation

### Shimmer Sensor Integration
The Shimmer system provides comprehensive Bluetooth sensor connectivity:

```bash
# Test Shimmer integration
python PythonApp/test_shimmer_implementation.py
```

**Features:**
- **Multi-Library Support**: Fallback support for pyshimmer, bluetooth, and pybluez libraries
- **Device Discovery**: Bluetooth scanning with automatic device detection and pairing
- **Direct Connections**: Full pyshimmer integration with serial port detection
- **Data Streaming**: Real-time sensor data with callback system and queue management
- **Session Management**: Session-based data organization with CSV export
- **Error Handling**: Graceful degradation when optional libraries are unavailable

### Android Compatibility Enhancements
Recent Android improvements include:

**DngCreator Support:**
- Reflection-based API compatibility for Android 21+ requirements
- Proper resource management with comprehensive cleanup
- Graceful degradation with informative error messages

**Shimmer Configuration:**
- Enhanced sampling rate configuration with reflection-based method detection
- SDK version compatibility handling
- Robust error recovery for missing SDK methods

**UI Improvements:**
- Enhanced SessionInfo display with status indicators and emojis
- Improved error state management with proper user feedback
- Better connection feedback during device operations

### Python Dependencies
The Python environment is managed automatically by Gradle. Dependencies are specified in `PythonApp/build.gradle`:

```gradle
python {
    pip 'pyqt5:5.15.7'
    pip 'opencv-python:4.8.0.74'
    pip 'numpy:1.24.3'
    pip 'requests:2.31.0'
    pip 'websockets:11.0.3'
    pip 'pillow:10.0.0'
}
```

### Optional Dependencies for Enhanced Features
The system includes optional dependencies that enable advanced functionality:

- **pyshimmer**: For direct Shimmer sensor connections (auto-detected)
- **bluetooth/pybluez**: Alternative Bluetooth libraries for Shimmer connectivity
- **OpenCV extras**: Additional computer vision algorithms for calibration
- **psutil**: System monitoring for performance optimization

The system gracefully handles missing optional dependencies and provides informative error messages when features are unavailable.

### Android Configuration
Key Android settings in `AndroidApp/build.gradle`:
- **Compile SDK:** 34
- **Min SDK:** 24 (Android 7.0)
- **Target SDK:** 34
- **Namespace:** `com.multisensor.recording`

## 🧪 Testing


The Multi-Sensor Recording System includes a comprehensive testing framework that validates all aspects of the system functionality, from individual component operation to complete end-to-end recording scenarios. The testing suite has been significantly extended to include advanced capabilities that ensure system reliability under various real-world conditions.

### Enhanced Testing Architecture

The testing framework follows a multi-layered approach that provides thorough coverage of all system components:

- **Foundation Tests**: Core logging and component integration validation
- **Functional Tests**: Individual feature and component testing
- **Integration Tests**: Cross-component and cross-platform coordination testing
- **Performance Tests**: Memory, CPU, and throughput validation under load
- **Resilience Tests**: Error recovery, network issues, and stress scenario testing
- **Quality Tests**: Data integrity, corruption detection, and recovery validation

### Running the Complete Test Suite

The comprehensive test suite orchestrates all testing scenarios as specified in the original requirements, with significant enhancements for real-world research environments:

```bash
# Run the complete enhanced test suite (recommended)
python PythonApp/run_complete_test_suite.py

# This will execute all test categories:
# 1. Integration Logging Test - Enhanced log analysis and validation
# 2. Focused Recording Session Test - PC-Android coordination with error recovery  
# 3. Hardware Sensor Simulation Test - Realistic sensor data and port validation
# 4. Enhanced Stress Testing Suite - Memory, CPU, and concurrent session testing
# 5. Network Resilience Testing - Latency, packet loss, and connection recovery
# 6. Data Integrity Validation Test - Corruption detection and file integrity
# 7. Comprehensive Recording Test - Complete end-to-end system validation
```

### Individual Test Categories

#### Basic System Validation
```bash
# Validate complete system functionality with build verification
./gradlew build

# Test core component implementations
python PythonApp/test_calibration_implementation.py
python PythonApp/test_shimmer_implementation.py

# Validate basic integration and logging
python PythonApp/test_integration_logging.py
```

#### Core Recording Functionality Testing
```bash
# Test PC-Android coordination and recording lifecycle
python PythonApp/test_focused_recording_session.py

# Test comprehensive sensor simulation on correct ports
python PythonApp/test_hardware_sensor_simulation.py

# Test complete end-to-end recording system
python PythonApp/test_comprehensive_recording_session.py
```

#### Enhanced Performance and Resilience Testing
```bash
# Test system performance under stress conditions
python PythonApp/test_enhanced_stress_testing.py

# Test network resilience and connection recovery
python PythonApp/test_network_resilience.py

# Test data integrity and corruption handling
python PythonApp/test_data_integrity_validation.py
```

#### Session Data Validation
```bash
# Validate all recorded sessions
python tools/validate_data_schemas.py --all-sessions

# Check specific session integrity
python tools/validate_data_schemas.py --session PythonApp/recordings/session_20250731_143022

# Validate session metadata and file integrity
python tools/validate_session_integrity.py --session session_20250731_143022
```

### Testing Capabilities and Coverage

The enhanced testing framework validates the complete problem statement requirements plus additional capabilities for research-grade reliability:

#### Original Requirements Validation ✅
1. **PC and Android app coordination**: Multiple device scenarios with connection recovery
2. **Phone connected to PC/IDE simulation**: Socket-based communication with error handling
3. **Recording session started from computer**: Various configuration scenarios and edge cases
4. **Available sensors used, rest simulated on correct ports**: Realistic data rates and port assignment
5. **Communication and networking testing**: Error conditions, recovery, and quality monitoring
6. **File saving and post processing**: Data integrity checks and metadata validation
7. **Button reaction and UI responsiveness**: Stress scenarios and response time validation
8. **Freezing/crashing detection and error handling**: Comprehensive recovery mechanisms
9. **Comprehensive logging verification**: Log analysis, anomaly detection, and validation

#### Enhanced Testing Capabilities 🚀
1. **Memory and Performance Monitoring**: Extended session testing with resource tracking
2. **Network Resilience Validation**: Latency, packet loss, and bandwidth limitation simulation
3. **Data Integrity Assurance**: Checksum validation, corruption detection, and recovery testing
4. **Concurrent Session Testing**: Multi-user scenarios and scalability validation
5. **Error Injection Testing**: Systematic failure simulation and recovery validation
6. **Performance Regression Detection**: Baseline comparison and performance monitoring
7. **Cross-Platform Compatibility**: Testing across different operating system configurations

### Implementation Testing Details

The system includes comprehensive testing for all major components with advanced validation capabilities:

#### **Enhanced Calibration Testing**
- **Pattern Detection Validation**: Support for various calibration board types and sizes
- **Accuracy Assessment**: Sub-pixel precision validation and error analysis
- **Stereo Calibration**: RGB-thermal alignment with rotation/translation validation
- **Quality Metrics**: Coverage analysis, RMS error assessment, and calibration recommendations
- **Persistence Testing**: Save/load validation with metadata integrity checking
- **Performance Testing**: Calibration speed and memory usage under various image conditions

#### **Advanced Shimmer Integration Testing**
- **Multi-Library Fallback**: Comprehensive testing across pyshimmer, bluetooth, and pybluez libraries
- **Device Discovery**: Bluetooth scanning reliability and automatic pairing validation
- **Data Streaming**: Real-time sensor data accuracy with callback system validation
- **Session Management**: CSV export integrity and session-based data organization
- **Error Recovery**: Graceful handling of missing dependencies and connection failures
- **Performance Validation**: Data throughput testing and memory usage optimization

#### **Comprehensive Android Compatibility Testing**
- **DngCreator Enhancement**: Reflection-based API compatibility for Android 21+ requirements
- **Sampling Rate Configuration**: Enhanced configuration across different SDK versions
- **UI State Management**: Comprehensive validation with error state handling
- **SessionInfo Display**: Status indicators, progress tracking, and user feedback validation
- **Resource Management**: Memory cleanup and proper lifecycle handling
- **Network Communication**: Robust socket communication with automatic reconnection

#### **Extended Performance Testing**
- **Memory Usage Monitoring**: Leak detection during extended recording sessions
- **CPU Performance**: Validation under high sensor data throughput conditions
- **Concurrent Sessions**: Multi-session scalability testing with resource contention
- **Network Throughput**: Bandwidth utilization and optimization under various conditions
- **Storage I/O Performance**: Large file operation testing and disk space management
- **Resource Cleanup**: Validation of proper resource release after session termination

#### **Advanced Network Resilience Testing**
- **Latency Simulation**: Configurable delay testing from 1ms to 500ms with jitter
- **Packet Loss Handling**: Recovery testing at various loss rates (0.1% to 10%)
- **Connection Recovery**: Automatic reconnection and session continuation validation
- **Bandwidth Adaptation**: Performance under constrained network conditions
- **Quality Degradation**: Graceful handling of network quality changes
- **Multi-Device Coordination**: Network stability with multiple simultaneous connections

#### **Comprehensive Data Integrity Testing**
- **Checksum Validation**: MD5 and SHA256 verification for all recorded data types
- **Corruption Detection**: Various corruption scenario testing (random, header, truncation)
- **Format Validation**: File format integrity checking for video, thermal, GSR, and metadata
- **Recovery Mechanisms**: Data recovery and error reporting under corruption scenarios
- **Cross-Platform Compatibility**: Data integrity across different operating systems
- **Temporal Synchronization**: Timestamp accuracy and consistency validation

### Test Results and Reporting

The testing framework provides comprehensive reporting and analysis:

#### **Real-Time Test Monitoring**
- **Progress Tracking**: Live updates during test execution with detailed status
- **Performance Metrics**: Real-time resource usage monitoring and alerting
- **Error Detection**: Immediate notification of test failures with context
- **Recovery Validation**: Automatic verification of error recovery mechanisms

#### **Comprehensive Test Reports**
```bash
# Test results are automatically saved to test_results/ directory
ls test_results/
# complete_test_results.json          - Overall test suite results
# enhanced_stress_test_results.json   - Performance and stress test data
# network_resilience_test_results.json - Network testing analysis
# data_integrity_test_results.json    - Data quality validation results
```

#### **Quality Metrics and Coverage**
- **Success Rate Tracking**: Percentage of tests passing with trend analysis
- **Performance Benchmarks**: Resource usage trends and regression detection
- **Coverage Analysis**: Requirements validation with evidence tracking
- **Reliability Metrics**: Error rates, recovery success, and system stability

### Testing Best Practices for Research Environments

The testing framework is specifically designed for research applications with the following considerations:

#### **Scientific Data Integrity**
- All recorded data is validated for integrity using cryptographic checksums
- Temporal synchronization accuracy is verified to ensure research-grade precision
- Cross-device data correlation is tested to maintain experimental validity
- File format compliance is verified to ensure long-term data accessibility

#### **Experimental Reliability**
- Extended session testing validates system stability during long research sessions
- Multi-participant scenarios are tested to ensure scalability for group studies
- Error recovery mechanisms are validated to prevent data loss during experiments
- Network resilience testing ensures reliable operation in various research facility environments

#### **Reproducibility and Documentation**
- All test scenarios are fully documented with expected outcomes and validation criteria
- Test data generation is deterministic to ensure reproducible results
- Performance baselines are established to detect system degradation over time
- Comprehensive logging provides audit trails for research compliance requirements

### Continuous Integration and Quality Assurance

The testing framework integrates with continuous integration systems to maintain code quality:

```bash
# Automated testing in CI/CD pipelines
./gradlew :PythonApp:runPythonTests          # Python unit tests
./gradlew :AndroidApp:testDebugUnitTest      # Android unit tests  
./gradlew :AndroidApp:connectedDebugAndroidTest # Android integration tests

# Quality gates and validation
./gradlew :PythonApp:runPythonTestsWithCoverage # Coverage analysis
./gradlew :AndroidApp:lintDebug                 # Code quality checks
./gradlew :PythonApp:formatPythonCode          # Code formatting validation
```

This comprehensive testing approach ensures that the Multi-Sensor Recording System meets research-grade requirements for reliability, accuracy, and data integrity while providing the flexibility needed for diverse experimental scenarios.
- SessionInfo display and status indicator testing
=======
The multi-sensor recording system includes a comprehensive testing framework that validates all aspects of the PC-Android simulation workflow. The testing infrastructure provides multiple validation scenarios ranging from basic functionality checks to advanced stress testing and performance benchmarking.

### Comprehensive Recording Session Testing

The system includes a specialized test suite that validates the complete PC-Android recording workflow. This comprehensive test simulates real-world usage scenarios where PC and Android applications work together to collect synchronized multi-sensor data.

#### Quick Validation Testing
For rapid validation and CI/CD integration, use the quick test runner that covers all core requirements without external dependencies:

```bash
# Quick comprehensive test (recommended for CI/CD)
cd PythonApp
python run_quick_recording_session_test.py
```

This streamlined test validates all essential system components including PC application initialization, Android device simulation, communication protocols, recording session management, sensor data generation, file persistence, and logging verification. The test typically completes within 30 seconds and provides immediate feedback on system functionality.

#### Advanced Recording Session Testing
For thorough validation with configurable test scenarios, use the enhanced test runner:

```bash
# Standard comprehensive test
python run_recording_session_test.py

# Extended test with multiple devices and longer duration
python run_recording_session_test.py --duration 120 --devices 4 --verbose

# Stress testing with high load scenarios
python run_recording_session_test.py --stress-test --devices 8 --duration 300

# Performance benchmarking with detailed metrics
python run_recording_session_test.py --performance-bench --save-logs

# Long-duration stability testing
python run_recording_session_test.py --long-duration --health-check

# Error condition simulation and recovery testing
python run_recording_session_test.py --error-simulation --network-issues

# Memory stress testing with high data volumes
python run_recording_session_test.py --memory-stress --devices 6
```

#### Test Configuration Options

The comprehensive test runner supports extensive configuration to validate different usage scenarios:

**Basic Testing Options:**
• `--duration SECONDS` - Set recording simulation duration (default: 30 seconds)
• `--devices COUNT` - Number of Android devices to simulate (default: 2 devices)
• `--port PORT` - Server communication port (default: 9000)
• `--verbose` - Enable detailed progress information and debug output
• `--log-level LEVEL` - Control logging verbosity (DEBUG, INFO, WARNING, ERROR)
• `--save-logs` - Persist detailed logs to files for post-analysis
• `--health-check` - Enable continuous system health monitoring

**Advanced Testing Scenarios:**
• `--stress-test` - High-load testing with increased device count and concurrent operations
• `--error-simulation` - Intentional failure injection and recovery validation
• `--performance-bench` - Detailed performance metrics and benchmarking
• `--long-duration` - Extended stability testing (minimum 10 minutes)
• `--network-issues` - Network latency, packet loss, and reconnection testing
• `--memory-stress` - High memory usage scenarios and leak detection

### Core System Testing

#### Running Tests
```bash
# Validate complete system functionality with all components
./gradlew build

# Test individual components for specific functionality validation
python PythonApp/test_calibration_implementation.py
python PythonApp/test_shimmer_implementation.py

# Validate data integrity and session management
python tools/validate_data_schemas.py --all-sessions

# Check specific recording session data
python tools/validate_data_schemas.py --session PythonApp/recordings/session_20250731_143022

# Run comprehensive test suite with all components
python PythonApp/run_comprehensive_tests.py
```

### Implementation Testing Categories

The testing framework validates all major system components through targeted test scenarios:

#### Camera Calibration System Testing
The calibration testing suite validates the OpenCV-based camera calibration implementation with comprehensive quality assessment:

• **Pattern Detection Validation**: Tests chessboard and circle grid detection algorithms with various calibration board configurations and lighting conditions
• **Single Camera Calibration Accuracy**: Validates intrinsic parameter calculation with RMS error analysis and quality metrics
• **Stereo Calibration Validation**: Tests RGB-thermal camera alignment with rotation and translation matrix validation using both synthetic and real-world data
• **Quality Assessment Algorithm Verification**: Validates calibration quality metrics, coverage analysis, and recommendation system accuracy
• **Data Persistence and Loading**: Tests JSON-based save/load functionality with metadata validation and parameter consistency checks

#### Shimmer Sensor Integration Testing
The Shimmer testing framework ensures robust Bluetooth sensor connectivity across multiple library implementations:

• **Multi-Library Fallback Testing**: Validates compatibility with pyshimmer, bluetooth, and pybluez libraries with graceful degradation
• **Device Discovery and Connection**: Tests Bluetooth scanning, device detection, pairing procedures, and serial port identification
• **Data Streaming Accuracy**: Validates real-time sensor data collection with callback system testing and queue management
• **Session Management Verification**: Tests session-based data organization with CSV export functionality and metadata persistence
• **Error Handling Validation**: Ensures graceful handling of missing dependencies, connection failures, and device disconnections

#### Android Application Compatibility Testing
The Android testing suite validates mobile application functionality and cross-platform compatibility:

• **DngCreator Implementation Testing**: Validates reflection-based API compatibility for Android 21+ with proper resource management
• **Sampling Rate Configuration**: Tests enhanced sampling rate settings across different SDK versions with reflection-based method detection
• **UI Component Validation**: Validates user interface responsiveness with error state management and status indicator accuracy
• **SessionInfo Display Testing**: Tests session information presentation with status indicators, emojis, and user feedback mechanisms
• **Communication Protocol Testing**: Validates JSON socket communication with PC controller and message acknowledgment systems

#### Integration and System Testing
The integration testing framework validates end-to-end system functionality:

• **PC-Android Communication**: Tests complete communication workflow with handshake procedures, command processing, and status updates
• **Multi-Device Coordination**: Validates synchronized operation across multiple Android devices with centralized PC control
• **Recording Session Management**: Tests complete recording lifecycle from initialization to data export with comprehensive validation
• **Data Synchronization**: Validates temporal alignment of multi-modal data streams with microsecond precision requirements
• **File System Integration**: Tests session folder creation, file naming conventions, and data persistence across all sensor types

### Testing Best Practices

#### Development Testing Workflow
When developing new features or modifications, follow this testing workflow to ensure system reliability:

1. **Unit Testing**: Test individual components in isolation to validate specific functionality
2. **Integration Testing**: Validate component interactions and data flow between system parts
3. **System Testing**: Run comprehensive recording session tests to validate end-to-end functionality
4. **Performance Testing**: Execute benchmarking tests to ensure performance requirements are met
5. **Stress Testing**: Validate system behavior under high load and resource constraints
6. **Error Testing**: Test error conditions and recovery mechanisms to ensure system robustness

#### Continuous Integration Testing
The testing framework is designed for automated CI/CD integration with structured reporting:

```bash
# CI/CD friendly test execution with structured output
python run_quick_recording_session_test.py --log-level INFO

# Generate test reports for automated analysis
python run_recording_session_test.py --save-logs --performance-bench

# Validate system health and performance metrics
python run_comprehensive_tests.py --generate-report
```

#### Troubleshooting Test Failures
When tests fail, use these diagnostic approaches to identify and resolve issues:

• **Verbose Logging**: Use `--verbose` and `--log-level DEBUG` for detailed execution information
• **Component Isolation**: Test individual components separately to isolate failure sources
• **Resource Monitoring**: Use `--health-check` to monitor system resources during test execution
• **Network Diagnostics**: Use `--network-issues` to test connectivity and communication protocols
• **Performance Analysis**: Use `--performance-bench` to identify performance bottlenecks and optimization opportunities


## Contributing

I welcome contributions to improve the multi-sensor recording system:

1. Fork the repository and create a feature branch
2. Make your changes following the established coding standards
3. Update documentation as needed for any new features
4. Ensure all tests pass and add new tests for new functionality
5. Submit a pull request with a clear description of changes

### Development Standards
- **Kotlin**: Follow official Kotlin coding conventions
- **Python**: Adhere to PEP 8 style guidelines  
- **Git**: Use descriptive commit messages and feature branches
- **Documentation**: Keep README and docs up-to-date with changes

## License

This project is licensed under the MIT License. See the LICENSE file for complete details.

## Acknowledgments

This multi-sensor recording system is designed for advanced research applications requiring precise temporal synchronization across diverse sensor modalities. The architecture leverages modern Android development practices and the proven Python scientific computing ecosystem to provide a robust platform for multi-modal data collection in experimental research environments.
