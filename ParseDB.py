import re
import time
import influxdb_client
import datetime

bucket = "Parse"
token = "Qpt6yYtZmBBr2a9NZQ-iiB3HQTri3AQSr_XfM0-jr6hPqYIE02pwwZmNUlOqCmEe3FRWpYV7kcV0QALG0DI6aQ=="
org = "ESD_B2"
client = influxdb_client.InfluxDBClient(url="http://localhost:8086", token=token, org=org)
write_api = client.write_api()

pattern = re.compile(r'CPU usage: (\d+\.\d+)% Memory usage: (\d+\.\d+)% Upload usage: (\d+\.\d+) MB Download usage: (\d+\.\d+) MB Disk usage: (\d+\.\d+)% GPU usage: (\d+\.\d+)% GPU temperature: (\d+\.\d+)°C')

log_file = datetime.datetime.now().strftime('System_Usage_%d-%m-%Y.log')

try:
    while True:
        current_time = datetime.datetime.now()
        if current_time.hour == 11 and current_time.minute == 32 and current_time.second == 0:

            log_file = current_time.strftime('System_Usage_%d-%m-%Y_%H-%M-%S.log')

        with open(log_file, 'r') as file:
            file.seek(0, 2)
            while True:
                where = file.tell()
                line = file.readline()
                if not line:
                    time.sleep(0.1)
                    file.seek(where)
                else:
                    match = pattern.search(line)
                    if match:
                        cpu_usage, mem_usage, upload_usage, download_usage, disk_usage, gpu_usage, gpu_temp = map(float, match.groups())

                        point = influxdb_client.Point('system_usage') \
                            .field('cpu_usage', cpu_usage) \
                            .field('mem_usage', mem_usage) \
                            .field('upload_usage', upload_usage) \
                            .field('download_usage', download_usage) \
                            .field('disk_usage', disk_usage) \
                            .field('gpu_usage', gpu_usage) \
                            .field('gpu_temperature', gpu_temp)

                        write_api.write(bucket=bucket, record=point)
except KeyboardInterrupt:
    pass
