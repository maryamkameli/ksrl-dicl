import time
import functools
from collections import defaultdict
from contextlib import contextmanager
import json
import csv
from typing import Dict, Any, Optional


class MyDxProfiler:
    
    def __init__(self, enabled: bool = True):
        self.enabled = enabled
        self.timings = defaultdict(list)
        self.call_counts = defaultdict(int)
        self.total_program_time = 0
        self.start_time = None
        self.last_report_time = None
        
    def start_profiling(self):
        # global profiling timer
        if not self.enabled:
            return
            
        self.start_time = time.perf_counter()
        self.last_report_time = self.start_time
        print("Started profiling my_dx methods...")
        
    def stop_profiling(self):
        if not self.enabled or not self.start_time:
            return
            
        self.total_program_time = time.perf_counter() - self.start_time
        print(f"Stopped profiling. Total program time: {self.total_program_time:.2f}s")
            
    @contextmanager
    def time_method(self, method_name: str):
        if not self.enabled:
            yield
            return
            
        start_time = time.perf_counter()
        try:
            yield
        finally:
            end_time = time.perf_counter()
            duration = end_time - start_time
            self.timings[method_name].append(duration)
            self.call_counts[method_name] += 1
    
    def get_stats(self) -> Dict[str, Any]:
        if not self.timings:
            return {"error": "No profiling data collected"}
            
        stats = {}
        total_measured_time = 0
        
        for method_name, times in self.timings.items():
            total_time = sum(times)
            total_measured_time += total_time
            
            stats[method_name] = {
                'total_time': total_time,
                'call_count': self.call_counts[method_name],
                'avg_time': total_time / len(times) if times else 0,
                'min_time': min(times) if times else 0,
                'max_time': max(times) if times else 0,
                'std_time': self._calculate_std(times) if len(times) > 1 else 0,
                'percentage_of_measured': (total_time / max(total_measured_time, 1e-9)) * 100,
            }
            
        # Calculate percentage of total program time
        if self.total_program_time > 0:
            for method_name in stats:
                stats[method_name]['percentage_of_total'] = (
                    stats[method_name]['total_time'] / self.total_program_time
                ) * 100
        else:
            # If profiling is still running, use elapsed time
            elapsed_time = time.perf_counter() - self.start_time if self.start_time else 1
            for method_name in stats:
                stats[method_name]['percentage_of_total'] = (
                    stats[method_name]['total_time'] / elapsed_time
                ) * 100
        
        stats['_summary'] = {
            'total_measured_time': total_measured_time,
            'total_program_time': self.total_program_time,
            'measured_percentage': (total_measured_time / max(self.total_program_time, elapsed_time if self.start_time else 1, 1e-9)) * 100,
            'num_methods_tracked': len([k for k in stats.keys() if k != '_summary']),
            'total_calls': sum(self.call_counts.values())
        }
        
        return stats
    
    def _calculate_std(self, times):
        if len(times) <= 1:
            return 0
        mean = sum(times) / len(times)
        variance = sum((t - mean) ** 2 for t in times) / (len(times) - 1)
        return variance ** 0.5
    
    def print_report(self, detailed: bool = True):
        stats = self.get_stats()
        
        if 'error' in stats:
            print(f"{stats['error']}")
            return
            
        print("\n" + "="*100)
        print("🔍 MY_DX METHODS PERFORMANCE REPORT")
        print("="*100)
        
        summary = stats['_summary']
        elapsed = time.perf_counter() - self.start_time if self.start_time else 0
        current_time = self.total_program_time if self.total_program_time > 0 else elapsed
        
        print(f"📊 Total Program Time: {current_time:.4f}s")
        print(f"⚡ Total my_dx Time: {summary['total_measured_time']:.4f}s")
        print(f"📈 my_dx Coverage: {summary['measured_percentage']:.2f}% of total program time")
        print(f"🔢 Methods Tracked: {summary['num_methods_tracked']}")
        print(f"📞 Total Calls: {summary['total_calls']}")
        print()
        
        if detailed:
            print(f"{'Method':<30} {'Calls':<8} {'Total(s)':<12} {'Avg(s)':<12} {'Std(s)':<12} {'% my_dx':<10} {'% Total':<10}")
            print("-" * 100)
        else:
            print(f"{'Method':<30} {'Calls':<8} {'Total(s)':<12} {'% Total':<10}")
            print("-" * 70)
        
        sorted_methods = sorted(
            [(k, v) for k, v in stats.items() if k != '_summary'],
            key=lambda x: x[1]['total_time'],
            reverse=True
        )
        
        for method_name, method_stats in sorted_methods:
            if detailed:
                print(f"{method_name:<30} "
                      f"{method_stats['call_count']:<8} "
                      f"{method_stats['total_time']:<12.4f} "
                      f"{method_stats['avg_time']:<12.6f} "
                      f"{method_stats['std_time']:<12.6f} "
                      f"{method_stats['percentage_of_measured']:<10.2f} "
                      f"{method_stats.get('percentage_of_total', 0):<10.2f}")
            else:
                print(f"{method_name:<30} "
                      f"{method_stats['call_count']:<8} "
                      f"{method_stats['total_time']:<12.4f} "
                      f"{method_stats.get('percentage_of_total', 0):<10.2f}")
        
        print("\n" + "="*100)
        
        if sorted_methods:
            biggest_bottleneck = sorted_methods[0]
            print(f"🐌 BIGGEST BOTTLENECK: {biggest_bottleneck[0]} ({biggest_bottleneck[1]['percentage_of_total']:.1f}% of total time)")
            
            # Frequency vs time analysis
            avg_times = [(name, stats['avg_time']) for name, stats in sorted_methods]
            avg_times.sort(key=lambda x: x[1], reverse=True)
            print(f"⏱️  SLOWEST AVERAGE: {avg_times[0][0]} ({avg_times[0][1]:.4f}s per call)")
            
            call_counts = [(name, stats['call_count']) for name, stats in sorted_methods]
            call_counts.sort(key=lambda x: x[1], reverse=True)
            print(f"📞 MOST FREQUENT: {call_counts[0][0]} ({call_counts[0][1]} calls)")
            
            print("="*100)
    
    def print_quick_report(self):
        """Print a concise version of the report"""
        self.print_report(detailed=False)
    
    def save_report(self, filepath: str, format: str = 'json'):
        """Save profiling report to file"""
        stats = self.get_stats()
        
        if format.lower() == 'json':
            with open(filepath, 'w') as f:
                json.dump(stats, f, indent=2)
        elif format.lower() == 'csv':
            csv_filepath = filepath.replace('.json', '.csv') if filepath.endswith('.json') else filepath
            with open(csv_filepath, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Method', 'Calls', 'Total_Time', 'Avg_Time', 'Std_Time', 
                               'Percentage_Measured', 'Percentage_Total'])
                
                for method_name, method_stats in stats.items():
                    if method_name != '_summary':
                        writer.writerow([
                            method_name,
                            method_stats['call_count'],
                            method_stats['total_time'],
                            method_stats['avg_time'],
                            method_stats['std_time'],
                            method_stats['percentage_of_measured'],
                            method_stats.get('percentage_of_total', 0)
                        ])
        
        print(f"💾 Profiling report saved to: {filepath}")
    
    def periodic_report(self, interval_seconds: float = 300):
        """Print a report if enough time has passed since last report"""
        if not self.enabled or not self.start_time:
            return
            
        current_time = time.perf_counter()
        if self.last_report_time is None:
            self.last_report_time = self.start_time
            
        if current_time - self.last_report_time >= interval_seconds:
            print(f"\n📊 PERIODIC REPORT (after {current_time - self.start_time:.1f}s)")
            self.print_quick_report()
            self.last_report_time = current_time
    
    def reset(self):
        """Reset all profiling data"""
        self.timings = defaultdict(list)
        self.call_counts = defaultdict(int)
        self.total_program_time = 0
        self.start_time = None
        self.last_report_time = None
        print("🔄 Profiler reset")
    
    def enable(self):
        """Enable profiling"""
        self.enabled = True
        print("Profiler enabled")
    
    def disable(self):
        """Disable profiling"""
        self.enabled = False
        print("Profiler disabled")


# Global profiler instance - import this in your main file
dx_profiler = MyDxProfiler()


# Convenience functions
def start_profiling():
    dx_profiler.start_profiling()

def stop_profiling():
    dx_profiler.stop_profiling()

def time_method(method_name: str):
    return dx_profiler.time_method(method_name)

def print_report():
    dx_profiler.print_report()

def save_report(filepath: str, format: str = 'json'):
    dx_profiler.save_report(filepath, format)