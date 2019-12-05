import socket
import json

from config import Action, Field, Sender, Ip


def add_string_value(request):
    string_value = input("Enter new value of string: ")
    request.update({Field.STRING_VALUE: string_value})
    return request


def add_string_number(request):
    number = int(input("Enter number of string: "))
    request.update({Field.STRING_NUMBER: number})
    return request


def form_request(action_index):
    request = {}
    request.update({Field.SENDER: Sender.CLIENT})
    request.update({Field.ACTION: action_index})
    if action_index == Action.DELETE or action_index == Action.CHANGE or action_index == Action.GET_STRING:
        request = add_string_number(request)
    if action_index == Action.ADD or action_index == Action.CHANGE:
        request = add_string_value(request)
    return request


if __name__ == '__main__':
    action = int(input("Enter:"
                       "%d to add string, "
                       "%d to delete,"
                       "%d to change string,"
                       "%d to get list of strings"
                       "%d to get the string"
                       % (Action.ADD, Action.DELETE, Action.CHANGE, Action.GET_LIST, Action.GET_STRING)))
    data = form_request(action)

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ip = input("IP: ")
    port = int(input("port: "))
    # ip = Ip.ip_active
    # port = Ip.port_active
    s.connect((ip, port))
    s.send(json.dumps(data).encode('ascii'))

    data = s.recv(1024).decode('ascii')
    data = json.loads(data)
    print(data)
    print("Server's answer: ", data[Field.MESSAGE])
    s.close()
