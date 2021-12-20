import json

def read_json(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def write_json(data, file_path, indent=4):
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=indent)