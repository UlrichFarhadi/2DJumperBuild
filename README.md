# 2DJumperBuild
Build for Windows and Linux, for the 2DJumper OpenAI gym environment

On Windows or Linux without docker
Pull the repository, then in the Training folder, run master_server.py, and then run as many compute_slave_client.py as you want. This is set up to run locally, and to run at a simulation speed of 100, so you might not benefit from running multiple clients. For better effect use a real server to run the master_server.py on, and then connect to that server from different devices by running compute_slave_client.py on those compyters and modify the host and port in both files so they can be connected.

Run using Docker (better guide coming soon...):
1)
Pull docker container: docker pull henning998/client_env
2)
install the python packages required in the Training folder and also protobuf. If protobuf version does not work, try this one: pip install protobuf==3.20.*
Run the master_server.py file in the Training folder
3)
Starting a docker container will start a compute_slave client

Notes:
- For larger pytorch neural network. Test using protobuf how many bytes the message is, and adjust the buffer_socket_size variable to be equal or higher than that number. Remember to change the variable in both compute_slave_client.py and master_server.py
