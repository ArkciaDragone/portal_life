# Intro
Portal Life通过P大门户数据分析制作可视化图表。使用MongoDB作为数据库，pyecharts绘图。

数据来源于门户网站提供的[校园指数](https://portal.pku.edu.cn/portal2017/#/pub/lifeH)。这个页面中提供了就餐指数、健身指数、停车指数和空闲教室数目的实时数据。

通过对历史数据的分析得出食堂就餐人数和教室空闲状况的规律，用这样的规律来帮助任何感兴趣的浏览者获得更好的校园体验。

![Canteen(5.22-6.6)](imgs/canteen7.gif)
# Usage
首先安装各依赖包 `pip install -r requirements.txt`。

在`config.json`中配置好MongoDB的连接参数，使用`crawler.py`积累数据，其余文件用于数据分析和绘图。

# Files
## General
 - `crawler.py` 爬虫程序，同时包含数据库的连接代码供其它文件使用。
 - `config.json` 项目配置文件，内有数据库的连接参数。
 - `counter.py` 简单地对爬取的数据进行计数和预览。

## Canteen
 - `draw.py` 不使用pandas直接绘图。绘制的时间跨度大时，降低采样频率（增大`STEP`）能显著降低浏览器的渲染压力。
 - `panda.py` 采用pandas处理数据，可以存储为csv文件和绘图。
 - `histo.py` 统计给定时段人数最值和出现时间的条形图。

## Classroom
 - `room.py` 画出某一周内各教学楼教室的空闲率。

# Metadata
食堂的数据在每天早上6点到晚上11点间每两分钟更新一次，教室的使用数据更新则会迟大约3分钟。

有时候服务器没有响应，爬取会失败，在约2周的爬取过程中发生了35次，不到0.2%。考虑到每分钟爬取一次，高于数据更新速度，不连续的失败几乎没有影响。

食堂的数据观察到有全部为0的情况，为门户提供了错误数据，有需要可以手动剔除。

教室的数据中，有的教室的数据为0/0，有的没有变化，已经列入了忽略列表中。值得一提的是，文史楼的数据空闲教室数会比总教室数多，这在原网页上也能看到。

# Future Directions
 - 格式化提取数据而不是整个保存JSON
 - 获取学校API的使用权直接用API取得数据
 - 分析体育场馆和停车位的数据
 - 现象背后的原因分析
 - 机器学习与预测
 - 网站/APP服务式发布

 # GIF
 |晚餐期间“双峰”的食堂|晚餐期间其它“单峰”食堂|
 |:-:|:-:|
 |!["Bimodal" canteens](imgs/canteen8.1.gif)|!["Unimodal" canteens](imgs/canteen8.2.gif)|

 |晚餐后人数仍然较多的食堂|晚餐后人数快速下降的食堂|
 |:-:|:-:|
 |!["Bimodal" canteens](imgs/canteen9.1.gif)|!["Unimodal" canteens](imgs/canteen9.2.gif)|

一周的教室空闲率
![Classroom util rate](imgs/room1.gif)