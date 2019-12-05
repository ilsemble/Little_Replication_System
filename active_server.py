import socket
import threading
import json

from config import Action, Field, Sender, Ip,  answer_on_get_list, answer_message


def answer_on_get_string(data):
    number = data[Field.STRING_NUMBER]
    if number in string_list:
        value = string_list[number]
    else:
        value = None
    return {Field.STRING_VALUE: value}


def notify_all_passive(changed_number):
    for node in list_ip:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # ip = input("IP: ")
        # port = int(input ("port: "))
        ip = node
        port = 9999
        s.connect((ip, port))
        data_to_passive = {}
        data_to_passive.update({Field.SENDER: Sender.ACTIVE})
        data_to_passive.update({Field.CHANGED_NUMBER: changed_number})
        print('Send to passive (%s): %s' % (ip, json.dumps(data_to_passive)))
        s.send(json.dumps(data_to_passive).encode('ascii'))
        s.close()


class ClientThread(threading.Thread):
    def __init__(self, channel, details):
        self.channel = channel
        self.details = details
        threading.Thread.__init__(self)

    def handle_hello_from_passive(self):
        if self.details[0] not in list_ip:
            list_ip.append(self.details[0])
        print("My passive friends: ", list_ip)
        data_to_passive = {}
        data_to_passive.update({Field.LIST: string_list})
        data_to_passive.update({Field.SENDER: Sender.ACTIVE})
        self.send_data_as_answer(data_to_passive)

    def send_data_as_answer(self, data):
        print('Send to [%s]: %s' % (self.details[0], json.dumps(data)))
        self.channel.send(json.dumps(data).encode('ascii'))
        self.channel.close()
        print('Closed connection:', self.details[0])

    def run(self):
        print('Received connection:', self.details[0])
        data = self.channel.recv(1024).decode('ascii')
        data = json.loads(data)
        print('Received data: ', data)
        # Определим, кто прислал запрос и обработаем его.
        if data[Field.SENDER] != Sender.CLIENT and data[Field.SENDER] != Sender.PASSIVE:
            print("Error: I was taught not to talk to strangers ...")
            self.channel.close()
            print('Closed connection:', self.details[0])
        if data[Field.SENDER] == Sender.PASSIVE:
            # С сервером общается его пассивный собрат.
            if data[Field.ACTION] == Action.HELLO:
                self.handle_hello_from_passive()
                return
            if data[Field.ACTION] == Action.GET_STRING:
                data_to_passive = answer_on_get_string(data)
                self.send_data_as_answer(data_to_passive)
                return
            print("I don't know what it wants from me...")
            self.channel.close()
            print('Closed connection:', self.details[0])
            return

        # С сервером общается клиент.
        # data[Field.SENDER] == Sender.CLIENT:
        if data[Field.ACTION] == Action.ADD:
            if string_list == {}:
                last_number = 0
            else:
                last_number = max(string_list.keys())
                last_number += 1
            string_list[last_number] = data[Field.STRING_VALUE]

            self.send_data_as_answer(answer_message("String was added to server successfully!"))
            print(string_list)
            notify_all_passive(last_number)
            return

        if data[Field.ACTION] == Action.DELETE:
            changed_number = data[Field.STRING_NUMBER]
            if changed_number not in string_list:
                msg = "String was not deleted because it is no longer here..."
            else:
                del string_list[changed_number]
                msg = "String was deleted from server successfully!"
            self.send_data_as_answer(answer_message(msg))
            print(string_list)
            notify_all_passive(changed_number)

        if data[Field.ACTION] == Action.CHANGE:
            changed_number = data[Field.STRING_NUMBER]
            if changed_number not in string_list:
                msg = "String was not changed because it is not here..."
            else:
                string_list[changed_number] = data[Field.STRING_VALUE]
                msg = "String was changed on server successfully!"
            self.send_data_as_answer(answer_message(msg))
            print(string_list)
            notify_all_passive(changed_number)
            return
        if data[Field.ACTION] == Action.GET_LIST:
            answer = answer_on_get_list(string_list.keys())
            self.send_data_as_answer(answer)
            return
        elif data[Field.ACTION] == Action.GET_STRING:
            number = data[Field.STRING_NUMBER]
            if number in string_list:
                string_value = string_list[number]
                msg = "Value of string: " + string_value
            else:
                msg = "There is not such string."
            answer = answer_message(msg)
            self.send_data_as_answer(answer)


if __name__ == '__main__':
    string_list = {}
    list_ip = []

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('', Ip.port_active))
    server.listen(5)

    while True:
        channel, details = server.accept()
        ClientThread(channel, details).start()
