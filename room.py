from pyecharts.commons.utils import JsCode
from pymongo import MongoClient
import pandas as pd
from datetime import datetime, time, timedelta
from operator import itemgetter
from pyecharts.globals import ThemeType
import pyecharts.options as opts
from pyecharts.charts import HeatMap, Timeline

# constants and options
ABSOLUTE = False
BEGIN = datetime(2021, 5, 26)
END = BEGIN + timedelta(weeks=1)
IGNORED = set(['电子', '化学', '电教听力', '地学', '哲学', '电教'])  # bad data exist
TITLE = f'room ({BEGIN.day}-{END.day})'
WEEK = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']


def extract(x, absolute=False):
    """extract db data for pandas to parse"""
    d = {i['buildingName']: i['classroomFree'] if absolute else i['classroomFree']/i['classroomSum']
         for i in x['rows'] if i['buildingName'] not in IGNORED}
    d['time'] = x['pull_time']
    return d


# connect to database and parse data
client = MongoClient()
col = client.portal_life.room
data = [extract(i, ABSOLUTE) for i in col.find(
        {'pull_time': {'$gt': BEGIN, '$lt': END}},
        sort=[('pull_time', 1)])]
df = pd.json_normalize(data).set_index('time')
df = df[:].loc[(df[:].shift() != df[:]).any(
    axis=1)]  # drop consecutive duplicates
df.to_csv('room.csv')

# curriculum info
with open('class_time.txt', encoding='utf-8') as f:
    schd = {datetime.strptime(line.split()[-1].split('-')[0], '%H:%M').time(): i
            for i, line in enumerate(f.readlines())}
    f.seek(0)
    lessons = [line.split()[0] for line in f.readlines()]

# collect data for each weekday
data = {i: [] for i in WEEK}
for i, cols in df.iterrows():
    # align time to 10-min
    c = schd.get(time(hour=i.hour, minute=i.minute // 10 * 10))
    if c is not None:  # c may be [] so check against None
        data[WEEK[i.weekday()]].append((c, cols))
ydata = {}  # {weekday: [[x_pos, y_pos, value]...]}
for weekday, icols in data.items():
    y = []
    ydata[weekday] = y
    nxt = 0  # next weekday pending collecting
    for cid, cols in sorted(icols, key=itemgetter(0)):
        while nxt < cid:  # consecutive ratio removed earlier, reproduce
            y.append([[i, len(schd) - 1 - nxt, v] for i, _, v in y[-1]])
            nxt += 1
        y.append([[i, len(schd) - 1 - cid, v] for i, v in enumerate(cols)])
        nxt += 1

# draw the graph
timeline = Timeline(init_opts=opts.InitOpts(
    width='100%', height='100%', theme=ThemeType.DARK, page_title=TITLE)
).add_schema(
    orient="vertical",
    pos_left="null",
    pos_right="5",
    pos_top="20",
    pos_bottom="20",
    width="60",
    is_inverse=True
)
for weekday in WEEK:
    yvalue = []
    for i in ydata[weekday]:
        yvalue.extend(i)
    timeline.add(
        HeatMap(init_opts=opts.InitOpts(
            width='100%', height='100%', theme=ThemeType.DARK)
        ).set_global_opts(title_opts=opts.TitleOpts(title=weekday))
        .add_xaxis(list(df.columns))
        .add_yaxis(
            series_name="空闲教室比例",
            yaxis_data=lessons[::-1],
            value=yvalue,
            label_opts=opts.LabelOpts(is_show=False),
        )
        .set_series_opts()
        .set_global_opts(
            legend_opts=opts.LegendOpts(is_show=False),
            xaxis_opts=opts.AxisOpts(
                type_="category",
                splitarea_opts=opts.SplitAreaOpts(
                    is_show=True, areastyle_opts=opts.AreaStyleOpts(opacity=1)
                ),
            ),
            yaxis_opts=opts.AxisOpts(
                type_="category",
                splitarea_opts=opts.SplitAreaOpts(
                    is_show=True, areastyle_opts=opts.AreaStyleOpts(opacity=1)
                ),
            ),
            visualmap_opts=opts.VisualMapOpts(
                min_=0, max_=1, is_calculable=True, orient="horizontal", pos_left="center",
                range_color=["#d94e5d", "#eac763", "#50a3ba"]
            ),
            tooltip_opts=opts.TooltipOpts(
                is_show=True,
                formatter=JsCode("""p => p.seriesName + '<br/>'
                + p.name + ' ' + p.marker + ' ' + p.data[2].toPrecision(3) * 100 + '%'""")
            ),
        ),
        weekday
    )
timeline.render(TITLE + '.html')
