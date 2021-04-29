from dbfread import DBF
import statistics as stat
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.colors import LightSource
import numpy as np

upload_speeds = []
latencies = []
counter = 0
sum_upload = 0
sum_latency = 0
total_devices = 0
hacks= []

for record in DBF('gps_mobile_tiles.dbf'):
    sum_upload += (record['avg_u_kbps'] / 1000) * record['devices']
    for i in range(record['devices']):
        hacks.append(int(round(record['avg_u_kbps'])))
    upload_speeds.append(record['avg_u_kbps'] / 1000)
    latencies.append(record['avg_lat_ms'])

    


# print("sum upload", sum_upload)
# print("total devices", total_devices)
avg_upload = 11.792259851890899
print("avg upload speed: ", avg_upload)


stdev = 10.511185494679083
print("standard deviation:", stdev)

count, bins, ignored = plt.hist(hacks, 100, density=True, align='mid')
# x = np.linspace(min(bins), max(bins), 10000)
# pdf = (np.exp(-(np.log(x) - avg_upload)**2 / (2 * stdev**2))
#        / (x * stdev * np.sqrt(2 * np.pi)))

# plt.plot(x, pdf, linewidth=2, color='r')
plt.axis('tight')
plt.show()

plt.savefig('dist.png')