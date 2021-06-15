# P2P-chord-search-time-calculator-for-large-contact-matchmaking
This report is a Bachelor thesis for a Bachelor in Computer Science and Engineering.

More information can be found at https://www.kth.se/student/kurser/kurs/DA150X?l=en



Decentralization is a technique that removes trust in central authorities by distributing authority across a network of nodes. But it comes with challenges. This project investigates the advantages and limitations a decentralized contact discovery system for a messaging application may have. The areas of interest in this project concerns performance and scalability of the system. The simulator uses a mathematical approach where each task’s expected runtime was estimated from experiments or previous conducted studies. 


### Navigation

### Final project report.pdf
A thorough report can be read about the project, the experiments and the results

### calculator.py
Smple component used to simulate a single contact discovery run. Slightly modified versions are used for the other simulators.

### database_size_vs_amount_of_packages.py
Heavy working simulator that tries to find the optimal amount of packages for different database sizes.

### network_case_tester.py
Testing partitions of the network quality distributions against varying user base sizes to see how different networks perform over different user base sizes.

### network_percentile_tester.py
Test different percentiles of the network (in terms of bandwidth and latency), over a fixed contact book size and user base size to find bottlenecks.

### contact_book_tester.py
Test a varying contact book size over a fixed user base size with a chosen spectrum of network qualities

### KexTest
Android project simulating the set up times and search times.
