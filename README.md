# Web Server Log Monitor Game
![LogGame](images/Xh7KgljWfS.png)

This project is a graphical application built using Pygame to visualize real-time web server log data. It reads log entries from a remote server, parses them, and represents each client request graphically. This can be useful for understanding the traffic and behavior of a web server in a dynamic and interactive way.

## Features

- Real-time log monitoring: Connects to a remote server via SSH and tails the Nginx access log.
- Graphical representation: Displays clients as dots and their requests as lines moving towards the server.
- Status indication: Uses different colors to represent the status of requests (successful, redirects, client errors, server errors).
- Interactive interface: Provides a real-time, animated view of web server activity.

## Requirements

- Python 3.x
- Pygame
- Paramiko

## Installation

1. Clone the repository:
   git clone https://github.com/yourusername/web-server-log-monitor-game.git
   cd web-server-log-monitor-game

2. Install the dependencies:
   pip install pygame paramiko

3. Setup your configuration:
   Modify the variables log_file, ip, user, and keys_folder in the script to match your server's details.

## Configuration

- log_file: Path to the log file on the remote server (e.g., `/var/log/nginx/access.log`).
- ip: IP address of the remote server.
- user: Username for SSH login.
- keys_folder: Directory containing SSH keys to authenticate with the remote server.

## Usage

1. Run the script:
   python log_monitor.py

2. Interactive visualization:
   - The server is represented by a circle at the center of the screen.
   - Clients appear as small dots scattered around the server.
   - Lines indicate requests moving from clients to the server, with colors changing based on the response status.

## Code Explanation

- Pygame Initialization: Initializes the Pygame library and sets up the screen dimensions and colors.
- Client Class: Represents a client, holding its position and requests.
- Request Class: Represents a request, handling its animation and status display.
- SSH Key Finder: Attempts to connect to the server using available SSH keys and selects the correct one.
- Log Monitor: Connects to the remote server, tails the log file, and parses log entries.
- Flash Server: Changes the server's color to indicate the presence of client or server errors.
- Main Loop: The main game loop that updates and renders the graphical elements.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
