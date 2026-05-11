import subprocess
import os

def check_server_status(hostname):
    # This function is intended to let users ping a server
    # to check if it is online.
    
    # Logic: The input is placed directly into a shell command string.
    command = "ping -c 1 " + hostname
    
    try:
        # shell=True tells Python to run the string through the system shell
        output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
        return output.decode()
    except subprocess.CalledProcessError as e:
        return e.output.decode()

# Standard operation
print(check_server_status("google.com"))

# Input that triggers system detection
# If a user enters "google.com; cat /etc/passwd", the shell executes both.
malicious_input = "127.0.0.1; ls -la"
print(check_server_status(malicious_input))