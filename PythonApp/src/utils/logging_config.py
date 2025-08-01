"""
Centralized Logging Configuration for Multi-Sensor Recording System

This module provides centralized logging configuration and utilities for the entire
Python application. It sets up consistent logging across all modules with proper
formatting, file rotation, and integration with the existing SessionLogger.

Enhanced with performance monitoring, structured logging, and comprehensive debugging.

Author: Multi-Sensor Recording System Team
Date: 2025-07-30
"""

import logging
import logging.handlers
import os
import sys
import time
import threading
import traceback
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
from functools import wraps


class StructuredFormatter(logging.Formatter):
    """Custom formatter that outputs structured JSON logs for machine parsing."""
    
    def format(self, record):
        """Format log record as structured JSON."""
        log_entry = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'thread': record.thread,
            'thread_name': record.threadName,
            'message': record.getMessage()
        }
        
        # Add exception information if present
        if record.exc_info:
            log_entry['exception'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'traceback': traceback.format_exception(*record.exc_info)
            }
        
        # Add any extra fields from the record
        extra_fields = {}
        reserved_fields = {
            'name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 
            'filename', 'module', 'lineno', 'funcName', 'created', 
            'msecs', 'relativeCreated', 'thread', 'threadName', 
            'processName', 'process', 'getMessage', 'exc_info', 
            'exc_text', 'stack_info', 'asctime', 'message'
        }
        
        for key, value in record.__dict__.items():
            if key not in reserved_fields:
                extra_fields[key] = value
        
        if extra_fields:
            log_entry['extra'] = extra_fields
        
        return json.dumps(log_entry, default=str)


class PerformanceMonitor:
    """Performance monitoring utilities for logging."""
    
    _timing_data = {}
    _lock = threading.Lock()
    
    @classmethod
    def start_timer(cls, operation: str, context: str = None) -> str:
        """Start timing an operation."""
        timer_id = f"{operation}_{int(time.time() * 1000000)}"
        if context:
            timer_id = f"{context}_{timer_id}"
        
        with cls._lock:
            cls._timing_data[timer_id] = {
                'operation': operation,
                'context': context,
                'start_time': time.perf_counter(),
                'thread': threading.current_thread().name
            }
        
        return timer_id
    
    @classmethod
    def end_timer(cls, timer_id: str, logger: logging.Logger = None) -> float:
        """End timing an operation and optionally log the result."""
        with cls._lock:
            if timer_id not in cls._timing_data:
                if logger:
                    logger.warning(f"Timer {timer_id} not found")
                return 0.0
            
            timing_info = cls._timing_data.pop(timer_id)
        
        duration = time.perf_counter() - timing_info['start_time']
        
        if logger:
            extra_info = {
                'duration_ms': duration * 1000,
                'operation': timing_info['operation'],
                'context': timing_info['context'],
                'timer_thread': timing_info['thread']  # Renamed to avoid conflict
            }
            logger.info(f"Operation '{timing_info['operation']}' completed in {duration:.3f}s", 
                       extra=extra_info)
        
        return duration
    
    @classmethod
    def get_active_timers(cls) -> Dict[str, Dict[str, Any]]:
        """Get information about currently active timers."""
        with cls._lock:
            return cls._timing_data.copy()


class ColoredFormatter(logging.Formatter):
    """Custom formatter that adds colors to console output based on log level."""
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
        'RESET': '\033[0m'       # Reset
    }
    
    def format(self, record):
        """Format log record with colors for console output."""
        # Store original level name
        original_levelname = record.levelname
        
        # Add color to level name
        if record.levelname in self.COLORS:
            record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}{self.COLORS['RESET']}"
        
        # Format the message
        formatted = super().format(record)
        
        # Restore original level name
        record.levelname = original_levelname
        
        return formatted


class AppLogger:
    """
    Centralized logger manager for the Multi-Sensor Recording System.
    
    Provides consistent logging configuration across all modules with:
    - Console output with colors
    - File output with rotation
    - Structured JSON logging for machine parsing
    - Performance monitoring
    - Integration with SessionLogger
    - Configurable log levels
    """
    
    _initialized = False
    _root_logger = None
    _log_dir = None
    _performance_monitor = PerformanceMonitor()
    
    @classmethod
    def initialize(cls, 
                   log_level: str = "INFO",
                   log_dir: Optional[str] = None,
                   console_output: bool = True,
                   file_output: bool = True,
                   structured_logging: bool = True) -> None:
        """
        Initialize the application logging system.
        
        Args:
            log_level: Minimum log level ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
            log_dir: Directory for log files (defaults to 'logs' in project root)
            console_output: Whether to output logs to console
            file_output: Whether to output logs to files
            structured_logging: Whether to include structured JSON logs
        """
        if cls._initialized:
            return
            
        # Set up log directory
        if log_dir is None:
            # Default to 'logs' directory in project root
            project_root = Path(__file__).parent.parent.parent
            log_dir = project_root / "logs"
        
        cls._log_dir = Path(log_dir)
        cls._log_dir.mkdir(parents=True, exist_ok=True)
        
        # Get root logger
        cls._root_logger = logging.getLogger()
        cls._root_logger.setLevel(getattr(logging, log_level.upper()))
        
        # Clear any existing handlers
        cls._root_logger.handlers.clear()
        
        # Console handler with colors
        if console_output:
            console_handler = logging.StreamHandler(sys.stdout)
            console_formatter = ColoredFormatter(
                '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
                datefmt='%H:%M:%S'
            )
            console_handler.setFormatter(console_formatter)
            console_handler.setLevel(getattr(logging, log_level.upper()))
            cls._root_logger.addHandler(console_handler)
        
        # File handler with rotation
        if file_output:
            # General application log file
            app_log_file = cls._log_dir / "application.log"
            file_handler = logging.handlers.RotatingFileHandler(
                app_log_file,
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5
            )
            file_formatter = logging.Formatter(
                '%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(file_formatter)
            file_handler.setLevel(logging.DEBUG)  # File gets all levels
            cls._root_logger.addHandler(file_handler)
            
            # Error-only log file for critical issues
            error_log_file = cls._log_dir / "errors.log"
            error_handler = logging.handlers.RotatingFileHandler(
                error_log_file,
                maxBytes=5*1024*1024,  # 5MB
                backupCount=3
            )
            error_handler.setFormatter(file_formatter)
            error_handler.setLevel(logging.ERROR)
            cls._root_logger.addHandler(error_handler)
            
            # Structured JSON log file for machine parsing
            if structured_logging:
                json_log_file = cls._log_dir / "structured.log"
                json_handler = logging.handlers.RotatingFileHandler(
                    json_log_file,
                    maxBytes=20*1024*1024,  # 20MB
                    backupCount=3
                )
                json_handler.setFormatter(StructuredFormatter())
                json_handler.setLevel(logging.DEBUG)
                cls._root_logger.addHandler(json_handler)
        
        cls._initialized = True
        
        # Log initialization message
        logger = cls.get_logger("AppLogger")
        logger.info("=== Multi-Sensor Recording System Logging Initialized ===")
        logger.info(f"Log level: {log_level}")
        logger.info(f"Log directory: {cls._log_dir}")
        logger.info(f"Console output: {console_output}")
        logger.info(f"File output: {file_output}")
        logger.info(f"Structured logging: {structured_logging}")
    
    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """
        Get a logger instance for a specific module.
        
        Args:
            name: Logger name (typically __name__ from calling module)
            
        Returns:
            logging.Logger: Configured logger instance
        """
        if not cls._initialized:
            cls.initialize()
        
        return logging.getLogger(name)
    
    @classmethod
    def start_performance_timer(cls, operation: str, context: str = None) -> str:
        """
        Start a performance timer for an operation.
        
        Args:
            operation: Name of the operation being timed
            context: Optional context information
            
        Returns:
            str: Timer ID to use with end_performance_timer
        """
        return cls._performance_monitor.start_timer(operation, context)
    
    @classmethod
    def end_performance_timer(cls, timer_id: str, logger_name: str = None) -> float:
        """
        End a performance timer and log the result.
        
        Args:
            timer_id: Timer ID returned by start_performance_timer
            logger_name: Name of logger to use for output
            
        Returns:
            float: Duration in seconds
        """
        logger = cls.get_logger(logger_name or "PerformanceMonitor")
        return cls._performance_monitor.end_timer(timer_id, logger)
    
    @classmethod
    def log_memory_usage(cls, context: str, logger_name: str = None) -> None:
        """
        Log current memory usage.
        
        Args:
            context: Context description for the memory measurement
            logger_name: Name of logger to use for output
        """
        try:
            import psutil
            process = psutil.Process()
            memory_info = process.memory_info()
            
            logger = cls.get_logger(logger_name or "MemoryMonitor")
            extra_info = {
                'context': context,
                'rss_mb': memory_info.rss / 1024 / 1024,
                'vms_mb': memory_info.vms / 1024 / 1024,
                'percent': process.memory_percent()
            }
            logger.info(f"Memory usage at {context}: RSS={memory_info.rss/1024/1024:.1f}MB, "
                       f"VMS={memory_info.vms/1024/1024:.1f}MB ({process.memory_percent():.1f}%)",
                       extra=extra_info)
        except ImportError:
            logger = cls.get_logger(logger_name or "MemoryMonitor")
            logger.debug("psutil not available for memory monitoring")
        except Exception as e:
            logger = cls.get_logger(logger_name or "MemoryMonitor")
            logger.error(f"Error getting memory usage: {e}")
    
    @classmethod
    def set_level(cls, level: str) -> None:
        """
        Change the logging level at runtime.
        
        Args:
            level: New log level ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
        """
        if cls._root_logger:
            cls._root_logger.setLevel(getattr(logging, level.upper()))
            # Update console handler level too
            for handler in cls._root_logger.handlers:
                if isinstance(handler, logging.StreamHandler) and handler.stream == sys.stdout:
                    handler.setLevel(getattr(logging, level.upper()))
    
    @classmethod
    def get_log_dir(cls) -> Optional[Path]:
        """Get the log directory path."""
        return cls._log_dir
    
    @classmethod
    def get_active_timers(cls) -> Dict[str, Dict[str, Any]]:
        """Get information about currently active performance timers."""
        return cls._performance_monitor.get_active_timers()


def get_logger(name: str) -> logging.Logger:
    """
    Convenience function to get a logger instance.
    
    Args:
        name: Logger name (typically __name__ from calling module)
        
    Returns:
        logging.Logger: Configured logger instance
    """
    return AppLogger.get_logger(name)


def performance_timer(operation_name: str = None, context: str = None):
    """
    Decorator to automatically time function execution.
    
    Args:
        operation_name: Custom operation name (defaults to function name)
        context: Optional context information
    
    Usage:
        @performance_timer("database_query", "user_data")
        def fetch_user_data():
            pass
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            op_name = operation_name or func.__name__
            timer_id = AppLogger.start_performance_timer(op_name, context)
            
            try:
                result = func(*args, **kwargs)
                AppLogger.end_performance_timer(timer_id, func.__module__)
                return result
            except Exception as e:
                AppLogger.end_performance_timer(timer_id, func.__module__)
                raise
        return wrapper
    return decorator


def log_function_entry(func):
    """
    Decorator to automatically log function entry and exit.
    
    Usage:
        @log_function_entry
        def my_function(arg1, arg2):
            pass
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        arg_info = f"args={len(args)}" if args else "no args"
        kwarg_info = f"kwargs={list(kwargs.keys())}" if kwargs else "no kwargs"
        logger.debug(f"→ Entering {func.__name__}({arg_info}, {kwarg_info})")
        
        try:
            result = func(*args, **kwargs)
            logger.debug(f"← Exiting {func.__name__} successfully")
            return result
        except Exception as e:
            logger.error(f"✗ Exception in {func.__name__}: {type(e).__name__}: {e}", exc_info=True)
            raise
    return wrapper


def log_method_entry(method):
    """
    Decorator to automatically log method entry and exit.
    
    Usage:
        class MyClass:
            @log_method_entry
            def my_method(self, arg1):
                pass
    """
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        logger = get_logger(self.__class__.__module__)
        arg_info = f"args={len(args)}" if args else "no args"
        kwarg_info = f"kwargs={list(kwargs.keys())}" if kwargs else "no kwargs"
        logger.debug(f"→ Entering {self.__class__.__name__}.{method.__name__}({arg_info}, {kwarg_info})")
        
        try:
            result = method(self, *args, **kwargs)
            logger.debug(f"← Exiting {self.__class__.__name__}.{method.__name__} successfully")
            return result
        except Exception as e:
            logger.error(f"✗ Exception in {self.__class__.__name__}.{method.__name__}: {type(e).__name__}: {e}", exc_info=True)
            raise
    return wrapper


def log_exception_context(logger_name: str = None):
    """
    Context manager to automatically log exceptions with context.
    
    Usage:
        with log_exception_context("my_operation"):
            risky_operation()
    """
    class ExceptionLogger:
        def __init__(self, logger_name):
            self.logger = get_logger(logger_name or __name__)
            
        def __enter__(self):
            return self
            
        def __exit__(self, exc_type, exc_val, exc_tb):
            if exc_type is not None:
                self.logger.error(f"Exception occurred: {exc_type.__name__}: {exc_val}", exc_info=True)
            return False  # Don't suppress the exception
    
    return ExceptionLogger(logger_name)


def log_memory_usage(context: str, logger_name: str = None):
    """
    Decorator to log memory usage before and after function execution.
    
    Args:
        context: Description of the operation
        logger_name: Optional logger name
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            AppLogger.log_memory_usage(f"{context} - before {func.__name__}", logger_name)
            try:
                result = func(*args, **kwargs)
                AppLogger.log_memory_usage(f"{context} - after {func.__name__}", logger_name)
                return result
            except Exception:
                AppLogger.log_memory_usage(f"{context} - after {func.__name__} (exception)", logger_name)
                raise
        return wrapper
    return decorator


# Auto-initialize on import with sensible defaults
AppLogger.initialize()