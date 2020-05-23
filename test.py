from client import *

# get无参数
#
# http = Http(url='http://ws.webxml.com.cn/WebServices/WeatherWS.asmx/getRegionProvince')
# http.send()
# http.check_status_code(200)
# http.res_headers


# post json
#
# http = Http(url='http://huice.huicewang.com:9000/event/weather/getWeather/',
#             method=Method.POST,
#             body_type=Body_Type.JSON,
#             timeout=3)
# http.set_body({"theCityCode": 1})
# http.send()
# http.check_status_code(200)
# http.check_res_time(500)
# http.check_json_node_exists(json_path='$.weather_info', exp='weather_info')
# http.check_json_node_value(json_path='$.name', exp_value='北京')


# post encoded

# http = Http(url='http://ws.webxml.com.cn/WebServices/WeatherWS.asmx/getSupportCityString',
#             method=Method.POST,
#             body_type=Body_Type.URLENCODE,
#             timeout=3)
# http.set_body({'theRegionCode': '31110'})
# http.send()
# http.check_status_code(200)
# http.check_res_time(100)
#
# for x in range(5):
#     if x == 2:
#         print(x)
#         break
# else:
#     print("执行else....")

import jsonpath
import requests
data = {'username':'admin','password':'huicehuice123'}
header = {'Content-Type': 'application/x-www-form-urlencoded'}
res = requests.post(url='http://huice.huicewang.com:9000/api/login/', data=data,headers=header,allow_redirects=False)
print(res.status_code)
print(res.headers)
value = jsonpath.jsonpath(dict(res.headers), '$.Set-Cookie')
print(value)

import re

# source = '{"city":"$cityid1","city2":"$cityid2", "month":"1"}'
# search_result = {'content_type': 'application/json', 'cityid1': 110000, 'cityid2': 350100}
#
# rs = re.findall(r'\$(\w+)', source)
# for s in rs:
#     value = search_result.get(s)
#     source = source.replace('$' + s, str(value))
# print(source)

# cookie = 'token=da2e7cd8423ab93a8bed12ce38bdf4365b063d45; Path=/,uid=3; Path=/'
#
# l = re.findall('\w+=\w+',cookie)
# print(';'.join(l))
