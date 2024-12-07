# IoT-System

0. Introduction:
- The system uses a TCP client-server setup for IoT data analysis. 
- The client handles three specific queries which are 1, 2, 3, 4.
- The client sends valid ones to the server, and shows the results. 
- The server connects to MongoDB, uses metadata (like device IDs and units).
- It can process data for averages, conversions, and comparisons. 
- Results are sent back to the client in a clear and user-friendly format.
- You can use your local machine or use virtual machine (we use Google Cloud Platform).

1. How to run database:
- Connect MongoDB and Dataniz from instruction.
- Create metadata on Dataniz then you can see your metadata on MongoDB.
- Active 3 devices then data can send from Dataniz to MongoDB.

2. How to run server:
- Open terminal and navigate to the directory where server.py is saved.
- Enter the server's IP addres as 0.0.0.0
- Enter the port number
- Wait for client connection

3. How to run client:
- Open terminal and navigate to the directory where client.py is saved.
- Run the script with command: py client.py
- Enter the server's IP address
- Enter the port number
- If IP address and port are correct, the client will connect to the server.
- Enter your choice as 1, 2, 3, 4 and wait for the server.