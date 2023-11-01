import logging
import datetime
import threading
import time
import psutil
import GPUtil

logger = logging.getLogger('my_logger')
logger.setLevel(logging.INFO)

log_file_name = datetime.datetime.now().strftime('System_Usage_%d-%m-%Y.log')
file_handler = logging.FileHandler(log_file_name)
file_handler.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
logger.addHandler(file_handler)

exit_flag = threading.Event()


def create_new_log_file():
    while not exit_flag.is_set():
        current_time = datetime.datetime.now()
        if current_time.hour == 11 and current_time.minute == 32 and current_time.second == 0:
            new_log_file_name = current_time.strftime('System_Usage_%d-%m-%Y_%H-%M-%S.log')

            for handler in logger.handlers:
                handler.close()

            file_handler = logging.FileHandler(new_log_file_name)
            file_handler.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
            logger.addHandler(file_handler)

            logger.info('Created a new log file: %s', new_log_file_name)

        time.sleep(1)


def get_gpu_info():
    try:
        gpus = GPUtil.getGPUs()
        gpu_usage = gpus[0].load * 100
        gpu_temp = gpus[0].temperature
        return gpu_usage, gpu_temp
    except (IndexError, GPUtil.GPSError):
        return None, None


def display_usage(cpu_usage, mem_usage, upload_usage, download_usage, disk_usage, gpu_usage, gpu_temperature):
    log_message = f"CPU usage: {cpu_usage:.1f}% Memory usage: {mem_usage:.1f}% Upload usage: {upload_usage:.1f} MB Download usage: {download_usage:.1f} MB Disk usage: {disk_usage:.1f}% GPU usage: {gpu_usage:.1f}% GPU temperature: {gpu_temperature:.1f}°C"
    logger.info(log_message)


def monitor_system_usage():
    try:
        while not exit_flag.is_set():

            cpu_usage = psutil.cpu_percent()
            mem_usage = psutil.virtual_memory().percent
            upload_usage = (psutil.net_io_counters().bytes_sent / 1048576)
            download_usage = (psutil.net_io_counters().bytes_recv / 1048576)
            disk_usage = psutil.disk_usage('/').percent
            gpu = GPUtil.getGPUs()[0]
            gpu_usage = gpu.load * 100
            gpu_temperature = gpu.temperature

            display_usage(cpu_usage, mem_usage, upload_usage, download_usage, disk_usage, gpu_usage, gpu_temperature)
            time.sleep(1)

    except KeyboardInterrupt:
        exit_flag.set()


if __name__ == "__main__":
    thread_log = threading.Thread(target=create_new_log_file)
    thread_log.start()

    thread_monitor = threading.Thread(target=monitor_system_usage)
    thread_monitor.start()

    try:
        while not exit_flag.is_set():
            time.sleep(1)
    except KeyboardInterrupt:
        exit_flag.set()

    thread_log.join()
    thread_monitor.join()
