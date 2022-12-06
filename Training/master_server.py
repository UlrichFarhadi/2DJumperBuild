from ast import If
from asyncore import read
from audioop import add
from concurrent.futures import thread
from http import server
import socket
from _thread import *
import multiprocessing
from time import sleep
from random import random
import pickle

#from xxlimited import Null

# Self made python files includes
import GA_evolver
import MessageTCP_pb2

# try:
#    multiprocessing.set_start_method('spawn', force=True)
#    print("process_start_method = 'spawn'")
# except RuntimeError:
#    pass

buffer_socket_size = 10048

host = '127.0.0.1'
port = 1234

# Logging the amount of threads containing active clients, connected to the server
thread_count = 0
thread_mutex = multiprocessing.Lock()

timeout_var = 50.0 # If the client takes more than timeout_var seconds to execute an episode, it will get fucked cuz either it's too slow or it was corrupted
                   # Timeout var is in seconds

# Create an instance from the class GA_evolver
population_size = 20
generations = 100
AI_instance = GA_evolver.GAevolver(population_size = population_size, generations=generations)

# Define model
input = 8       # Observation Space
hidden = [10]*5 # [5,5,5,5]
output = 3      # Action space

# Set evolution parameters
elitism = 1
top_best_actors_mutates = 5
random_mutation_percent = 5
amount_of_nonbest_actors_mutates = 0

AI_instance.set_model_parameters(input=input, hidden=hidden, output=output)
AI_instance.set_evolution_parameters(elitism=elitism, top_best_actors_mutates=top_best_actors_mutates, random_mutation_percent=random_mutation_percent, amount_of_nonbest_actors_mutates=amount_of_nonbest_actors_mutates)

AI_instance.generate_initial_jobs()

socket_id = 0
socket_id_mutex = multiprocessing.Lock()


def thread_count_add(add_value):
    global thread_count, thread_mutex
    thread_mutex.acquire()
    thread_count += add_value
    thread_mutex.release()

def client_disconnect(job):
    AI_instance.append_job(job)
    thread_count_add(-1)
    print("Client disconnected: Amount of running client threads =", thread_count)
    # append to the data queue, the data lost

def AI_handler():
    while True:
        #print("Test: AI HANDLER DOING SHIT")
        #print("Test: Finished Jobs: ", len(AI_instance.finished_jobs))
        #print("Test: Available Jobs: ", len(AI_instance.available_jobs))
        
        #sleep(1.3) # Delay for testing purposes
        #print(AI_instance.available_jobs[0])
        
        # Checking if the amount of completed jobs is equal to population size, if it is it needs to call on_generation to apply mutation and other operators and to distribute new jobs
        #print("AI_instance.completed_jobs: ", AI_instance.completed_jobs)
        #print("AI_instance.population_size: ", AI_instance.population_size)
        if AI_instance.completed_jobs == AI_instance.population_size:
            AI_instance.operating = True
            #print("Calling on_generation()")
            AI_instance.on_generation()
            print("Generation Best Reward = ", AI_instance.best_generation_reward)
            #print("Test: No more jobs left, calling on_generation()...")

            AI_instance.completed_jobs = 0
            AI_instance.operating = False

def client_handler(connection):
    global thread_count, socket_id
    thread_count_add(1)
    socket_id_mutex.acquire()
    this_id = socket_id
    socket_id += 1
    socket_id_mutex.release()
    print("Client connected: Amount of running client threads =", thread_count)
    connection.sendall(str.encode('You are now connected to the MASTER server...'))
    released = False
    while True:
        #sleep(2.2) # does it just spam aquire and release the mutex? Maybe that makes on_generation() not able to acuire the mutex when it needs to refill the qyeye
        if AI_instance.operating == True:
            sleep(1)
            continue
        AI_instance.available_jobs_mutex.acquire()
        if len(AI_instance.available_jobs) != 0 and AI_instance.operating == False:
            job = AI_instance.available_jobs.pop(0)
            AI_instance.available_jobs_mutex.release()
            released = True
            try: # First Pass
                message_obj = MessageTCP_pb2.MessageTCP()
                message_obj.agent_id = job[0]
                message_obj.model = pickle.dumps(job[1])
                data = message_obj.SerializeToString()
                #print(len(data))
                connection.sendall(bytes(data)) # Blocking here until data is sent
                #print(this_id, " Test: Job sent to compute slave")
            except:
                #print(this_id, " Error: Failed to send compute job")
                client_disconnect(job)
                break
            # Wait for answer back to receive the reward
            try: # Last Pass
                #print(this_id, " Attempting to receive")
                connection.settimeout(timeout_var)
                data_recv = connection.recv(buffer_socket_size) # Blocking here until data is received
                #print(this_id, " Successfull receive")
                read_data = MessageTCP_pb2.MessageTCP()
                read_data.ParseFromString(data_recv)
                #print(this_id, " Test: Data read from compute slave")
                job_idx = read_data.agent_id
                reward = read_data.reward
                if job[0] != job_idx:
                    #print(this_id, " Error: Returned job index is not the same as the original job index")
                    print("Error: Returned job index is not the same as the original job index")
                    client_disconnect(job)
                    break
                #print("Reward for agent = ", reward)
                if AI_instance.completed_jobs == AI_instance.population_size:
                    AI_instance.operating = True
                AI_instance.add_finished_job(job_idx=job_idx, reward=reward)
            except:
                #print(this_id, " Error: Failed to receive reward")
                print("Error: Failed to receive reward")
                client_disconnect(job)
                break
        if released == False:
            AI_instance.available_jobs_mutex.release()
        else:
            released = False
    
    #client_disconnect()
    #print(this_id, " Closing socket")
    print("Closing socket")
    connection.close()

def accept_connections(ServerSocket):
    Client, address = ServerSocket.accept()
    print('Connected to: ' + address[0] + ':' + str(address[1]))
    #p = multiprocessing.Process(target=client_handler, args=(Client,))
    #p.start()
    #p.join()
    start_new_thread(client_handler, (Client, ))

def start_server(host, port):
    ServerSocket = socket.socket()
    try:
        ServerSocket.bind((host, port))
    except socket.error as e:
        print(str(e))
    print(f'Server is listing on the port {port}...')
    ServerSocket.listen()
    
    while True:
        accept_connections(ServerSocket)

# Start the AI_handler
start_new_thread(AI_handler, ())

# Start the MASTER server
start_server(host, port)