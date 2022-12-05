import socket
import numpy as np
import random
from time import sleep
import gym
import pickle
import torch
import time

# Self made python files includes
import MessageTCP_pb2
import Jumper2Denv

buffer_socket_size = 10048

host = 'host.docker.internal'  #'127.0.0.1'
port = 1234

ClientSocket = socket.socket()
print('Waiting for connection')
try:
    ClientSocket.connect((host, port))
except socket.error as e:
    print(str(e))
Response = ClientSocket.recv(2048)
print(Response.decode('utf-8'))

# Make Gym environment, so that we dont have to start and stop it everytime
env_simulation_speed = 100.0 # env_simulation_speed determines the speed of the simulation where 1 is normal speed and 100 is 100 times faster
                           # Can max be 100, but if set too high it will will adapt to how fast your pc can perform calculations
env, behavior_name = Jumper2Denv.create_env(show_graphics=False, env_simulation_speed=env_simulation_speed)
timesteps_per_episode = 1000 # Simulation runs in 50 fps, 1 frame = 1 timestep, so 1000 timesteps equals to 20 sec simulation

while True:
    job_idx = -1
    try:
        print("t1")
        data_recv = ClientSocket.recv(buffer_socket_size) # Blocking here until data is received
        print("t2")
        read_data = MessageTCP_pb2.MessageTCP()
        print("t3")
        print(len(data_recv))
        read_data.ParseFromString(data_recv)
        print("t4")
        job_idx = read_data.agent_id
        print("t5")
        model = pickle.loads(read_data.model)
        #print("Test: Data received from master")
    except Exception as e:
        print(e)
        print("Test: Error: Something went wrong receiving the job")
        break
    try:
        print("t6")
        env.reset()
        print("t7")
        cum_reward = Jumper2Denv.run_one_episode(env=env, model=model, behavior_name=behavior_name, timesteps_per_episode=timesteps_per_episode)
        print("Episode Reward: ", cum_reward)
        message_obj = MessageTCP_pb2.MessageTCP()
        message_obj.reward = cum_reward
        message_obj.agent_id = job_idx
        data = message_obj.SerializeToString()
        #sleep(5)
        ClientSocket.sendall(bytes(data)) # Blocking here until data is sent
        #print("Test: Sending back reward")
    except:
        print("Test: Error: Something went wrong sending the reward back")
        break

print("Test: Closing env...")
env.close()
print("Closing Socket")
ClientSocket.close()