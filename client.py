import requests
import jsonpath

# class Method:
#     GET = 'get'
#     POST = 'post'
#
#
# class Body_Type:
#     URLENCODE = 'urlencoded'
#     JSON = 'json'
#     XML = 'xml'
#     FORM_DATA = 'form-data'


class Http(object):

    session = requests.session()

    # 构造函数
    def __init__(self, url, method='get', body_type=None, timeout=3):
        # 成员变量
        self.url = url
        self.method = method
        self.body_type = body_type
        self.params = {}
        self.res = None
        self.headers = {}
        self.body = {}
        self.timeout = timeout
        # 请求头设置。传字典

    def get_headers(self):
        return self.headers

    # 请求头设置。传字典
    def set_headers(self, headers_dict):
        if isinstance(headers_dict, dict):
            self.headers = headers_dict
        else:
            raise Exception('请求头参数不是字典类型的')

    # 求头设置。传key,value
    def set_header(self, key, value):
        self.set_headers({key: value})


    # 设置params
    def set_params(self, params_dict):
        if isinstance(params_dict,dict):
            self.params = params_dict
        else:
            raise Exception('参数不是字典类型的')


    # 设置body
    def set_body(self, body_dict):
        if isinstance(body_dict, dict):
            self.body = body_dict
        else:
            raise Exception('请求正文内容不是字典类型')

        if self.body_type == 'urlencoded':
            self.set_header('Content-Type', 'application/x-www-form-urlencoded')
        elif self.body_type == 'json':
            self.set_header('Content-Type', 'application/json')
        elif self.body_type == 'xml':
            self.set_header('Content-Type', 'text/xml')
        elif self.body_type == 'form-data':
            pass
        else:
            raise Exception("不支持的请求正文类型")

    # 发送请求
    def send(self):
        if self.method == 'get':
            try:
                self.res = self.session.get(url=self.url, params=self.params, timeout=self.timeout,allow_redirects=False)
            except Exception as e:
                print("不正确的res", e)
        elif self.method == 'post':
            if self.body_type == 'urlencoded':
                try:
                    self.res = self.session.post(url=self.url, data=self.body, headers=self.headers, timeout=self.timeout,allow_redirects=False)
                except Exception as e:
                    print("不正确的res", e)
            elif self.body_type == 'json':
                self.res = self.session.post(url=self.url, json=self.body, headers=self.headers, timeout=self.timeout,allow_redirects=False)
            elif self.body_type == 'xml':
                result = self.body.get('xml')
                if result:
                    self.res = self.session.post(url=self.url, data=result, headers=self.headers, timeout=self.timeout,allow_redirects=False)
                else:
                    raise Exception("xml请求正文格式不正确，应该为{'xml':'XXXXXXX'}")
            elif self.body_type == 'form-data':
                self.res = self.session.post(url=self.url, files=self.body, headers=self.headers, timeout=self.timeout,allow_redirects=False)
            else:
                raise Exception('不正确的body-Type')

        else:
            raise Exception('不支持的请求方式', self.method)

    @property
    def res_code(self):
        if self.res != None:
            return self.res.status_code
        else:
            return None

    @property
    def res_headers(self):
        if self.res != None:
            return self.res.headers
        else:
            return {}

    @property
    def res_text(self):
        if self.res != None:
            return self.res.text
        else:
            return None

    @property
    def res_dict_from_json(self):
        if self.res != None:
            try:
                return self.res.json()
            except:
                raise Exception('响应正文不是json格式，响应正文{text}'.format(text=self.res_text))
        else:
            return None

    @property
    def res_time(self):
        if self.res != None:
            return round(self.res.elapsed.total_seconds()*1000)
        else:
            return None

            # 依赖细节使用.正文

    # 依赖细节使用.头
    def get_header_value(self, json_path):
        target = jsonpath.jsonpath(dict(self.res_headers), json_path)
        if target !=False:
            value = target[0]
            return value
        else:
            print('headers中{path}不存在'.format(path=json_path))
            return None

    # 依赖细节使用.正文
    def get_json_node_value(self, json_path):
        target = jsonpath.jsonpath(self.res_dict_from_json, json_path)

        if target:
            value = jsonpath.jsonpath(self.res_dict_from_json, json_path)[0]
            return value
        else:
            print('json字段{path}不存在'.format(path=json_path))
            return None

    # 检查状态码
    def check_status_code(self, exp=200):
        assert self.res_code == exp,'响应状态码检查通过，预期[{exp}],实际[{act}]'\
            .format(exp=exp, act=self.res_code)
        info = '响应状态码检查通过'
        print(info)
        return info

    def check_text_equals(self, exp):
        assert self.res_text == exp,'响应正文检查通过，预期[{exp}],实际[{act}]'\
            .format(exp=exp, act=self.res_text)
        info = '响应正文检查通过'
        print(info)
        return info

    def check_text_contains(self, exp):
        assert exp in self.res_text, '响应正文检查通过，预期包含[{exp}],实际未包含，响应正文[{act}]' \
            .format(exp=exp, act=self.res_text)
        info = '响应正文检查通过'
        print(info)
        return info

    def check_json_node_exists(self, json_path, exp):
        assert jsonpath.jsonpath(self.res_dict_from_json, json_path),\
            'json字段[{exp}]检查失败，不存在该节点'.format(exp=exp)
        info = 'json字段[{exp}]检查通过'.format(exp=exp)
        print(info)
        return info

    def check_json_node_value(self, json_path, exp_value):
        target = jsonpath.jsonpath(self.res_dict_from_json, json_path)

        if target:
            act_value = jsonpath.jsonpath(self.res_dict_from_json, json_path)[0]
            assert str(act_value) == str(exp_value),\
                'json字段值[{exp}]检查失败，预期[{path}=={exp}]，实际[{path}=={act}]'\
                    .format(exp=exp_value, path=json_path, act=act_value)
            info = 'json字段值[{path}=={exp}]检查通过'.format(path=json_path, exp=exp_value)
            print(info)
            return info
        else:
            raise AssertionError('json字段{path}不存在'.format(path=json_path))

    def check_res_time(self, max_allowed_ms):
        assert self.res_time < max_allowed_ms,\
            '响应时间检查通过失败，预期[<{max_allowed_ms}]ms，实际[{time}]ms'\
                .format(max_allowed_ms= max_allowed_ms,time=self.res_time)
        info = '响应时间检查通过'
        print(info)
        return info
