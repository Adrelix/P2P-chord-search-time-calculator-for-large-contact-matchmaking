import numpy as np
import math
from random import sample
import matplotlib.pyplot as plt
from matplotlib import cbook
from matplotlib import cm
from matplotlib.colors import LightSource

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


class node:
    def __init__(self, id, latency, packageID, packageSize, search_time, establish_connection_time, upload_time, download_time):
        self.id = id
        self.latency = latency
        self.packageID = packageID
        self.packageSize = packageSize
        self.search_time = search_time
        self.establish_connection_time = establish_connection_time
        self.upload_time = upload_time
        self.download_time = download_time


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


# Time required to search through the uploaded contactbook and compare it to the nodes information
# Based on our experiment (see xxxx)
def get_search_time(package_size, amount_of_packages):

    num_list = [10000, 25000, 50000, 100000,
                250000, 500000, 1000000, 1500000, 2000000, 5000000]
    closest_number = min(num_list, key=lambda x: abs(x-package_size))

    if closest_number == 10000:
        search_time_mean = 38.72
        search_time_spread = 3.45
    elif closest_number == 25000:
        search_time_mean = 27.72
        search_time_spread = 1.50
    elif closest_number == 50000:
        search_time_mean = 30.86
        search_time_spread = 2.91
    elif closest_number == 100000:
        search_time_mean = 36
        search_time_spread = 3.16
    elif closest_number == 250000:
        search_time_mean = 61
        search_time_spread = 17.67
    elif closest_number == 500000:
        search_time_mean = 83.29
        search_time_spread = 4.61
    elif closest_number == 1000000:
        search_time_mean = 141.43
        search_time_spread = 8.14
    elif closest_number == 1500000:
        search_time_mean = 207.57
        search_time_spread = 17.26
    elif closest_number == 2000000:
        search_time_mean = 271.57
        search_time_spread = 15.79
    elif closest_number == 5000000:
        search_time_mean = 810.86
        search_time_spread = 35.33
    return np.random.normal(search_time_mean, search_time_spread, amount_of_packages)


x = []
y = []
z = []

# amount of users in millions
a_min = 1
a_max = 20

# amount of packages
p_min = 1
p_max = 50
p_inc_size = 5

# amount of iteration for each combination
i_tot = 3

for database_size in range(a_min*1000000, a_max*1000000+1000000, 1000000):
    print(database_size/1000000)

    for amount_of_packages in range(p_min, p_max+p_inc_size, p_inc_size):
        results = []
        # Set Values
        # All times are in milliseconds
        amount_of_nodes = database_size
        package_size = math.floor(database_size/amount_of_packages)
        contact_book_size = 1000
        hash_table_creation_time = 10
        time_to_send_requests = amount_of_packages
        # print("Amount of nodes to collect from:", amount_of_packages)
        # print("Average package size:", package_size)

        for i in range(i_tot):

            search_times = get_search_time(package_size, amount_of_packages)

            # https://www.speedtest.net/global-index
            latency_mean = 37
            latency_spread = 10

            # Upload and download averages based on
            # https://www.speedtest.net/global-index
            upload_speed_mean = 13.06
            upload_speed_spread = 4.64
            download_speed_mean = 41.5
            download_speed_spread = 32.68

            # Based on a tcp and tls handshake protocol. Six (one-way) exchanges is required before the connection is established and secure
            # https://learning.oreilly.com/library/view/high-performance-browser/9781449344757/ch04.html#TLS_HANDSHAKE
            connection_protocol_multiplier = 3

            # Normal distribution of latencies
            latencies = np.random.normal(
                latency_mean, latency_spread, amount_of_packages)

            # Normal distribution of latencies on the path when searching for nodes
            path_latencies = np.random.normal(
                latency_mean, latency_spread, 100000)

            # Normal distribution of download speed
            download_speed = np.random.normal(
                download_speed_mean, download_speed_spread, amount_of_packages)

            # Normal distribution of upload speed
            upload_speed = np.random.normal(
                upload_speed_mean, upload_speed_spread, amount_of_packages)

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
                    path_latencies.tolist(), math.floor(path_lengths[track_id]))) * connection_protocol_multiplier

                search_contacts_time = search_times[track_id]

                # Time required to establish a TCP connection to the final node
                establish_connection_time = latencies[track_id] * \
                    connection_protocol_multiplier

                # Calculate the maximum TCP throughput with standard window size 65536 Bytes = 524288 bits
                max_TCP_throughput = 0.524288 / (latencies[track_id] / 1000)

                # Upload speed is capped by max_TCP_thprughput if it's higher than upload_speed[track_id]
                node_upload_speed = upload_speed[track_id] if upload_speed[
                    track_id] < max_TCP_throughput else max_TCP_throughput

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
                            client_status = CLIENT_WAITING_FOR_TRANSFER

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
                            if client_status == CLIENT_WAITING_FOR_TRANSFER:
                                client_status = (
                                    "TRANSFERING DOWN BETWEEN CLIENT AND TRACK #" + str(track.track_id))
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
            if ms_count < 5000:
                results.append(ms_count)

        average = sum(results)/len(results)
        # print("AVERAGE: ", average, "ms", sep='')
        y.append(amount_of_packages)
        x.append(database_size/1000000)
        z.append(average)

x = np.reshape(x, (len(np.unique(x)), len(np.unique(y))))
y = np.reshape(y, (len(np.unique(x)), len(np.unique(y))))
z = np.reshape(z, (len(np.unique(x)), len(np.unique(y))))


fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

ax.plot_surface(x, y, z)

ax.set_ylabel('Amount of packages')
ax.set_xlabel('Amount of users (in millions)')
ax.set_zlabel('Time (in ms)')

ls = LightSource(270, 45)
# To use a custom hillshading mode, override the built-in shading and pass
# in the rgb colors of the shaded surface calculated from "shade".
rgb = ls.shade(z, cmap=cm.gist_earth, vert_exag=0.1, blend_mode='soft')
surf = ax.plot_surface(x, y, z, rstride=1, cstride=1,
                       facecolors=rgb, linewidth=0, antialiased=False, shade=False)

plt.show()
plt.savefig('plot.png')


# plt.show()
