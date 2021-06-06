from pyecharts.globals import ThemeType
import pyecharts.options as opts
from pyecharts.charts import Line
from pymongo import MongoClient
import datetime

# constants and options
JUMP = 8
SEL = (0, 1, 2, 3, 8, 9, 10, 11, 15, 16, 17, 18)
BEGIN = datetime.datetime(2021, 5, 22, 6, 0, 30)
END = datetime.datetime(2021, 6, 6, 23, 0, 30)
TITLE = f'canteen ({BEGIN.month}.{BEGIN.day}-{END.month}.{END.day})'
# helper functions
def gettime(x): return (x['time'][-8:] if BEGIN.day != END.day else x['time'].split()[-1])
def getname(x, i): return x['rows'][i]['name']
def getpop(x, i): return x['rows'][i]['ip'] / x['rows'][i]['seat']

# connect to database and query data
client = MongoClient()
col = client.portal_life.canteen
data = [i for i in col.find(
    {'pull_time': {'$gt': BEGIN, '$lt': END}}, sort=[('pull_time', 1)])]
xlabels = list(map(gettime, data[::JUMP]))
ydata = [(getname(data[0], i),
          [getpop(d, i) for d in data[::JUMP]]) for i in SEL]

# draw the graph
c = Line(init_opts=opts.InitOpts(
    theme=ThemeType.DARK, page_title=TITLE,
    width='100%', height='100%')).add_xaxis(xlabels)
for n, d in ydata:
    c.add_yaxis(n, d, is_smooth=True)
(
    c.set_series_opts(
        areastyle_opts=opts.AreaStyleOpts(opacity=0.5),
        label_opts=opts.LabelOpts(is_show=False),
    )
    .set_global_opts(
        title_opts=opts.TitleOpts(title=TITLE),
        xaxis_opts=opts.AxisOpts(
            axistick_opts=opts.AxisTickOpts(is_align_with_label=True),
            boundary_gap=False,
        ),
        yaxis_opts=opts.AxisOpts(
            type_="value",
            axistick_opts=opts.AxisTickOpts(is_show=True),
            splitline_opts=opts.SplitLineOpts(is_show=True),
        ),
        datazoom_opts=[opts.DataZoomOpts()],
    )
    .render(TITLE + ".html")
)
