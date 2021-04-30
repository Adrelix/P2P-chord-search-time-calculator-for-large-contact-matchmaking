import matplotlib
import numpy as np
import math
from random import sample
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.colors import LightSource
from dbfread import DBF

# amount of users in millions
database_size = 10

# amount of packages
amount_of_packages = 34

# amount of iteration for each combination
i_tot = 2

# range presentated in graph (to avoid extremely high/low times ruining graph)
graph_cap = 3000
graph_min = 0

# Boundaries
latency_minimum = 5
latency_maximum = 500
upload_speed_minimum = 0.1
download_speed_minimum = 0.1

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

best_times = []
bestX = []
bestY = []
bestZ = []

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

class best_line:
    def __init__(self, amount_of_packages, amount_of_users, time):
        self.amount_of_packages = amount_of_packages
        self.amount_of_users = amount_of_users
        self.time = time



# Read in data from Ookla-open-data database to create statistics regarding latencies, upload speeds and download speeds
# Data is from Q1 2020, and is based on the average of 604m*604m areas with 'devices' amount of devices.
# We sort out latencies and upload speeds that are extremely high (for latencies) and low (for upload speeds) as these should in practise be counted as dead nodes.
upload_speeds = []
download_speeds = []
latencies = []
for record in DBF('gps_mobile_tiles.dbf'):
    for i in range(record['devices']):
        if record['avg_u_kbps'] > upload_speed_minimum: #if above 0.1 mbps
            upload_speeds.append(record['avg_u_kbps']/ 1000)
        if record['avg_d_kbps'] > download_speed_minimum: #if above 0.1 mbps
            upload_speeds.append(record['avg_d_kbps']/ 1000)
        if record['avg_lat_ms'] < latency_maximum: #if below 500ms
            latencies.append(record['avg_lat_ms'])


upload_speeds.sort()
latencies.sort()

latencies_percentiles = []
for i in range(0, len(latencies)-(len(latencies)%10), math.floor(len(latencies)/10)):
    chunk = latencies[i:i +  math.floor(len(latencies)/10)]
    latencies_percentiles.append(chunk)

upload_speed_percentiles = []
for i in range(0, len(upload_speeds)-(len(upload_speeds)%10), math.floor(len(upload_speeds)/10)):
    chunk = upload_speeds[i:i +  math.floor(len(upload_speeds)/10)]
    upload_speed_percentiles.append(chunk)



for l_perc_id in range (len(latencies_percentiles)):
    #latencies = latencies_percentiles[l_perc_id]

    for u_spd_id in range (len(upload_speed_percentiles)):
        #upload_speeds = upload_speed_percentiles[u_spd_id]

        amount_of_nodes = database_size
        package_size = math.floor(database_size/amount_of_packages)
        time_to_send_requests = amount_of_packages

        #Based on our experiment (see xxx)
        hash_table_creation_time = 10
        
        #contact book size is based on the average amount of contacts a person has on their phone
        # according to http://web.mit.edu/bentley/www/papers/phonebook-CHI15.pdf
        contact_book_size = 308

 
        # Time required to search through the uploaded contactbook and compare it to the nodes information
        # Based on our experiment (see xxxx)
        search_time_mean = package_size * 0.0009 + 125.666
        search_time_spread = package_size * 0.000009 + 6.1168
        search_times = np.random.normal(
            search_time_mean, search_time_spread, amount_of_packages)


        # Distribution of path lengths based on
        # https://cs.nyu.edu/courses/fall18/CSCI-GA.3033-002/papers/chord-ton.pdf
        path_lengths = np.random.normal(np.log2(
            database_size) / 2, np.log2(database_size) / 6, math.floor(amount_of_packages))
        
        
        for i in range(len(path_lengths)):
            if path_lengths[i] < 2:
                path_lengths[i] = 2


        results = []
        for i in range(i_tot):
            tracks = []
            for track_id in range(amount_of_packages):
                # Takes path length and multiplies with the time it takes to connect to the next node with a TCP protocol.
                # Sending request after a connection been made is neglectable
                node_latency = sample(latencies, 1)[0]
                node_upload_speed = sample(upload_speeds, 1)[0]


                find_node_time = sum(sample(
                    latencies, math.floor(path_lengths[track_id]))) * connection_protocol_multiplier

                search_contacts_time = search_times[track_id]

                # Time required to establish a TCP connection to the final node
                establish_connection_time = node_latency * \
                    connection_protocol_multiplier

                # Calculate the maximum TCP throughput with standard window size 65536 Bytes = 524288 bits
                max_TCP_throughput = 0.524288 / (node_latency / 1000)

                # Upload speed is capped by max_TCP_thprughput if it's higher than node_upload_speed
                if node_upload_speed < max_TCP_throughput:
                    node_upload_speed = max_TCP_throughput

                #Calculating upload time
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

                # Connect client to track if both are ready, we are never close to caping download speed so it's free to engage whenever it is ready
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

        if average > graph_cap:
            average = graph_cap
        y.append(u_spd_id*10)
        x.append(l_perc_id*10)
        z.append(average)



X = np.reshape(x, (len(np.unique(x)), len(np.unique(y))))
Y = np.reshape(y, (len(np.unique(x)), len(np.unique(y))))
Z = np.reshape(z, (len(np.unique(x)), len(np.unique(y))))

fig = plt.figure()
ax = fig.add_subplot(projection='3d')

ax.set_ylabel('Network upload speed percentile')
ax.set_xlabel('Network latency speed percentile')
ax.set_zlabel('Time (in ms)')

ls = LightSource(270, 45)
# To use a custom hillshading mode, override the built-in shading and pass
# in the rgb colors of the shaded surface calculated from "shade".
rgb = ls.shade(Z, cmap=cm.gist_earth, norm=matplotlib.colors.Normalize(vmin=graph_min, vmax=graph_cap+graph_cap*0.05), vert_exag=0.1, blend_mode='soft')
surf = ax.plot_surface(X, Y, Z, rstride=1, cstride=1,
                       facecolors=rgb, linewidth=0, antialiased=True, shade=False)

plt.title('Result for contact discovery in a user base of 10M depending on network percentiles')
plt.show()
plt.savefig('plot.png')


fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.set_xlabel('Network upload speed percentile')
ax.set_ylabel('Network latency speed percentile')
ax.set_zlabel('Time (in ms)')
rgb = ls.shade(Z, cmap=cm.gist_earth, norm=matplotlib.colors.Normalize(vmin=graph_min, vmax=graph_cap+graph_cap*0.05), vert_exag=0.1, blend_mode='soft')
surf = ax.plot_surface(Y, X, Z, rstride=1, alpha=1, cstride=1,
                       facecolors=rgb, linewidth=0, antialiased=True, shade=False)
plt.title('Result for contact discovery in a user base of 10M depending on network percentiles')
plt.show()
plt.savefig('plot2.png')