from pprint import pprint
from pymongo import MongoClient
import pandas as pd
import datetime
from pyecharts.globals import ThemeType
import pyecharts.options as opts
from pyecharts.charts import Line

# constants and options
ABSOLUTE = True
SELECT = False
BEGIN = datetime.datetime(2021, 5, 25, 6, 0, 30)
END = datetime.datetime(2021, 5, 26, 0, 0, 30)
IGNORE = True
IGNORED = set(['畅春园一层', '畅春园二层', '畅春园三层', '农园三层', '中关园食堂', '万柳食堂', '成府园食堂'])
DRAW = False

def extract(x, absolute=False):
    """extract db data for pandas to parse"""
    d = {i['name']: i['ip'] if absolute else i['ip']/i['seat']
         for i in x['rows'] if not IGNORE or i['name'] not in IGNORED}
    d['time'] = datetime.datetime.strptime(x['time'], '%Y-%m-%d %H:%M')
    return d

# connect to database and use pandas to parse data
client = MongoClient()
col = client.portal_life.canteen
data = [extract(i, ABSOLUTE) for i in col.find(
        {'pull_time': {'$gt': BEGIN, '$lt': END}} if SELECT else {},
        sort=[('pull_time', 1)])]
df = pd.json_normalize(data).set_index('time')
print('before drop: ', len(df))
df = df.drop_duplicates()
print('after drop: ', len(df))
df.to_csv('panda.csv')

# print statistics
q = pd.concat({'mean': df.mean(), 'max': df.max(),
               'median': df.median()}, axis=1)
print(q.sort_values('mean'))

if DRAW:
    c = Line(init_opts=opts.InitOpts(theme=ThemeType.DARK, width='100%', height='100%')).add_xaxis(
        [datetime.datetime.strftime(i, '%m-%d %H:%M') for i in df.index])
    for n, d in df.iteritems():
        c.add_yaxis(n, d, is_smooth=True)
    (
        c.set_series_opts(
            areastyle_opts=opts.AreaStyleOpts(opacity=0.5),
            label_opts=opts.LabelOpts(is_show=False),
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title="Canteen"),
            xaxis_opts=opts.AxisOpts(
                axistick_opts=opts.AxisTickOpts(is_align_with_label=True),
                boundary_gap=False,
            ),
            yaxis_opts=opts.AxisOpts(
                type_="value",
                axistick_opts=opts.AxisTickOpts(is_show=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
            ),
            datazoom_opts=[opts.DataZoomOpts(is_realtime=SELECT),
                        opts.DataZoomOpts(is_realtime=SELECT, type_='inside')],
        )
        .render("panda.html")
    )
