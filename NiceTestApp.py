"""
NiceTestApp - A system monitoring utility

This script collects system information and outputs to console and optionally a log.

Features:
- Retrieve system information (computer name, memory, CPU, disks, processes)
- Display formatted output to the console
- Optionally log output to a file (NiceTestApp.log)

Usage:
    python NiceTestApp.py [-loginfo]

Author: Jim Watson
Date: 2/12/2025
"""
import argparse
import logging
import logging.handlers
import os
import platform
import sys
import time

import psutil

class NiceTestApp:
    """
    A class to retrieve, display, and optionally log system information.

    This class collects various system details, including:
    - Computer name
    - Total physical memory
    - Number of physical and logical processors
    - Number of hard disks
    - Top 5 CPU-consuming processes

    The retrieved information is displayed in the console and can optionally be logged to a file.
    """
    def __init__(self):
        """
        Initializes the NiceTestApp class, retrieves system information,
        formats the output, prints it to the console, and logs it if specified.
        """
        args = self.parse_arguments()

        # Execute system info function
        system_info = self.get_system_info()

        # Generate formatted output
        formatted_output = self.constuct_output(system_info)

        # Print out system info
        print(formatted_output)

        if args.loginfo:
            self.log_output(formatted_output)


    def constuct_output(self, system_info):
        """
        Creates a standard output for use by the print and log functions

        Arguments:
            
        system_info (dict):
            Dictionary of results containing the system information

        Returns:
            str: Formatted string for output to console and or log
        """

        # Prepare output as a formatted string
        formatted_message = (
            f"Computer Name: {system_info['computer_name']}\n"
            f"Total Physical Memory: {system_info['total_physical_memory_gb']} Gb\n"
            f"Total Number of Physical Processors: {system_info['physical_processors']}\n"
            f"Total Number of Cores: {system_info['logical_processors']}\n"
            f"Total Number of Hard Disks: {system_info['number_of_hard_disks']}\n"
            f"Top 5 processes in terms of CPU:\n"
        )

        for idx, (name, cpu) in enumerate(system_info['top_5_cpu_processes'], start=1):
            formatted_message += f"     {idx}. {name} - {cpu:.0f}%\n"

        return formatted_message


    def get_execution_dir(self):
        """
        Returns the directory where the script or executable is running.

        Returns:
            str: Path the executable or script is being run from
        """
        if getattr(sys, 'frozen', False):  # Running as a bundled executable
            return os.path.dirname(sys.executable)

        if '__file__' in globals():  # Running as a Python script
            return os.path.dirname(os.path.abspath(__file__))

        return os.getcwd()


    def get_system_info(self):
        """
        Retrieves the information about the local computer

        Returns:
            dict: A dictionary containing system details.
        """

        # Retrieve System Information
        system_info = {
            "computer_name": platform.node(),
            "total_physical_memory_gb": round(psutil.virtual_memory().total / (1024**3), 2),
            "physical_processors": psutil.cpu_count(logical=False),  # Only physical CPUs
            "logical_processors": psutil.cpu_count(logical=True),  # Includes hyper-threaded cores
            "number_of_hard_disks": len(
                [disk for disk in psutil.disk_partitions() if 'fixed' in disk.opts.lower()]
            ),
            "top_5_cpu_processes": self.get_system_processes()
        }

        return system_info


    def get_system_processes(self):
        """
        Get Top 5 Processes by CPU Usage

        Returns:
            list: A list of the top five processes in terms of CPU usage
        """
        num_logical_processors = psutil.cpu_count(logical=True)

        # Initialize CPU usage measurement
        for proc in psutil.process_iter(['name']):
            proc.cpu_percent(interval=None)

        time.sleep(1)  # Allow CPU measurement to update

        # Collect updated CPU usage
        processes = []
        for proc in psutil.process_iter(['name', 'cpu_percent']):
            try:
                cpu_usage = proc.info['cpu_percent'] / num_logical_processors  # Normalize CPU %
                processes.append((proc.info['name'], cpu_usage))
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        top_five_procs = sorted(processes, key=lambda x: x[1], reverse=True)[:5]

        return top_five_procs


    def log_output(self, formatted_output):
        """
        Outputs the system information to the NiceTestApp.log file

        Arguments:
            
        system_info (dict):
            Dictionary of results containing the system information
        """

        # Get the script or .exe directory
        log_dir = self.get_execution_dir()

        # Set the logging path
        log_path = os.path.join(log_dir, "NiceTestApp.log")

        # Create the log format
        log_format = (
            "[%(asctime)s] "
            "[%(module)-12s : %(lineno)-3d] "
            "[%(levelname)-8s] "
            "[%(process)d] "
            "%(message)s"
        )

        # Set basic logging config
        logging.basicConfig(
            filename=log_path,
            level=logging.INFO,
            format=log_format,
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        logging.info("\n%s", formatted_output)


    def parse_arguments(self):
        """
        Parses command-line arguments for the application.

        Returns:
            argparse.Namespace: Parsed arguments.
        """
        parser = argparse.ArgumentParser(
            prog="Nice Test App",
            description="A simple Python application that outputs system info, optionally to a log."
        )

        parser.add_argument(
            "-loginfo",
            action="store_true",
            help="If specified, the info will also be written to a log file: NiceTestApp.log",
            required=False
        )

        return parser.parse_args()


if __name__ == "__main__":
    NiceTestApp()
