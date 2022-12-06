# 2DJumperBuild<br />
Build for Windows and Linux, for the 2DJumper OpenAI gym environment<br />

On Windows or Linux without docker<br />
Pull the repository, then in the Training folder, run master_server.py, and then run as many compute_slave_client.py as you want. This is set up to run locally, and to run at a simulation speed of 100, so you might not benefit from running multiple clients. For better effect use a real server to run the master_server.py on, and then connect to that server from different devices by running compute_slave_client.py on those compyters and modify the host and port in both files so they can be connected.

Run using Docker (better guide coming soon...):<br />
1)<br />
Pull docker container: docker pull henning998/client_env<br />
2)<br />
install the python packages required in the Training folder and also protobuf. If protobuf version does not work, try this one: pip install protobuf==3.20.*
Run the master_server.py file in the Training folder<br />
3)<br />
Starting a docker container will start a compute_slave client<br />

Notes:<br />
- For larger pytorch neural networks. Test using protobuf how many bytes the message is, and adjust the buffer_socket_size variable to be equal or higher than that number. Remember to change the variable in both compute_slave_client.py and master_server.py<br />
- The client auto detects if you are using Windows or Linux or Docker, so all you have to do is run it. Just makae sure that you have the correct python libraries if you run the client outside Docker (install the requirements.txt file in the Training folder). NOTE: If you are running the client on Linux (outside Docker), mlagents is using pytorch, and it has to be version 1.8.1 (specified by mlagents), so you have to run Conda to get that exact version. Therefore it is advised to use Docker (or windows) when running the client
- For GPU support:
  - Requirements: Must have a 64bit operating system
  - Docker has to be installed on Linux, if using Windows install it inside WSL and follow the rest of this guide inside WSL
  - Install NVIDIA Container Toolkit
  - sudo apt-get install -y nvidia-docker2
  - Restart the Docker daemon
  - When doing docker.run give it the flag: --gpus all


Demonstration video of how to run the setup locally<br />
https://user-images.githubusercontent.com/49520062/205865598-8452b39f-4169-43d9-8357-a83415dd7ff5.mp4

