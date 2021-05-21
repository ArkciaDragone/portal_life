try:
    import json
    from dotmap import DotMap
    import requests
    import logging as log
    from pymongo import MongoClient
    from pymongo.errors import ServerSelectionTimeoutError
    import datetime
except ImportError as e:
    print(e.msg)
    print('Please install all required packages by "pip install -r requirements.txt"')
    exit(-1)

# Load configurations
try:
    with open('./config.json') as f:
        config = DotMap(json.load(f))
except FileNotFoundError:
    print('config file "config.json" not found')
    exit(1)
log.basicConfig(filename=config.log.filename, style='{',
                format=config.log.format, level=config.log.level)
# Connect to database
try:
    client = MongoClient(host=config.mongo.host, port=config.mongo.port,
                         serverSelectionTimeoutMS=3000)
    log.debug(f'database connected as {client.address}')
    db = client[config.mongo.database_name]
except ServerSelectionTimeoutError:
    log.error(
        f'failed to connect to database at {config.mongo.host}:{config.mongo.port}')
    exit(2)

# Pull contents
for name, url in config.urls.items():
    try:
        resp = requests.get(url)
        j = resp.json()
    except (ValueError, requests.exceptions.ConnectionError) as e:
        log.warning('failed to pull ' + name + ' data, reason: ' + str(e))
        continue
    j['pull_time'] = datetime.datetime.now()
    i = db[name].insert_one(j).inserted_id
    log.info(f'{name}: {i}')
