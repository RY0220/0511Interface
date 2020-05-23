import xlrd, xlwt
from xlutils.copy import copy
from client import *
import time,re


def run_case(case_id, worksheet, header_dict_for_search=None, body_dict_for_search=None):
    print('----------[{case_id}]用例开始执行----------'.format(case_id=case_id))
    RESULT = {}
    search_result = {}
    info = []
    flag = True
    all_ids = worksheet.col_values(colx=0)
    # 用来定义依赖用例返回的值
    r = {}
    # 依赖用例所在的列
    j = 0
    for all_id in all_ids:
        if all_id == case_id:
            j = all_ids.index(all_id)
            case = worksheet.row_values(j)
            case_desc = case[1]
            dependices = case[2]
            dep_details = case[3]
            if dependices:
                dep_case_ids = dependices.split(',')
                for dep_case_id in dep_case_ids:

                    headers_dict = {}
                    body_dict = {}
                    dep_items = dep_details.split('\n')
                    for dep_item in dep_items:
                        lst = dep_item.split(':')
                        cid = lst[0]
                        part = lst[1]
                        expre = lst[2]
                        if cid == dep_case_id:
                            name = expre.split('=')[0]
                            path = expre.split('=')[1]
                            if part == '头':
                                headers_dict[name] = path
                            elif part == '正文':
                                body_dict[name] = path
                            else:
                                raise Exception('依赖细节part传递有误，仅支持[正文][头]')

                    print(headers_dict,body_dict)
                    r = run_case(dep_case_id, sheet,
                                 header_dict_for_search=headers_dict,
                                 body_dict_for_search=body_dict).get('search_result')
                    print("执行[{dep_case_id}]取到的[{search_result}]:"
                          .format(dep_case_id=dep_case_id,search_result = r))
                    search_result.update(r)

            case_url = case[4]
            case_method = case[5]
            case_params = case[6]
            print(case_params)
            case_headers = case[7]
            case_body_type = case[8]
            case_body = case[9]
            case_check = case[10]
            http = Http(url=case_url, method=case_method, body_type=case_body_type, timeout=10)
            if case_params:
                rs = re.findall(r'\$(\w+)', case_params)
                for s in rs:
                    value = search_result.get(s)
                    case_params = case_params.replace('$' + s, str(value))
                http.set_headers(eval(case_headers))
                http.set_params(eval(case_params))
            if case_headers:
                rs = re.findall(r'\$(\w+)', case_headers)
                for s in rs:
                    value = search_result.get(s)
                    if s == 'cookie':
                        value = ';'.join(re.findall(r'\w+=\w+', str(value)))
                        print('^^^^^')
                        print(value)
                        print('^^^^^')
                    case_headers = case_headers.replace('$' + s, str(value))
                    print(case_headers)
                http.set_headers(eval(case_headers))

            if case_body:
                rs = re.findall(r'\$(\w+)', case_body)
                for s in rs:
                    value = search_result.get(s)
                    case_body = case_body.replace('$' + s, str(value))
                http.set_body(eval(case_body))
            print('发送的请求头：', http.get_headers())
            print('发送的正文：', http.body)

            http.send()
            # 检查点
            case_checkitems = case_check.split('\n')
            for item in case_checkitems:
                key = item.split(' ')[0]
                value = item.split(' ')[1]
                try:
                    if key == '状态码':
                        info.append(http.check_status_code(int(value)))
                    elif key == '时间小于(ms)':
                        info.append(http.check_res_time(int(value)))
                    elif key == '内容包含':
                        info.append(http.check_text_contains(value))
                    elif key == '字段包含':
                        info.append(http.check_json_node_exists(value, value.split('.')[1]))
                    elif key == '字段值检查':
                        info.append(http.check_json_node_value(value.split('=')[0], value.split('=')[1]))
                except Exception as e:
                    flag = False
                    info.append('%s 检查点失败' % key)
                    print(e)

            if header_dict_for_search:
                for k, v in header_dict_for_search.items():
                    search_result[k] = http.get_header_value(v)
            if body_dict_for_search:
                for k, v in body_dict_for_search.items():
                    search_result[k] = http.get_json_node_value(v)
            break
    else:
        raise Exception('用例%s不存在' % case_id)

    RESULT['flag'] = flag
    RESULT['info'] = info
    RESULT['search_result'] = search_result
    print('----------[{case_id}]用例运行结束----------'.format(case_id=case_id))
    print(RESULT)
    return RESULT


# 测试报告时间戳生成
ts = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
workbook = xlrd.open_workbook('./cases.xls', formatting_info=True)
sheet = workbook.sheet_by_index(1)
# 测试报告生成
workbook_new = copy(workbook)
sheet_new = workbook_new.get_sheet(1)

# 1.读取xls测试用例的每一行
# 2.使用http对象，设置请求url、请求方式、正文类型、头信息，发送
# 3.使用http对象封装的断言
# 4.将用例执行结果和日志会写到xls里
for i in range(1, sheet.nrows):
    case_id = sheet.cell_value(i, 0)
    case_desc = sheet.cell_value(i, 1)
    print('==========[{case_id}]用例开始执行=========='.format(case_id=case_id))
    result = run_case(case_id, sheet)
    print('==========[{case_id}]用例结束执行=========='.format(case_id=case_id))
    flag = result.get('flag')
    info = result.get('info')
    print("info---------%s"%info)
    if flag:
        style = xlwt.easyxf('pattern: pattern solid, fore_colour green;')
        sheet_new.write(i, 11, 'PASS', style)
        print('**********[{case_id}[{case_desc}]用例通过**********'.format(case_id=case_id, case_desc=case_desc))
    else:
        style = xlwt.easyxf('pattern: pattern solid, fore_colour red;')
        sheet_new.write(i, 11, 'FAIL', style)
        print('**********[{case_id}][{case_desc}]用例失败**********'.format(case_id=case_id, case_desc=case_desc))

    sheet_new.write(i, 12, '\n'.join(info))
workbook_new.save('./测试报告_%s.xls' % ts)
