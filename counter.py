from pymongo import MongoClient
from pprint import pprint
import datetime

client = MongoClient()
db = client.portal_life
names = 'canteen gym parking room'.split()
for n in names:
    print(n, db[n].count_documents({}))
bg = datetime.datetime(2021, 5, 28, 11, 30, 30)
ed = datetime.datetime(2021, 5, 28, 12, 30, 30)
funcs = [
    lambda x: (x['time'].split()[-1], x['rows'][0]['ip']),
    lambda x: (x['timestamp'].split()[-1][:-3], x['gyms'][4]['occupy']),
    lambda x: x['obj']['details'][3]['free'],
    lambda x: x['pull_time'] #x['rows'][1]['classroomFree']
]
for n, f, _ in zip(names, funcs, range(4)):
    print(n + '-'*10)
    pprint(list(f(i) for i in db[n].find({
        'pull_time': {'$gt': bg, '$lt': ed}
    }, sort=[('pull_time', 1)])))
# pprint(list(i for i in db.canteen.find().sort('_id', -1).limit(3)))
