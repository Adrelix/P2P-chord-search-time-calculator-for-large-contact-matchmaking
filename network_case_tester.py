import matplotlib
import numpy as np
import math
from random import sample
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.colors import LightSource
from dbfread import DBF
from statistics import mean



# amount of iteration for each combination
i_tot = 3

# Based on a tcp and tls handshake protocol. Six (one-way) exchanges is required before the connection is established and secure
# https://learning.oreilly.com/library/view/high-performance-browser/9781449344757/ch04.html#TLS_HANDSHAKE
connection_protocol_multiplier = 3


TRACK_NOT_CONNECTED = "NOT_CONNECTED                "
TRACK_SEARCHING_FOR_NODE = "SEARCHING_FOR_NODE           "
TRACK_ESTABLISHING_CONNECTION = "ESTABLISHING_CONNECTION      "
TRACK_WAITING_FOR_TRANSFER_UP = "WAITING_FOR_TRANSFER_UP      "
TRACK_WAITING_FOR_TRANSFER_DOWN = "WAITING_FOR_TRANSFER_DOWN    "
TRACK_TRANSFERING_UP = "TRANSFERING_UP               "
TRACK_TRANSFERING_DOWN = "TRANSFERING_DOWN             "
TRACK_COMPARING_LIST = "COMPARING_LIST               "
TRACK_DONE = "DONE                         "

CLIENT_CREATING_HASH_TABLE = "CREATING_HASH_TABLE              "
CLIENT_SENDING_REQUESTS_TO_P2P_NETWORK = "SENDING_REQUESTS_TO_P2P_NETWORK  "
CLIENT_WAITING_FOR_TRANSFER = "WAITING_FOR_TRANSFER             "
CLIENT_DONE = "DONE                             "


x = []
y = []
z = []



class track:
    def __init__(self, track_id, total_time, track_status, find_node_time, establish_connection_time, search_contacts_time, client_to_node_upload_time, node_to_client_upload_time):
        self.total_time = total_time
        self.time_left = total_time
        self.track_id = track_id
        self.track_status = track_status
        self.find_node_time = find_node_time
        self.search_contacts_time = search_contacts_time
        self.establish_connection_time = establish_connection_time
        self.client_to_node_upload_time = client_to_node_upload_time
        self.node_to_client_upload_time = node_to_client_upload_time

class network_case:
    def __init__(self, latencies, upload_speeds):
        self.latencies = latencies
        self.upload_speeds = upload_speeds
        self.latencies_mean = round(mean(latencies))
        self.upload_speed_mean = round(mean(upload_speeds))
        self.result_y = []
        self.result_x = []

class database_premis:
    def __init__(self, amount_of_users, optimal_package_distribution):
        self.amount_of_users = amount_of_users
        self.optimal_package_distribution = optimal_package_distribution
        
# Read in data from Ookla-open-data database to create statistics regarding latencies, upload speeds and download speeds
# Data is from Q1 2020, and is based on the average of 604m*604m areas with 'devices' amount of devices.
# We sort out latencies and upload speeds that are extremely high (for latencies) and low (for upload speeds) as these should in practise be counted as dead nodes.
upload_speeds = []
download_speeds = []
latencies = []
latency_minimum = 1
upload_speed_minimum = 0.1


latency_minimum = 5
latency_maximum = 500
upload_speed_minimum = 0.1
download_speed_minimum = 0.1
for record in DBF('gps_mobile_tiles.dbf'):
    for i in range(record['devices']):
        if record['avg_u_kbps'] > upload_speed_minimum: #if above 0.1 mbps
            upload_speeds.append(record['avg_u_kbps']/ 1000)
        if record['avg_d_kbps'] > download_speed_minimum: #if above 0.1 mbps
            upload_speeds.append(record['avg_d_kbps']/ 1000)
        if record['avg_lat_ms'] < latency_maximum and latency_minimum < record['avg_lat_ms'] : #if below 500ms
            latencies.append(record['avg_lat_ms'])

upload_speeds.sort()
latencies.sort()
latencies.reverse()

latencies_percentiles = []
for i in range(0, len(latencies)-(len(latencies)%6), math.floor(len(latencies)/6)):
    chunk = latencies[i:i +  math.floor(len(latencies)/6)]
    latencies_percentiles.append(chunk)

upload_speed_percentiles = []
for i in range(0, len(upload_speeds)-(len(upload_speeds)%6), math.floor(len(upload_speeds)/6)):
    chunk = upload_speeds[i:i +  math.floor(len(upload_speeds)/6)]
    upload_speed_percentiles.append(chunk)

network_cases = []
for i in range(6):
    network_cases.append(network_case(latencies_percentiles[i], upload_speed_percentiles[i]))



premises = []
premises.append(database_premis(1000000, 4))
premises.append(database_premis(10000000, 36))
premises.append(database_premis(50000000, 64))
premises.append(database_premis(100000000, 90))
premises.append(database_premis(500000000, 120))
premises.append(database_premis(1000000000, 250))


result_x = []
result_y = []

for premis in premises:
    database_size = premis.amount_of_users
    amount_of_packages = premis.optimal_package_distribution 

    for case in network_cases:
        latency_minimum = 1
        upload_speed_minimum = 0.1
        # Set Values
        # All times are in milliseconds
        amount_of_nodes = database_size
        package_size = math.floor(database_size/amount_of_packages)
        contact_book_size = 1000
        hash_table_creation_time = 10
        time_to_send_requests = amount_of_packages

        results = []
        for i in range(i_tot):

            # Time required to search through the uploaded contactbook and compare it to the nodes information
            # Based on our experiment (see xxxx)
            search_time_mean = package_size * 0.0009 + 125.666
            search_time_spread = package_size * 0.000009 + 6.1168
            search_times = np.random.normal(
                search_time_mean, search_time_spread, amount_of_packages)

            # Normal distribution of latencies
            latencies = case.latencies
            # Normal distribution of upload speed
            upload_speed = case.latencies
            # Normal distribution of path lengths based on
            # https://cs.nyu.edu/courses/fall18/CSCI-GA.3033-002/papers/chord-ton.pdf
            path_lengths = np.random.normal(np.log2(
                database_size) / 2, np.log2(database_size) / 6, math.floor(amount_of_packages))

            for i in range(len(path_lengths)):
                if path_lengths[i] < 2:
                    path_lengths[i] = 2

            tracks = []
            for track_id in range(amount_of_packages):
                # Takes path length and multiplies with the time it takes to connect to the next node with a TCP protocol.
                # Sending request after a connection been made is neglectable

                find_node_time = sum(sample(
                    latencies, math.floor(path_lengths[track_id]))) * connection_protocol_multiplier

                search_contacts_time = search_times[track_id]

                node_latency = sample(latencies, 1)[0]
                node_upload_speed = sample(upload_speed, 1)[0]
                # Time required to establish a TCP connection to the final node
                establish_connection_time = node_latency * \
                    connection_protocol_multiplier

                # Calculate the maximum TCP throughput with standard window size 65536 Bytes = 524288 bits
                max_TCP_throughput = 0.524288 / (node_latency / 1000)

                # Upload speed is capped by max_TCP_thprughput if it's higher than upload_speed[track_id]
                if node_upload_speed < max_TCP_throughput:
                    node_upload_speed = max_TCP_throughput
                node_to_client_upload_time = (
                    1000 * (contact_book_size * 256) / amount_of_packages) / (node_upload_speed * 1000000)
                client_to_node_upload_time = (
                    1000 * (contact_book_size * 256)) / (node_upload_speed * 1000000)

                # The total estimated time each node require (if assumed it never needs to wait for the client)
                total_time = math.floor(find_node_time + establish_connection_time +
                                        node_to_client_upload_time + search_contacts_time + client_to_node_upload_time)
                track_status = "NOT_CONNECTED"
                new_track = track(track_id, total_time, track_status, find_node_time, establish_connection_time,
                                  search_contacts_time, client_to_node_upload_time, node_to_client_upload_time)
                tracks.append(new_track)

            ms_count = 0
            client_status = "STARTING_UP"

            def update_track_status():
                # Import global variables and flags
                global tracks
                global client_status
                global hash_table_creation_time
                global time_to_send_requests

                global TRACK_NOT_CONNECTED
                global TRACK_SEARCHING_FOR_NODE
                global TRACK_ESTABLISHING_CONNECTION
                global TRACK_WAITING_FOR_TRANSFER_UP
                global TRACK_WAITING_FOR_TRANSFER_DOWN
                global TRACK_TRANSFERING_UP
                global TRACK_TRANSFERING_DOWN
                global TRACK_COMPARING_LIST
                global TRACK_DONE
                global CLIENT_CREATING_HASH_TABLE
                global CLIENT_SENDING_REQUESTS_TO_P2P_NETWORK
                global CLIENT_WAITING_FOR_TRANSFER
                global CLIENT_DONE

                # Initialize client
                if ms_count < hash_table_creation_time:
                    client_status = CLIENT_CREATING_HASH_TABLE
                if hash_table_creation_time <= ms_count and ms_count < hash_table_creation_time + time_to_send_requests:
                    client_status = CLIENT_SENDING_REQUESTS_TO_P2P_NETWORK
                    # Initialize tracks
                    tracks[ms_count-hash_table_creation_time].track_status = TRACK_SEARCHING_FOR_NODE
                if client_status == CLIENT_SENDING_REQUESTS_TO_P2P_NETWORK and ms_count > hash_table_creation_time + time_to_send_requests:
                    client_status = CLIENT_WAITING_FOR_TRANSFER

                # Update client status

                # Update tracks status
                for track in tracks:

                    if track.track_status == TRACK_TRANSFERING_DOWN:
                        track.time_left -= 1
                        if track.time_left < track.total_time - track.find_node_time - track.establish_connection_time - track.client_to_node_upload_time - track.search_contacts_time - track.node_to_client_upload_time:
                            track.track_status = TRACK_DONE

                    if track.track_status == TRACK_COMPARING_LIST:
                        track.time_left -= 1
                        if track.time_left < track.total_time - track.find_node_time - track.establish_connection_time - track.client_to_node_upload_time - track.search_contacts_time:
                            track.track_status = TRACK_WAITING_FOR_TRANSFER_DOWN

                    if track.track_status == TRACK_TRANSFERING_UP:
                        track.time_left -= 1
                        if track.time_left < track.total_time - track.find_node_time - track.establish_connection_time - track.client_to_node_upload_time:
                            track.track_status = TRACK_COMPARING_LIST
                            client_status = CLIENT_WAITING_FOR_TRANSFER

                    if track.track_status == TRACK_ESTABLISHING_CONNECTION:
                        track.time_left -= 1
                        if track.time_left < track.total_time - track.find_node_time - track.establish_connection_time:
                            track.track_status = TRACK_WAITING_FOR_TRANSFER_UP

                    if track.track_status == TRACK_SEARCHING_FOR_NODE:
                        track.time_left -= 1
                        if track.time_left < track.total_time - track.find_node_time:
                            track.track_status = TRACK_ESTABLISHING_CONNECTION

                # Connect client to track if both are ready (prioritizes upload to node as it potentionally bottlenecks the system if left waiting)
                if client_status == CLIENT_WAITING_FOR_TRANSFER:
                    for track in tracks:
                        if track.track_status == TRACK_WAITING_FOR_TRANSFER_UP:
                            if client_status == CLIENT_WAITING_FOR_TRANSFER:
                                client_status = (
                                    "TRANSFERING UP BETWEEN CLIENT AND TRACK #" + str(track.track_id))
                                track.track_status = TRACK_TRANSFERING_UP

                    for track in tracks:
                        if track.track_status == TRACK_WAITING_FOR_TRANSFER_DOWN:
                                track.track_status = TRACK_TRANSFERING_DOWN

                    all_tracks_done = True
                    for track in tracks:
                        if track.track_status != TRACK_DONE:
                            all_tracks_done = False

                    if all_tracks_done:
                        client_status = CLIENT_DONE

            while client_status != CLIENT_DONE:
                ms_count += 1
                update_track_status()

            results.append(ms_count)

        average = sum(results)/len(results)

        case.result_x.append(database_size/1000000)
        case.result_y.append(average)

        print("Amount of users:", database_size /
          1000000, "Time:", average)




tableau20 = [(31, 119, 180), (174, 199, 232), (255, 127, 14), (255, 187, 120),    
             (44, 160, 44), (152, 223, 138), (214, 39, 40), (255, 152, 150),    
             (148, 103, 189), (197, 176, 213), (140, 86, 75), (196, 156, 148),    
             (227, 119, 194), (247, 182, 210), (127, 127, 127), (199, 199, 199),    
             (188, 189, 34), (219, 219, 141), (23, 190, 207), (158, 218, 229)]    

for i in range(len(tableau20)):    
    r, g, b = tableau20[i]    
    tableau20[i] = (r / 255., g / 255., b / 255.)    

labels = [1000000, ]

fig = plt.figure()

plt.ylabel('Time (in ms)')
plt.xlabel('Amount of users (in millions)')

s = 'U:' +  str(network_cases[0].upload_speed_mean) + ' L:' + str(network_cases[0].latencies_mean)
plt.plot(network_cases[0].result_x, network_cases[0].result_y, color = tableau20[0], marker = 'o', label = s)
s = 'U:' +  str(network_cases[1].upload_speed_mean) + ' L:' + str(network_cases[1].latencies_mean)
plt.plot(network_cases[1].result_x, network_cases[1].result_y, color = tableau20[2], marker = 'o', label = s)
s = 'U:' +  str(network_cases[2].upload_speed_mean) + ' L:' + str(network_cases[2].latencies_mean)
plt.plot(network_cases[2].result_x, network_cases[2].result_y, color = tableau20[4], marker = 'o', label = s)
s = 'U:' +  str(network_cases[3].upload_speed_mean) + ' L:' + str(network_cases[3].latencies_mean)
plt.plot(network_cases[3].result_x, network_cases[3].result_y, color = tableau20[6], marker = 'o', label = s)
s = 'U:' +  str(network_cases[4].upload_speed_mean) + ' L:' + str(network_cases[4].latencies_mean)
plt.plot(network_cases[4].result_x, network_cases[4].result_y, color = tableau20[8], marker = 'o', label = s)
s = 'U:' +  str(network_cases[5].upload_speed_mean) + ' L:' + str(network_cases[5].latencies_mean)
plt.plot(network_cases[5].result_x, network_cases[5].result_y, color = tableau20[10], marker = 'o', label = s)


plt.title('Performance with variance in network quality')
plt.legend()
plt.show()
plt.savefig('plot.png')