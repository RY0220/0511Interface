import xlrd
import time
import unittest
from client import *
import HTMLTestReportCN

ts = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
suite = unittest.TestSuite()

workbook = xlrd.open_workbook('./cases.xls', formatting_info=True)
sheet = workbook.sheet_by_index(0)
# 动态拼接代码
result_code = []
result_class_code = 'class Test(unittest.TestCase):'
result_code.append(result_class_code)

for i in range(1, sheet.nrows):
    case = sheet.row_values(i)
    case_id = 'test_'+case[0]
    case_desc = case[1]
    case_url = case[2]
    case_method = case[3]

    # case_params
    case_params = case[4]
    if case_params:
        case_params = case[4]
    else:
        case_params = {}
    # case_headers
    case_headers = case[5]
    if case_headers:
        case_headers = case[5]
    else:
        case_headers = {}
    # case_body_type
    case_body_type = case[6]

    # case_body
    case_body = eval(case[7])
    if case_body:
        case_body = eval(case[7])
    else:
        case_body = {}

    case_check = case[8]
    # 发送请求 动态代码拼接
    result_func_code = '''
        def {case_id}(self):
            '{case_desc}'
            http = Http(url='{case_url}',
                        method='{case_method}',
                        body_type='{case_body_type}')
            http.set_params({case_params})
            http.set_headers({case_headers})
            http.set_body({case_body})
            http.send()
    '''.format(case_desc=case_desc,
               case_id=case_id,
               case_url=case_url,
               case_method=case_method,
               case_body_type=case_body_type,
               case_params=case_params,
               case_headers=case_headers,
               case_body=case_body)
    result_code.append(result_func_code)
    # result_code.append("suite.addTest(Test('{case_id}'))".format(case_id=case_id))
    # 检查点动态代码拼接
    case_checkitems = case_check.split('\n')
    for item in case_checkitems:
        key = item.split(' ')[0]
        value = item.split(' ')[1]
        if key == '状态码':
            result_code.append("            http.check_status_code(int({value}))".format(value=value))
        elif key == '时间小于(ms)':
            result_code.append("            http.check_res_time(int({value}))".format(value=value))
        elif key == '内容包含':
            result_code.append("            http.check_text_contains('{value}')".format(value=value))
        elif key == '字段包含':
            result_code.append("            http.check_json_node_exists('{value}', '{value}'.split('.')[1])".format(value=value))
        elif key == '字段值检查':
            result_code.append("            http.check_json_node_value('{value}'.split('=')[0], '{value}'.split('=')[1])".format(value=value))

for i in range(1,sheet.nrows):
    case_id='test_'+sheet.row_values(i)[0]
    result_code.append("suite.addTest(Test('{case_id}'))".format(case_id=case_id))

code = '\n'.join(result_code)
print(code)
exec(code)
HTMLTestReportCN.HTMLTestRunner(stream=open('./report_%s.html'%ts,'wb'),
                                title='天气接口测试报告',
                                tester='renyun',
                                description='测试接口').run(suite)
