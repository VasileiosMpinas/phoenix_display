import json
from .models import YourModel

def load_data_from_json(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
        for item in data:
            YourModel.objects.create(**item)