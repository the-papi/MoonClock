def center_string(string, capacity=10):
    length = len(string)
    margin = (capacity - length) // 2
    if margin < 0:
        margin = 0

    string = (' ' * margin) + string + (' ' * margin)

    if len(string) < capacity:
        string = (' ' * (capacity - len(string))) + string

    return string


def str_rjust(string, length, char=' '):
    while len(string) < length:
        string = char + string
    return string
