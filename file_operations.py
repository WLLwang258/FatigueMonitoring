import datetime
import json

class FileOperations:
    def __init__(self, log_file_path="./log/detect_data.txt"):
        self.log_file_path = log_file_path
        self.__initialize_log_file()

    def __initialize_log_file(self):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = {
            "timestamp": timestamp,
            "message": "Log file initialized"
        }
        self.__write_log_entry(log_entry)

    def log_program_error(self, message):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = {
            "timestamp": timestamp,
            "program_status": "error",
            "message": message
        }
        self.__write_log_entry(log_entry)

    def log_program_start(self, success: bool):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status = "normal" if success else "error"
        log_entry = {
            "timestamp": timestamp,
            "message": f"Program started",
            "program_status": status
        }
        self.__write_log_entry(log_entry)

    def log_fatigue_detection(self, behavior):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = {
            "timestamp": timestamp,
            "message": f"Fatigue detected",
            "program_status": "normal",
            "behavior": behavior
        }
        self.__write_log_entry(log_entry)

    def log_fatigue_recovery(self):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = {
            "timestamp": timestamp,
            "message": "Fatigue recovery, Driver has resumed normal driving",
            "program_status": "normal",
            "behavior": "normal driving"
        }
        self.__write_log_entry(log_entry)

    def __write_log_entry(self, log_entry):
        with open(self.log_file_path, 'a') as file:
            file.write(json.dumps(log_entry) + "\n")

    def __del__(self):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = {
            "timestamp": timestamp,
            "message": "Program ended"
        }
        self.__write_log_entry(log_entry)