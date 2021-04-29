import matplotlib
import numpy as np
import math
from random import sample
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.colors import LightSource


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
    def __init__(self, latency_mean, latency_spread, upload_mean, upload_spread):
        self.latency_mean = latency_mean
        self.latency_spread = latency_spread
        self.upload_mean = upload_mean
        self.upload_spread = upload_spread
        self.result_y = []
        self.result_x = []
class database_premis:
    def __init__(self, amount_of_users, optimal_package_distribution):
        self.amount_of_users = amount_of_users
        self.optimal_package_distribution = optimal_package_distribution
        

#Creating different network cases based on, in said order:
# Average latency, 
network_cases = []
network_cases.append(network_case(latency_mean=10, latency_spread=3, upload_mean=50, upload_spread=10))
network_cases.append(network_case(latency_mean=20, latency_spread=5, upload_mean=50, upload_spread=10))
network_cases.append(network_case(latency_mean=37, latency_spread=15, upload_mean=13.06, upload_spread=4.64))
network_cases.append(network_case(latency_mean=60, latency_spread=20, upload_mean=8, upload_spread=2))
network_cases.append(network_case(latency_mean=90, latency_spread=30, upload_mean=5, upload_spread=1))
network_cases.append(network_case(latency_mean=150, latency_spread=30, upload_mean=2, upload_spread=0.5))

premises = []
premises.append(database_premis(1000000, 4))
premises.append(database_premis(10000000, 36))
premises.append(database_premis(50000000, 64))
premises.append(database_premis(100000000, 90))
premises.append(database_premis(500000000, 120))
premises.append(database_premis(1000000000, 250))


for premis in premises:
    database_size = premis.amount_of_users
    amount_of_packages = premis.optimal_package_distribution 

    for case in network_cases:
        latency_mean = case.latency_mean
        latency_spread = case.latency_spread
        latency_minimum = 1
        upload_speed_mean = case.upload_mean
        upload_speed_spread = case.upload_spread
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
            latencies = np.random.normal(
                latency_mean, latency_spread, amount_of_packages)

            for i in range(amount_of_packages):
                if latencies[i] < latency_minimum:
                    latencies[i] = latency_minimum

            # Normal distribution of latencies on the path when searching for nodes
            path_latencies = np.random.normal(
                latency_mean, latency_spread, 100000)

            # Normal distribution of upload speed
            upload_speed = np.random.normal(
                upload_speed_mean, upload_speed_spread, amount_of_packages)

            for i in range(amount_of_packages):
                if upload_speed[i] < upload_speed_minimum:
                    upload_speed[i] = upload_speed_minimum

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

            results.append(ms_count)

        average = sum(results)/len(results)

        case.result_x.append(database_size/1000000)
        case.result_y.append(average)

        print("Amount of users:", database_size /
          1000000, " Latency:", case.latency_mean, "ms  Upload_mean:", case.upload_mean, "Mbps  Time:", average)
        

    

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

plt.plot(network_cases[0].result_x, network_cases[0].result_y, color = tableau20[0], marker = 'o', label = 'Network case 1')
plt.plot(network_cases[1].result_x, network_cases[1].result_y, color = tableau20[2], marker = 'o', label = 'Network case 2')
plt.plot(network_cases[2].result_x, network_cases[2].result_y, color = tableau20[4], marker = 'o', label = 'Network case 3')
plt.plot(network_cases[3].result_x, network_cases[3].result_y, color = tableau20[6], marker = 'o', label = 'Network case 4')
plt.plot(network_cases[4].result_x, network_cases[4].result_y, color = tableau20[8], marker = 'o', label = 'Network case 5')
plt.plot(network_cases[5].result_x, network_cases[5].result_y, color = tableau20[10], marker = 'o', label = 'Network case 6')


plt.title('Performance with variance in network quality')
plt.legend()
plt.show()
plt.savefig('plot.png')
