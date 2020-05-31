#import the module what we used
import requests
from pyquery import PyQuery as pq
import numpy as np
import pandas as pd
import os
import os.path
if not os.path.isdir("dataset"):
    os.mkdir("dataset")
import time
import datetime

def get_between_month(end_date):
    # 获得两个日期之间的天数
    start_date = time.strftime('%Y/%m',time.localtime(time.time()))
    start = datetime.datetime.strptime(start_date,'%Y/%m')
    end = datetime.datetime.strptime(end_date,'%Y/%m')
#     try:
#         end = datetime.datetime.strptime(end_date,'%Y/%m')
#     except ValueError:
#         end = datetime.datetime.strptime(end_date,'%Y年%m月')
    month = (start.year-end.year)*12 +(start.month-end.month)
    return month

# add the website with the url into the pyquery
url = "https://www.sogi.com.tw/"
html = requests.get(url+"brands/").text
txt = pq(html)

# Find all of the brands in this site
links =txt("#main > div:nth-child(2) > div:nth-child(1) > div:nth-child(n+1) a")
brands = txt("#main > div:nth-child(2) > div:nth-child(1)").find(".text-center p")
link_list, brand_list = [],[]
for link in links: 
    link_list.append(pq(link).attr('href'))
for brand in range(len(brands)):
    tmp = str(brands.eq(brand).text()).split("(")
    brand_list.append(tmp[0].replace(" ",""))
# [(link_list[i]) for i in range(len(link_list))]
# [(brand_list[i]) for i in range(len(brand_list))]
link_list.pop(-2)
brand_list.pop(-2)
# To pick up the information about cellphone, because this site have the info of tablet and wearable
for index in range(len(link_list)):
    print("[{:>2d}/{}] {} start.".format(index+1,len(link_list),brand_list[index]))
    brand = pq(requests.get(url+link_list[index]).text)
    text =brand.find(".fcellphone").not_('div.mix-item.col-12.col-lg-4.cat1.cat2.cat3.fcellphone.ftablet.fwearable')
    # print(str(brand('#section-list')('#mixitup-1').find(".fcellphone").text()))
    # brand.find(".col-12").find(".d-inline-block").text()
    # brand.find(".fcellphone").not_(".iframe-rwd").text()
    name, price, price_first, price_second, date, month= [],[],[],[],[],[]
    # Find the name of phones
    pqname = text.find(".text-row-1")+text.find(".text-row-2")
    for i in range(len(pqname)):
        name.append(pqname.eq(i).text())
    # Find the price of phones
    pqprice = text.find(".d-block").not_('.d-block text-center').not_('img').not_('a.d-block.text-center')
    for i in [0,1]:
        price.append(text.find(".d-inline-block").eq(3*i).text()+"\n"+text.find(".d-inline-block").eq(3*i+1).text()+"\n"+text.find(".d-inline-block").eq(3*i+2).text())
    for i in range(len(pqprice)):
        price.append(pqprice.eq(i).text())
    for i in range(len(price)):
        tmp = price[i].split("\n")
        if len(tmp)==3:
            a, b = tmp[0].split("$"), tmp[1].split("$")
            c = tmp[2].split("：")
            if a[-1] == "------":
                a[-1] = np.nan
            else:
                a[-1] = int(a[-1].replace(",",""))
            if b[-1] == "------":
                b[-1] = np.nan
            else:
                b[-1] = int(b[-1].replace(",",""))
            try:
                test = datetime.datetime.strptime(c[-1],'%Y/%m')
                pass
            except ValueError:
                test = datetime.datetime.strptime(c[-1],'%Y年%m月')
                c[-1] = test.strftime('%Y/%m')
                pass
            price_first.append(a[-1])
            price_second.append(b[-1])
            date.append(c[-1])
            month.append(get_between_month(c[-1]))
        else:
            a, b = tmp[0].split("$"),tmp[1].split("：")
            if a[-1] =="------":
                a[-1]= np.nan
            else:
                a[-1] = int(a[-1].replace(",",""))
            try:
                test = datetime.datetime.strptime(c[-1],'%Y/%m')
                pass
            except ValueError:
                test = datetime.datetime.strptime(c[-1],'%Y年%m月')
                c[-1] = test.strftime('%Y/%m')
                pass
            price_first.append(a[-1])
            price_second.append(np.nan)
            date.append(c[-1])
            month.append(get_between_month(c[-1]))
#     print(len(name),"\n",len(price_first),"\n",len(price_second),"\n",len(date),"\n",len(month))
    # Combine the name and the price of the phone
    try:
        price_first = list(map(int, price_first))
    except ValueError:
        pass
    try:
        price_second = list(map(int, price_second))
    except ValueError:
        pass
    dic = {"Name":name, "Price":price_first, "Second-hand":price_second, "Listing date":date, "Month":month}
    df = pd.DataFrame(dic)
    #set up the path
    path = "./dataset/" + brand_list[index] + ".csv"
    # save the data as csv
    df.to_csv(path, index = False, header=True)
    print("[{:>2d}/{}] {} complete.".format(index+1,len(link_list),brand_list[index]))
