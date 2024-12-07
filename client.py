import socket
import ipaddress

# Function to display menu options
def printChoices():
    print("1. What is the average moisture inside my kitchen fridge in the past three hours?")
    print("2. What is the average water consumption per cycle in my smart dishwasher?")
    print("3. Which device consumed more electricity among my three IoT devices (two refrigerators and a dishwasher)?")
    print("4. Exit")

# Prompt the user to enter the server IP address
server_ipaddress = input("Enter the server IP address: ")

# Validate the IP address
try:
    ipaddress.ip_address(server_ipaddress)
except ValueError:
    print("Invalid IP address.")
    exit()

# Prompt the user to enter the server's port
try:
    server_port = int(input("Enter the port number of server: "))
    if not (0 < server_port <= 65535):
        raise ValueError
except ValueError:
    print("Invalid port number.")
    exit()

# Create a TCP connection to the server
try:
    myTCPSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    myTCPSocket.connect((server_ipaddress, server_port))
    print(f"Connected to server at {server_ipaddress}:{server_port}")
except Exception as e:
    print(f"Failed to connect to the server: {e}")
    exit()

# Main loop which can let user ask more questions
while True:
    # Display all choices
    printChoices()
    try:
        # Get the user's choice
        choice = int(input("Enter your choice: "))
        if choice not in [1, 2, 3, 4]:
            print("Sorry, this query cannot be processed. Please try one of the following:")
            printChoices()
            continue

        if choice == 4:
            print("Exiting...")
            break

        # Send the user's choice to the server
        myTCPSocket.sendall(str(choice).encode('utf-8'))
        print(f"Sent choice {choice} to the server.")

        # Receive and show the server's response
        server_response = myTCPSocket.recv(1024).decode('utf-8')
        print("Response from server:", server_response)

    except ValueError:
        print("Invalid input. Please enter a number.")
    except Exception as e:
        print(f"An error occurred: {e}")
        break

myTCPSocket.close()
print("Connection closed.")