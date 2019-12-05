from enum import Enum


class Ip:
    ip_active = '127.0.0.1'
    port_active = 8888
    active = (ip_active, port_active)
    port_passive = 9999


class Action(int):
    ADD = 0
    DELETE = 1
    CHANGE = 2
    GET_LIST = 3
    GET_STRING = 4
    HELLO = 5


class Sender(str):
    ACTIVE = "active"
    PASSIVE = "passive"
    CLIENT = "client"


class Field(str):
    ACTION = 'Action'
    STRING_VALUE = 'String'
    STRING_NUMBER = 'String_number'
    MESSAGE = 'Message'
    SENDER = 'Sender'
    LIST = 'List'
    CHANGED_NUMBER = 'Changed_number'


def answer_on_get_list(string_list):
    if len(string_list) == 0:
        return answer_message("List is empty.")
    msg = "List of strings on server:"
    for k in string_list:
        msg += ' '
        msg += str(k)
    return answer_message(msg)


def answer_message(msg):
    return {Field.MESSAGE: msg}
