from dbfread import DBF
import statistics as stat
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.colors import LightSource
import numpy as np

upload_speeds = []
download_speeds = []
latencies = []
counter = 0
sum_upload = 0
sum_latency = 0
total_devices = 0

for record in DBF('gps_mobile_tiles.dbf'):
    sum_upload += (record['avg_u_kbps'] / 1000) * record['devices']
    if record['avg_u_kbps'] < 100000:
        for i in range(record['devices']):
            upload_speeds.append(round(record['avg_u_kbps'] / 1000))

    if record['avg_lat_ms'] < 300:
        for i in range(record['devices']):
                latencies.append(record['avg_lat_ms'])
    
    if record['avg_d_kbps'] < 200000:
        for i in range(record['devices']):
            download_speeds.append(round(record['avg_d_kbps'] / 1000))


    


# print("sum upload", sum_upload)
# print("total devices", total_devices)
avg_upload = 11.792259851890899
print("avg upload speed: ", avg_upload)


stdev = 10.511185494679083
print("standard deviation:", stdev)

count, bins, ignored = plt.hist(download_speeds, 100, density=True, align='mid')
plt.title('Download speed distribution')
plt.axis('tight')
plt.xlabel('Download speed (in Mbps)')
plt.show()

plt.savefig('download_speed_distribution.png')
plt.clf()



count, bins, ignored = plt.hist(upload_speeds, 100, density=True, align='mid')
plt.title('Upload speed distribution')
plt.axis('tight')
plt.xlabel('Upload speed (in Mbps)')
plt.show()

plt.savefig('upload_speed_distribution.png')
plt.clf()


count, bins, ignored = plt.hist(latencies, 300, density=True, align='mid')
# x = np.linspace(min(bins), max(bins), 10000)
# pdf = (np.exp(-(np.log(x) - avg_upload)**2 / (2 * stdev**2))
#        / (x * stdev * np.sqrt(2 * np.pi)))

# plt.plot(x, pdf, linewidth=2, color='r')
plt.title('Latency distribution')
plt.xlabel('Latencies (in ms)')
plt.axis('tight')
plt.show()

plt.savefig('latencies_distribution.png')