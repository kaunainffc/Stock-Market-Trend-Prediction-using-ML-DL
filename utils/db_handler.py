import json
import os

def load_user_db():
    paths = ["user_db.json", "user_info.json", "watchlist_db.json"]
    data = {}
    for p in paths:
        path = f"data/{p}"
        if os.path.exists(path):
            with open(path, "r") as f:
                data[p] = json.load(f)
        else:
            data[p] = {} if "watchlist" in p else {"remote_users": {}, "service_providers": {}}
    return data

def save_user_db(data_dict):
    for filename, data in data_dict.items():
        with open(f"data/{filename}", "w") as f:
            json.dump(data, f, indent=4)
