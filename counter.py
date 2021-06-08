from crawler import client
from pprint import pprint
import datetime

SHOW_SAMPLE = True
db = client.portal_life
names = 'canteen gym parking room'.split()
for n in names:
    print(n, db[n].count_documents({}))

if SHOW_SAMPLE:
    bg = datetime.datetime(2021, 5, 28, 12, 00, 30)
    ed = datetime.datetime(2021, 5, 28, 12, 10, 30)
    funcs = [
        lambda x: (x['time'].split()[-1], x['rows'][0]['ip']),
        lambda x: (x['timestamp'].split()[-1][:-3], x['gyms'][4]['occupy']),
        lambda x: x['obj']['details'][3]['free'],
        lambda x: x['rows'][1]['classroomFree']
    ]
    for n, f in zip(names, funcs):
        print(n + '-'*20)
        pprint(list(f(i) for i in db[n].find({
            'pull_time': {'$gt': bg, '$lt': ed}
        }, sort=[('pull_time', 1)])))
