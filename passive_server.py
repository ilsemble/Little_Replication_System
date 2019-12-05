import pickle
import socket
import threading
import json

from config import Action, Field, Sender, Ip, answer_on_get_list, answer_message


def update_string_from_active(number):
    request = {}
    request.update({Field.SENDER: Sender.PASSIVE})
    request.update({Field.ACTION: Action.GET_STRING})
    request.update({Field.STRING_NUMBER: int(number)})
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(Ip.active)
    print("Send to active: ", json.dumps(request))
    s.send(json.dumps(request).encode('ascii'))
    data = s.recv(1024).decode('ascii')
    s.close()
    data = json.loads(data)
    print(data)
    print("Get update from active: ", data)
    return data[Field.STRING_VALUE]


class ClientThread(threading.Thread):
    def __init__(self, channel, details):
        self.channel = channel
        self.details = details
        threading.Thread.__init__(self)

    def handle_client_request(self, data):
        if data[Field.ACTION] == Action.GET_LIST:
            answer = answer_on_get_list(string_list.keys())
            self.channel.send(json.dumps(answer).encode('ascii'))
        elif data[Field.ACTION] == Action.GET_STRING:
            number = str(data[Field.STRING_NUMBER])
            print(number)
            print(string_list)
            print(changed_string)
            if number in changed_string:
                changed_string.remove(number)
                new_value = update_string_from_active(number)
                if new_value is None:
                    del string_list[number]
                    msg = "This string have been deleted from server."
                else:
                    string_list[number] = new_value
                    msg = "Value of string: " + new_value
            elif number in string_list:
                string_value = string_list[number]
                msg = "Value of string: " + string_value
            else:
                msg = "There is not such string."
            answer = answer_message(msg)
            print("Send answer: ", answer)
            self.channel.send(json.dumps(answer).encode('ascii'))
            print(string_list)
        else:
            answer = answer_message("I don't understand what you want from me, I'm little passive server... "
                                    "Maybe my active brother can help you.")
            self.channel.send(json.dumps(answer).encode('ascii'))
            print(string_list)

    def run(self):
        print('Received connection:', self.details[0])
        data = self.channel.recv(1024).decode('ascii')
        data = json.loads(data)
        print("Received data: ", data)
        if data[Field.SENDER] == Sender.ACTIVE:
            # Значит активный сервер прислал сообщения об изменениях.
            changed_number = str(data[Field.CHANGED_NUMBER])
            if changed_number not in changed_string:
                changed_string.append(changed_number)
                string_list.update({changed_number: None})
            print("String %s was changed." % changed_number)
        elif data[Field.SENDER] == Sender.CLIENT:
            # Общаемся с клиентом
            self.handle_client_request(data)
        else:
            print("Error: I don't understand who is my sender!")
        self.channel.close()
        print('Closed connection:', self.details[0])


if __name__ == '__main__':
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(Ip.active)
    data = {Field.SENDER: Sender.PASSIVE}
    data.update({Field.ACTION: Action.HELLO})
    print("I says hello to active: ", json.dumps(data))
    s.send(json.dumps(data).encode('ascii'))

    data = s.recv(1024).decode('ascii')
    data = json.loads(data)
    print("Answer from active: ", data)
    s.close()
    string_list = data[Field.LIST]
    print("List: ", string_list)
    changed_string = [i for i in string_list.keys()]
    print("Changes: ", changed_string)

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('', 9999))
    server.listen(5)

    while True:
        channel, details = server.accept()
        ClientThread(channel, details).start()

    # exit(0)
