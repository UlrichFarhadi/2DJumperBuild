import MessageTCP_pb2


message_obj = MessageTCP_pb2.MessageTCP()

message_obj.agent_id = 5
model = [5,33,55]
message_obj.model = str(model)

data = message_obj.SerializeToString()

print(data)

# Read the data

read_data = MessageTCP_pb2.MessageTCP()
read_data.ParseFromString(data)

print(read_data)
print(read_data.agent_id)
print(read_data.model[1])
print(read_data.model)

#socket.sendto(bytes(data),(HOST,PORT))
# Or sendall???