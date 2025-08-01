"""
Performance Optimizer - Comprehensive performance monitoring and optimization

This module provides advanced performance monitoring, profiling, and optimization
capabilities for the Multi-Sensor Recording System, ensuring efficient resource
utilization during long recording sessions.

Features:
- Memory usage monitoring and optimization
- CPU load balancing and thread management
- Network bandwidth management and adaptive quality control
- Data structure optimization and buffer management
- Real-time performance metrics and alerting
- Automatic resource cleanup and garbage collection

Author: Multi-Sensor Recording System
Date: 2025-07-30
"""

import gc
import json
import logging
import os
import psutil
import threading
import time
import tracemalloc
import weakref
from collections import deque, defaultdict
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Callable, Any


@dataclass
class PerformanceMetrics:
    """Performance metrics snapshot"""

    timestamp: float
    cpu_percent: float
    memory_mb: float
    memory_percent: float
    network_bytes_sent: int
    network_bytes_recv: int
    disk_io_read: int
    disk_io_write: int
    thread_count: int
    process_count: int
    gpu_usage: Optional[float] = None
    gpu_memory_mb: Optional[float] = None


@dataclass
class ResourceLimits:
    """Resource usage limits and thresholds"""

    max_memory_mb: float = 2048.0  # 2GB default
    max_cpu_percent: float = 80.0
    max_network_mbps: float = 100.0
    max_threads: int = 16
    memory_warning_threshold: float = 0.8  # 80% of max
    cpu_warning_threshold: float = 0.7  # 70% of max
    cleanup_interval_seconds: int = 300  # 5 minutes


@dataclass
class OptimizationConfig:
    """Configuration for performance optimization"""

    enable_memory_optimization: bool = True
    enable_cpu_optimization: bool = True
    enable_network_optimization: bool = True
    enable_automatic_cleanup: bool = True
    enable_adaptive_quality: bool = True
    monitoring_interval_seconds: float = 1.0
    history_retention_minutes: int = 60
    alert_threshold_violations: int = 3  # Alert after 3 consecutive violations


class MemoryOptimizer:
    """Advanced memory usage optimization"""

    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        self.memory_pools = {}
        self.weak_references = weakref.WeakSet()
        self.cleanup_callbacks = []

    def start_memory_tracking(self):
        """Start detailed memory tracking"""
        tracemalloc.start()
        self.logger.info("Memory tracking started")

    def stop_memory_tracking(self):
        """Stop memory tracking and get final statistics"""
        if tracemalloc.is_tracing():
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()

            return {"current_mb": current / 1024 / 1024, "peak_mb": peak / 1024 / 1024}
        return None

    def get_memory_snapshot(self) -> Dict[str, Any]:
        """Get detailed memory usage snapshot"""
        process = psutil.Process()
        memory_info = process.memory_info()

        snapshot = {
            "rss_mb": memory_info.rss / 1024 / 1024,
            "vms_mb": memory_info.vms / 1024 / 1024,
            "percent": process.memory_percent(),
            "available_mb": psutil.virtual_memory().available / 1024 / 1024,
            "total_mb": psutil.virtual_memory().total / 1024 / 1024,
        }

        # Add tracemalloc data if available
        if tracemalloc.is_tracing():
            current, peak = tracemalloc.get_traced_memory()
            snapshot.update(
                {
                    "traced_current_mb": current / 1024 / 1024,
                    "traced_peak_mb": peak / 1024 / 1024,
                }
            )

        return snapshot

    def optimize_memory_usage(self) -> Dict[str, Any]:
        """Perform memory optimization"""
        initial_memory = self.get_memory_snapshot()

        # Force garbage collection
        collected = gc.collect()

        # Clear weak references
        self.weak_references.clear()

        # Run cleanup callbacks
        for callback in self.cleanup_callbacks:
            try:
                callback()
            except Exception as e:
                self.logger.error(f"Error in cleanup callback: {e}")

        # Clear memory pools
        for pool_name, pool in self.memory_pools.items():
            if hasattr(pool, "clear"):
                pool.clear()
                self.logger.debug(f"Cleared memory pool: {pool_name}")

        final_memory = self.get_memory_snapshot()

        optimization_result = {
            "initial_memory_mb": initial_memory["rss_mb"],
            "final_memory_mb": final_memory["rss_mb"],
            "memory_freed_mb": initial_memory["rss_mb"] - final_memory["rss_mb"],
            "objects_collected": collected,
            "cleanup_callbacks_run": len(self.cleanup_callbacks),
        }

        self.logger.info(
            f"Memory optimization completed: freed {optimization_result['memory_freed_mb']:.2f}MB"
        )
        return optimization_result

    def register_cleanup_callback(self, callback: Callable[[], None]):
        """Register callback for memory cleanup"""
        self.cleanup_callbacks.append(callback)

    def create_memory_pool(self, name: str, initial_size: int = 100):
        """Create a managed memory pool"""
        self.memory_pools[name] = deque(maxlen=initial_size)
        return self.memory_pools[name]

    def get_top_memory_consumers(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top memory consuming code locations"""
        if not tracemalloc.is_tracing():
            return []

        snapshot = tracemalloc.take_snapshot()
        top_stats = snapshot.statistics("lineno")

        consumers = []
        for stat in top_stats[:limit]:
            consumers.append(
                {
                    "filename": stat.traceback.format()[0],
                    "size_mb": stat.size / 1024 / 1024,
                    "count": stat.count,
                }
            )

        return consumers


class CPUOptimizer:
    """CPU usage optimization and load balancing"""

    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        self.thread_pools = {}
        self.cpu_intensive_tasks = []
        self.load_balancer = None

    def create_optimized_thread_pool(
        self, name: str, max_workers: Optional[int] = None
    ) -> ThreadPoolExecutor:
        """Create CPU-optimized thread pool"""
        if max_workers is None:
            # Use CPU count but limit to reasonable maximum
            max_workers = min(psutil.cpu_count(logical=False), 8)

        pool = ThreadPoolExecutor(
            max_workers=max_workers, thread_name_prefix=f"OptimizedPool-{name}"
        )

        self.thread_pools[name] = pool
        self.logger.info(
            f"Created optimized thread pool '{name}' with {max_workers} workers"
        )
        return pool

    def get_cpu_metrics(self) -> Dict[str, Any]:
        """Get detailed CPU usage metrics"""
        cpu_percent = psutil.cpu_percent(interval=1, percpu=True)
        cpu_freq = psutil.cpu_freq()

        return {
            "overall_percent": psutil.cpu_percent(),
            "per_core_percent": cpu_percent,
            "core_count": psutil.cpu_count(logical=False),
            "logical_count": psutil.cpu_count(logical=True),
            "frequency_mhz": cpu_freq.current if cpu_freq else None,
            "load_average": os.getloadavg() if hasattr(os, "getloadavg") else None,
        }

    def optimize_cpu_usage(self) -> Dict[str, Any]:
        """Optimize CPU usage across the system"""
        initial_metrics = self.get_cpu_metrics()

        # Adjust thread pool sizes based on current load
        optimizations = []
        for name, pool in self.thread_pools.items():
            if hasattr(pool, "_max_workers"):
                current_workers = pool._max_workers
                optimal_workers = self._calculate_optimal_workers(
                    initial_metrics["overall_percent"]
                )

                if optimal_workers != current_workers:
                    # Note: ThreadPoolExecutor doesn't support dynamic resizing
                    # This would require custom implementation
                    optimizations.append(
                        {
                            "pool": name,
                            "current_workers": current_workers,
                            "recommended_workers": optimal_workers,
                        }
                    )

        # Set process priority if needed
        current_process = psutil.Process()
        if initial_metrics["overall_percent"] > 80:
            try:
                current_process.nice(1)  # Lower priority
                optimizations.append({"action": "lowered_process_priority"})
            except:
                pass

        final_metrics = self.get_cpu_metrics()

        return {
            "initial_cpu_percent": initial_metrics["overall_percent"],
            "final_cpu_percent": final_metrics["overall_percent"],
            "optimizations": optimizations,
        }

    def _calculate_optimal_workers(self, cpu_percent: float) -> int:
        """Calculate optimal number of worker threads based on CPU usage"""
        base_workers = psutil.cpu_count(logical=False)

        if cpu_percent > 80:
            return max(1, base_workers // 2)  # Reduce workers under high load
        elif cpu_percent < 30:
            return min(base_workers * 2, 16)  # Increase workers under low load
        else:
            return base_workers

    def cleanup_thread_pools(self):
        """Clean up all thread pools"""
        for name, pool in self.thread_pools.items():
            pool.shutdown(wait=True)
            self.logger.info(f"Shut down thread pool: {name}")
        self.thread_pools.clear()


class NetworkOptimizer:
    """Network bandwidth management and optimization"""

    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        self.bandwidth_history = deque(maxlen=60)  # 1 minute of history
        self.quality_levels = {
            "high": {"resolution": (1920, 1080), "fps": 30, "quality": 0.9},
            "medium": {"resolution": (1280, 720), "fps": 20, "quality": 0.7},
            "low": {"resolution": (640, 480), "fps": 15, "quality": 0.5},
        }
        self.current_quality = "high"

    def get_network_metrics(self) -> Dict[str, Any]:
        """Get detailed network usage metrics"""
        net_io = psutil.net_io_counters()

        # Calculate bandwidth if I have history
        bandwidth_mbps = 0.0
        if self.bandwidth_history:
            last_measurement = self.bandwidth_history[-1]
            time_diff = time.time() - last_measurement["timestamp"]
            if time_diff > 0:
                bytes_diff = (net_io.bytes_sent + net_io.bytes_recv) - last_measurement[
                    "total_bytes"
                ]
                bandwidth_mbps = (bytes_diff * 8) / (
                    time_diff * 1024 * 1024
                )  # Convert to Mbps

        current_measurement = {
            "timestamp": time.time(),
            "bytes_sent": net_io.bytes_sent,
            "bytes_recv": net_io.bytes_recv,
            "total_bytes": net_io.bytes_sent + net_io.bytes_recv,
            "bandwidth_mbps": bandwidth_mbps,
        }

        self.bandwidth_history.append(current_measurement)

        return {
            "bytes_sent": net_io.bytes_sent,
            "bytes_recv": net_io.bytes_recv,
            "packets_sent": net_io.packets_sent,
            "packets_recv": net_io.packets_recv,
            "current_bandwidth_mbps": bandwidth_mbps,
            "average_bandwidth_mbps": self._calculate_average_bandwidth(),
        }

    def _calculate_average_bandwidth(self) -> float:
        """Calculate average bandwidth over recent history"""
        if len(self.bandwidth_history) < 2:
            return 0.0

        bandwidths = [
            m["bandwidth_mbps"]
            for m in self.bandwidth_history
            if m["bandwidth_mbps"] > 0
        ]
        return sum(bandwidths) / len(bandwidths) if bandwidths else 0.0

    def optimize_network_usage(
        self, max_bandwidth_mbps: float = 50.0
    ) -> Dict[str, Any]:
        """Optimize network usage based on available bandwidth"""
        metrics = self.get_network_metrics()
        current_bandwidth = metrics["average_bandwidth_mbps"]

        optimization_result = {
            "current_bandwidth_mbps": current_bandwidth,
            "max_bandwidth_mbps": max_bandwidth_mbps,
            "previous_quality": self.current_quality,
            "actions_taken": [],
        }

        # Adaptive quality control
        if current_bandwidth > max_bandwidth_mbps * 0.8:  # 80% threshold
            if self.current_quality == "high":
                self.current_quality = "medium"
                optimization_result["actions_taken"].append("reduced_quality_to_medium")
            elif self.current_quality == "medium":
                self.current_quality = "low"
                optimization_result["actions_taken"].append("reduced_quality_to_low")
        elif current_bandwidth < max_bandwidth_mbps * 0.4:  # 40% threshold
            if self.current_quality == "low":
                self.current_quality = "medium"
                optimization_result["actions_taken"].append(
                    "increased_quality_to_medium"
                )
            elif self.current_quality == "medium":
                self.current_quality = "high"
                optimization_result["actions_taken"].append("increased_quality_to_high")

        optimization_result["new_quality"] = self.current_quality
        optimization_result["quality_settings"] = self.quality_levels[
            self.current_quality
        ]

        return optimization_result

    def get_recommended_settings(self) -> Dict[str, Any]:
        """Get recommended settings based on current network conditions"""
        return self.quality_levels[self.current_quality]


class PerformanceMonitor:
    """Comprehensive performance monitoring and alerting"""

    def __init__(self, config: OptimizationConfig, logger=None):
        self.config = config
        self.logger = logger or logging.getLogger(__name__)
        self.metrics_history = deque(
            maxlen=int(
                config.history_retention_minutes
                * 60
                / config.monitoring_interval_seconds
            )
        )
        self.alert_callbacks = []
        self.violation_counts = defaultdict(int)
        self.is_monitoring = False
        self.monitor_thread = None

        # Initialize optimizers
        self.memory_optimizer = MemoryOptimizer(logger)
        self.cpu_optimizer = CPUOptimizer(logger)
        self.network_optimizer = NetworkOptimizer(logger)

    def start_monitoring(self):
        """Start continuous performance monitoring"""
        if self.is_monitoring:
            return

        self.is_monitoring = True
        self.monitor_thread = threading.Thread(
            target=self._monitoring_loop, daemon=True
        )
        self.monitor_thread.start()

        if self.config.enable_memory_optimization:
            self.memory_optimizer.start_memory_tracking()

        self.logger.info("Performance monitoring started")

    def stop_monitoring(self):
        """Stop performance monitoring"""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5.0)

        if self.config.enable_memory_optimization:
            final_stats = self.memory_optimizer.stop_memory_tracking()
            if final_stats:
                self.logger.info(f"Final memory stats: {final_stats}")

        self.cpu_optimizer.cleanup_thread_pools()
        self.logger.info("Performance monitoring stopped")

    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.is_monitoring:
            try:
                metrics = self._collect_metrics()
                self.metrics_history.append(metrics)

                # Check for violations and optimize if needed
                self._check_violations(metrics)

                # Perform automatic cleanup if enabled
                if self.config.enable_automatic_cleanup:
                    self._perform_automatic_cleanup()

                time.sleep(self.config.monitoring_interval_seconds)

            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(self.config.monitoring_interval_seconds)

    def _collect_metrics(self) -> PerformanceMetrics:
        """Collect comprehensive performance metrics"""
        process = psutil.Process()
        net_io = psutil.net_io_counters()
        disk_io = psutil.disk_io_counters()

        return PerformanceMetrics(
            timestamp=time.time(),
            cpu_percent=process.cpu_percent(),
            memory_mb=process.memory_info().rss / 1024 / 1024,
            memory_percent=process.memory_percent(),
            network_bytes_sent=net_io.bytes_sent,
            network_bytes_recv=net_io.bytes_recv,
            disk_io_read=disk_io.read_bytes if disk_io else 0,
            disk_io_write=disk_io.write_bytes if disk_io else 0,
            thread_count=process.num_threads(),
            process_count=len(psutil.pids()),
        )

    def _check_violations(self, metrics: PerformanceMetrics):
        """Check for resource limit violations"""
        violations = []

        # Check memory usage
        if (
            metrics.memory_mb
            > self.config.max_memory_mb * self.config.memory_warning_threshold
        ):
            violations.append("memory")
            self.violation_counts["memory"] += 1
        else:
            self.violation_counts["memory"] = 0

        # Check CPU usage
        if (
            metrics.cpu_percent
            > self.config.max_cpu_percent * self.config.cpu_warning_threshold
        ):
            violations.append("cpu")
            self.violation_counts["cpu"] += 1
        else:
            self.violation_counts["cpu"] = 0

        # Trigger optimizations for persistent violations
        for violation_type in violations:
            if (
                self.violation_counts[violation_type]
                >= self.config.alert_threshold_violations
            ):
                self._trigger_optimization(violation_type, metrics)
                self.violation_counts[violation_type] = 0  # Reset after optimization

    def _trigger_optimization(self, violation_type: str, metrics: PerformanceMetrics):
        """Trigger specific optimization based on violation type"""
        self.logger.warning(f"Performance violation detected: {violation_type}")

        if violation_type == "memory" and self.config.enable_memory_optimization:
            result = self.memory_optimizer.optimize_memory_usage()
            self.logger.info(f"Memory optimization result: {result}")

        elif violation_type == "cpu" and self.config.enable_cpu_optimization:
            result = self.cpu_optimizer.optimize_cpu_usage()
            self.logger.info(f"CPU optimization result: {result}")

        # Notify alert callbacks
        for callback in self.alert_callbacks:
            try:
                callback(violation_type, metrics)
            except Exception as e:
                self.logger.error(f"Error in alert callback: {e}")

    def _perform_automatic_cleanup(self):
        """Perform automatic cleanup based on schedule"""
        current_time = time.time()

        # Check if it's time for cleanup
        if not hasattr(self, "_last_cleanup_time"):
            self._last_cleanup_time = current_time
            return

        if (
            current_time - self._last_cleanup_time
            >= self.config.cleanup_interval_seconds
        ):
            self.logger.debug("Performing automatic cleanup")

            # Trigger garbage collection
            collected = gc.collect()
            if collected > 0:
                self.logger.debug(f"Garbage collection freed {collected} objects")

            self._last_cleanup_time = current_time

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary"""
        if not self.metrics_history:
            return {"error": "No metrics available"}

        recent_metrics = list(self.metrics_history)[-60:]  # Last minute

        summary = {
            "monitoring_duration_minutes": len(self.metrics_history)
            * self.config.monitoring_interval_seconds
            / 60,
            "current_metrics": recent_metrics[-1].__dict__ if recent_metrics else None,
            "averages": {
                "cpu_percent": sum(m.cpu_percent for m in recent_metrics)
                / len(recent_metrics),
                "memory_mb": sum(m.memory_mb for m in recent_metrics)
                / len(recent_metrics),
                "memory_percent": sum(m.memory_percent for m in recent_metrics)
                / len(recent_metrics),
            },
            "peaks": {
                "cpu_percent": max(m.cpu_percent for m in recent_metrics),
                "memory_mb": max(m.memory_mb for m in recent_metrics),
                "memory_percent": max(m.memory_percent for m in recent_metrics),
            },
            "violation_counts": dict(self.violation_counts),
            "optimization_recommendations": self._generate_recommendations(),
        }

        return summary

    def _generate_recommendations(self) -> List[str]:
        """Generate performance optimization recommendations"""
        recommendations = []

        if not self.metrics_history:
            return recommendations

        recent_metrics = list(self.metrics_history)[-10:]  # Last 10 measurements
        avg_memory = sum(m.memory_mb for m in recent_metrics) / len(recent_metrics)
        avg_cpu = sum(m.cpu_percent for m in recent_metrics) / len(recent_metrics)

        if avg_memory > self.config.max_memory_mb * 0.7:
            recommendations.append(
                "Consider reducing buffer sizes or implementing more aggressive cleanup"
            )

        if avg_cpu > self.config.max_cpu_percent * 0.7:
            recommendations.append(
                "Consider reducing processing frequency or optimizing algorithms"
            )

        if len(recent_metrics) > 5:
            memory_trend = recent_metrics[-1].memory_mb - recent_metrics[-5].memory_mb
            if memory_trend > 50:  # 50MB increase
                recommendations.append(
                    "Memory usage is trending upward - check for memory leaks"
                )

        return recommendations

    def add_alert_callback(self, callback: Callable[[str, PerformanceMetrics], None]):
        """Add callback for performance alerts"""
        self.alert_callbacks.append(callback)

    def export_metrics(self, filename: str):
        """Export metrics history to file"""
        try:
            metrics_data = []
            for metric in self.metrics_history:
                metrics_data.append(metric.__dict__)

            with open(filename, "w") as f:
                json.dump(
                    {
                        "export_timestamp": datetime.now().isoformat(),
                        "config": self.config.__dict__,
                        "metrics": metrics_data,
                    },
                    f,
                    indent=2,
                )

            self.logger.info(f"Metrics exported to {filename}")

        except Exception as e:
            self.logger.error(f"Error exporting metrics: {e}")


# Integration helper for main application
class PerformanceManager:
    """Manager class for integrating performance optimization with main application"""

    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        self.monitor: Optional[PerformanceMonitor] = None
        self.config = OptimizationConfig()

    def initialize(self, config: Optional[OptimizationConfig] = None) -> bool:
        """Initialize performance monitoring"""
        try:
            if config:
                self.config = config

            self.monitor = PerformanceMonitor(self.config, self.logger)

            # Add alert callback for logging
            self.monitor.add_alert_callback(self._on_performance_alert)

            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize performance manager: {e}")
            return False

    def start(self) -> bool:
        """Start performance monitoring"""
        if self.monitor:
            self.monitor.start_monitoring()
            return True
        return False

    def stop(self) -> None:
        """Stop performance monitoring"""
        if self.monitor:
            self.monitor.stop_monitoring()

    def get_status(self) -> Optional[Dict[str, Any]]:
        """Get performance status"""
        if self.monitor:
            return self.monitor.get_performance_summary()
        return None

    def optimize_now(self) -> Dict[str, Any]:
        """Trigger immediate optimization"""
        if not self.monitor:
            return {"error": "Monitor not initialized"}

        results = {}

        if self.config.enable_memory_optimization:
            results["memory"] = self.monitor.memory_optimizer.optimize_memory_usage()

        if self.config.enable_cpu_optimization:
            results["cpu"] = self.monitor.cpu_optimizer.optimize_cpu_usage()

        if self.config.enable_network_optimization:
            results["network"] = self.monitor.network_optimizer.optimize_network_usage()

        return results

    def _on_performance_alert(self, violation_type: str, metrics: PerformanceMetrics):
        """Handle performance alerts"""
        self.logger.warning(f"Performance alert: {violation_type} violation detected")
        self.logger.warning(
            f"Current usage - CPU: {metrics.cpu_percent:.1f}%, Memory: {metrics.memory_mb:.1f}MB"
        )


# Example usage and testing
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Create and test performance manager
    config = OptimizationConfig(
        max_memory_mb=1024,  # 1GB limit
        max_cpu_percent=70,
        monitoring_interval_seconds=2.0,
    )

    manager = PerformanceManager()

    try:
        # Initialize and start monitoring
        if manager.initialize(config):
            print("Performance manager initialized successfully")

            if manager.start():
                print("Performance monitoring started")

                # Run for test period
                print("Monitoring performance... Press Ctrl+C to stop")
                while True:
                    time.sleep(10)
                    status = manager.get_status()
                    if status:
                        current = status.get("current_metrics", {})
                        print(
                            f"CPU: {current.get('cpu_percent', 0):.1f}%, "
                            f"Memory: {current.get('memory_mb', 0):.1f}MB"
                        )

                        # Test optimization
                        if current.get("memory_mb", 0) > 500:  # If memory > 500MB
                            print("Triggering optimization...")
                            result = manager.optimize_now()
                            print(f"Optimization result: {result}")

    except KeyboardInterrupt:
        print("\nShutting down performance manager...")
    finally:
        manager.stop()
        print("Performance manager stopped")
