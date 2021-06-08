from crawler import client
from pyecharts.globals import ThemeType
import pyecharts.options as opts
from pyecharts.charts import Bar
from pyecharts.commons.utils import JsCode
import pandas as pd
import datetime

# constants and options
IGNORE = True
IGNORED = set(['畅春园一层', '畅春园二层', '畅春园三层', '农园三层', '中关园食堂', '万柳食堂', '成府园食堂'])
DRAW = True
RANGE = ((6, 00), (23, 00))
RANGE_STR = f"{RANGE[0][0]}:{RANGE[0][1]:02d} ~ {RANGE[1][0]}:{RANGE[1][1]:02d}"
LIMIT = datetime.datetime.today()
TITLE = f'histo ({RANGE_STR})'


def extract(x):
    """extract db data"""
    d = {i['name']: i['ip']
         for i in x['rows'] if not IGNORE or i['name'] not in IGNORED}
    d['time'] = datetime.datetime.strptime(x['time'], '%Y-%m-%d %H:%M')
    return d

# connect to database
col = client.portal_life.canteen
data = {}
f = datetime.datetime(2021, 5, 22, RANGE[0][0], RANGE[0][1])
t = f.replace(hour=RANGE[1][0], minute=RANGE[1][1])
DAY = datetime.timedelta(1)
while t < LIMIT:
    ext = [extract(i) for i in col.find({'pull_time': {'$gt': f, '$lt': t}},
                                        sort=[('pull_time', 1)])]
    df = pd.json_normalize(ext).set_index('time')
    data[f] = df.max(), df.idxmax()
    f += DAY
    t += DAY

if DRAW:
    c = (
        Bar(init_opts=opts.InitOpts(width='100%', height='100%',
                                    theme=ThemeType.DARK, page_title=RANGE_STR))
        .set_global_opts(title_opts=opts.TitleOpts(title=RANGE_STR))
        .add_xaxis([i.strftime('%m-%d %a') for i in data.keys()])
    )
    for idx in df.columns:
        ydata = [{'value': int(v[idx]), 'time': t[idx].strftime(
            '%H:%M')} for v, t in data.values()]
        c.add_yaxis(idx, ydata, stack='stack1', category_gap='50%')

(
    c.set_series_opts(
        label_opts=opts.LabelOpts(
            position="right",
            formatter=JsCode("function(x){return (x.data.time);}"),
        )
    )
    .render(TITLE.replace(':', '.') + '.html')
)
