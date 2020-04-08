import requests, re
from lxml import etree
import pandas as pd
import os

href = 'http://www.dianping.com/shop/507685/review_all/p9'
page = '9'
cookie = '_lxsdk_cuid=1691a949bb8c8-04d8bc0c44962f-43450721-1fa400-1691a949bb8c8; _lxsdk=1691a949bb8c8-04d8bc0c44962f-43450721-1fa400-1691a949bb8c8; _hc.v=d0011738-9740-3959-10a9-7d59a7d1eeac.1585554729; s_ViewType=10; _dp.ac.v=233bd24e-3836-4e9d-b023-47c918642e39; ua=%E9%9C%9C%E4%B9%8B%E5%93%80%E4%BC%A4_5002; ctu=5bb9b42e931861c06bf91f192fd3934f0426b5a3d785d6b19d9e2f49df4ff481; dper=8a8675567db0e38b89d1148dc72799ed8e541f9fa3afac5fa6a75d949714971bec343a2c43b1122c8a4e03fc358e2b6d6d9cbf1f4e51fe1507858d40fd934600af2d3a18d71c25e1fac9ad39d1e85dda33387f594fc03f0ac7f47698c5028bc3; ll=7fd06e815b796be3df069dec7836c3df; _lx_utm=utm_source%3Dso.com%26utm_medium%3Dorganic; dplet=6150f58b4ca44ebb600b39f8eea92efc; cy=2; cye=beijing; _lxsdk_s=1713eee3b08-b07-cea-321%7C%7C5602'



info_table = pd.DataFrame(columns=['昵称','口味', '环境', '服务', '人均', '评论', '时间'])

css_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'
    }
font_size = 14
start_y = 23
css_link = ''
font_dict = {}
comment_headers = {
    'Cookie': cookie,
    'Host': 'www.dianping.com',
    'Referer': 'http://www.dianping.com/guangzhou/ch10/r13880',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 UBrowser/6.2.4098.3 Safari/537.36'
}

def get_url(url, headers):
    r = requests.get(url, headers=headers)
    # r.encoding = r.apparent_encoding
    r.encoding = 'utf-8'
    return r.text


def xpath_href(html_text):
    html = etree.HTML(html_text)
    href_all_list = html.xpath('//div[@id="shop-all-list"]/ul/li/div[2]/div/a[1]/@href')
    return href_all_list


def re_item(html_text, item):
    res = re.findall('<p class="desc">(.*?)</p>', html_text)
    for review in res:
        rev = re.findall('<svgmtsi class="review">&#x(.*?);</svgmtsi>', review)
        uni = re.split('<svgmtsi class="review">.*?</svgmtsi>', review)
        txt = ''
        for k, v in enumerate(rev):
            txt += uni[k] + item['\\' + v]
        txt += uni[-1]
        # print(txt)

def get_font_dict_by_offset(url):
    global css_headers, start_y, font_size
    """
        获取坐标偏移的文字字典, 会有最少两种形式的svg文件（目前只遇到两种）
    """
    res = requests.get(url, headers=css_headers)
    html = res.text
    font_dict = {}
    y_list = re.findall(r'd="M0 (\d+?) ', html)
    if y_list:
        font_list = re.findall(r'<textPath .*?>(.*?)<', html)
        for i, string in enumerate(font_list):
            y_offset = start_y - int(y_list[i])

            sub_font_dict = {}
            for j, font in enumerate(string):
                x_offset = -j * font_size
                sub_font_dict[x_offset] = font
            font_dict[y_offset] = sub_font_dict
    else:
        font_list = re.findall(r'<text.*?y="(.*?)">(.*?)<', html)
        for y, string in font_list:
            y_offset = start_y - int(y)
            sub_font_dict = {}
            for j, font in enumerate(string):
                x_offset = -j * font_size
                sub_font_dict[x_offset] = font
            font_dict[y_offset] = sub_font_dict
    return font_dict

def get_css_info(url):
    global css_headers
    res = requests.get(url, headers=css_headers)
    html = res.text

    background_image_link = re.findall(r'background-image:.*?\((.*?svg)\)', html)
    print(background_image_link)
    background_image_link_list = []
    for i in background_image_link:
        url = 'http:' + i
        background_image_link_list.append(url)

    # print(background_image_link_list)

    html = re.sub(r'span.*?\}', '', html)
    group_offset_list = re.findall(r'\.([a-zA-Z0-9]{5,6}).*?round:(.*?)px (.*?)px;', html)
    '''
    多个偏移字典，合并在一起；；；
    '''
    font_dict_by_offset_list = {}
    for i in background_image_link_list:
        font_dict_by_offset_list.update(get_font_dict_by_offset(i))

    font_dict_by_offset = font_dict_by_offset_list
    # print(font_dict_by_offset)
    font_dict = {}
    for class_name, x_offset, y_offset in group_offset_list:
        x_offset = x_offset.replace('.0', '')
        y_offset = y_offset.replace('.0', '')
        try:
            font_dict[class_name] = font_dict_by_offset[int(y_offset)][int(x_offset)]

        except:
            font_dict[class_name] = ''
    return font_dict

def get_comment():
    global comment_headers, font_dict, href
    url = href
    html = get_url(url, comment_headers)
    # html = etree.HTML(html)
    # h = html.xpath('//*[@id="review-list"]/div[2]/div[3]/div[3]/div[3]')
    class_set = []
    for span in re.findall(r'<svgmtsi class="([a-zA-Z0-9]{5,6})"></svgmtsi>', html):
        class_set.append(span)
    for class_name in class_set:
        try:
            html = re.sub('<svgmtsi class="%s"></svgmtsi>' % class_name, font_dict[class_name], html)
            # print('{}已替换完毕_______________________________'.format(font_dict[class_name]))
        except:
            html = re.sub('<svgmtsi class="%s"></svgmtsi>' % class_name, '', html)
            print('替换失败…………………………………………………………………………&&&&&&&&&&&&&&&&&&&&&&&&')
    # html_tree = etree(html)
    my_prosess(html)
    # h = html_tree.xpath('//*[@id="review-list"]/div[2]/div[3]/div[3]/div[3]/ul/li[1]/div/div[1]/a/text()')
    # print(h)

def my_prosess(html):
    global page
    html = html.replace('\n', '')
    # print(html)
    # name = re.findall(r'<a class="name"(.*?) data-click-title="文字">(.*?)<\/a>', html)
    # print(name[0])
    print(str(html))
    html_tree = etree.HTML(html)
    pre = '////*[@id="review-list"]/div[2]/div[3]/div[3]/div[3]/ul/li['
    for i in range(1, 16):
        alist = []
        name_xpath = pre + str(i) + ']/div/div[1]/a/text()'
        kouwei_xpath = pre + str(i) + ']/div/div[2]/span[2]/span[1]/text()'
        huanjing_xpath = pre + str(i) + ']/div/div[2]/span[2]/span[2]/text()'
        fuwu_xpath = pre + str(i) + ']/div/div[2]/span[2]/span[3]/text()'
        renjun_xpath = pre + str(i) + ']/div/div[2]/span[2]/span[4]/text()'
        pinglun_xpath = pre + str(i) + ']/div/div[3]/text()'
        time_xpath = pre + str(i) + ']/div/div[7]/span[1]/text()'

        name =     html_tree.xpath(name_xpath)
        kouwei =   html_tree.xpath(kouwei_xpath)
        huanjing = html_tree.xpath(huanjing_xpath)
        fuwu =     html_tree.xpath(fuwu_xpath)
        renjun =   html_tree.xpath(renjun_xpath)
        pinglun =  html_tree.xpath(pinglun_xpath)
        time =     html_tree.xpath(time_xpath)
        if(len(time)==0):
            time_xpath = pre+str(i)+']/div/div[6]/span[1]/text()'
            time = html_tree.xpath(time_xpath)
        # h =        html_tree.xpath('//*[@id="review-list"]/div[2]/div[3]/div[3]/div[3]/ul/li[2]/div/div[1]/a/text()')

        alist.append(str(name[0]).replace(' ', '').replace(u'\xa0', u' '))
        if len(kouwei)!=0:
            alist.append(str(kouwei[0]).replace(' ', '').replace('口味：', '').replace(u'\xa0', u' '))
        else:
            alist.append('NONE')
        if len(huanjing)!=0:
            alist.append(str(huanjing[0]).replace(' ', '').replace('环境：', '').replace(u'\xa0', u' '))
        else:
            alist.append('NONE')
        if len(fuwu)!=0:
            alist.append(str(fuwu[0]).replace(' ', '').replace('服务：', '').replace(u'\xa0', u' '))
        else:
            alist.append('NONE')
        if len(renjun)!=0:
            alist.append(str(renjun[0]).replace(' ', '').replace('人均：', '').replace(u'\xa0', u' '))
        else:
            alist.append('NONE')
        print(str(pinglun[0]).replace('\n', '').replace('\t', ''))
        if len(pinglun)!=0:
            alist.append(str(pinglun[0]).replace('\n', '').replace('\t', '').replace(u'\u2323', u'').replace(u'\u02d8', u'').replace(u'\u10e6', u'').replace(u'\U0001f954', u'').replace(u'\U0001f34e', u'').replace(u'\U0001f606', u'').replace(u'\U0001f490', u'').replace(u'\U0001f365', u'').replace(u'\u2763', u'').replace(u'\U0001f92b', u'').replace(u'\u2764', u'').replace(u'\U0001f604', u'').replace(u'\ufffc', u'').replace(u'\u261e', u'').replace(u'\U0001f440', u'').replace(u'\u2666', u'').replace(u'\U0001f3b8', u'').replace(u'\u26f3', u'').replace(u'\u2b55', u'').replace(u'\u23f3', u'').replace(u'\U0001f937', u'').replace(u'\U0001f9c0', u'').replace(u'\U0001f42e', u'').replace(u'\U0001f605', u'').replace(u'\U0001f33e', u'').replace(u'\U0001f414', u'').replace(u'\U0001f17f', u'').replace(u'\u270c', u'').replace(u'\U0001f375', u'').replace(u'\U0001f615', u'').replace(u'\U0001f9a5', u'').replace(u'\u2614', u'').replace(u'\U0001f62b', u'').replace(u'\U0001f963', u'').replace(u'\U0001f345', u'').replace(u'\U0001f236', u'').replace(u'\u2795', u'').replace(u'\U0001f362', u'').replace(u'\U0001f364', u'').replace(u'\U0001f973', u'').replace(u'\u200d', u'').replace(u'\U0001f486', u'').replace(u'\u0301', u'').replace(u'\u0300', u'').replace(u'\u2022', u'').replace(u'\u0e07', u'').replace(u'\u2661', u'').replace(u'\uff89', u'').replace(u'\uff65', u'').replace(u'\uff61', u'').replace(u'\u06f6', u'').replace(u'\u0e51', u'').replace(u'\u0669', u'').replace(u'\U0001f958', u'').replace(u'\U0001f356', u'').replace(u'\U0001f957', u'').replace(u'\u2b50', u'').replace(u'\u20e3', u'').replace(u'\u25ab', u'').replace(u'\U0001f1f3', u'').replace(u'\U0001f1e8', u'').replace(u'\U0001f68c', u'').replace(u'\U0001f53b', u'').replace(u'\u272a', u'').replace(u'\U0001f481', u'').replace(u'\U0001f374', u'').replace(u'\xb4', u'').replace(u'\u2207', u'').replace(u'\u22da', u'').replace(u'\u22db', u'').replace(u'\u2736', u'').replace(u'\u2737', u'').replace(u'\u2738', u'').replace(u'\u2739', u'').replace(u'\u273a', u'').replace(u'\U0001f9b4', u'').replace(u'\U0001f41f', u'').replace(u'\U0001f411', u'').replace(u'\U0001f49a', u'').replace(u'\U0001f539', u'').replace(u'\U0001f53a', u'').replace(u'\U0001f49b', u'').replace(u'\U0001f4dd', u'').replace(u'\U0001f538', u'').replace(u'\U0001f31f', u'').replace(u'\U0001f46d', u'').replace(u'\U0001f234', u'').replace(u'\ufe0f', u'').replace(u'\u2b05', u'').replace(u'\U0001f36f', u'').replace(u'\U0001f308', u'').replace(u'\U0001f495', u'').replace(u'\U0001f923', u'').replace(u'\U0001f927', u'').replace(u'\U0001f388', u'').replace(' ', '').replace(u'\xa0', u' ').replace('\xa5', '').replace(u'\U0001f4cd', u' ').replace(u'\U0001f44f', u' ').replace(u'\U0001f3fb', u' ').replace(u'\U0001f60b', u' '))
        else:
            alist.append('NONE')
        if len(time)!=0:
            alist.append(str(time[0]).replace(' ', '').replace(u'\xa0', u' '))
        else:
            alist.append('NONE')
        # print(str(name[0]).replace(' ', ''))
        # print(str(kouwei[0]).replace(' ', ''))
        # print(str(huanjing[0]).replace(' ', ''))
        # print(str(fuwu[0]).replace(' ', ''))
        # print(str(renjun[0]).replace(' ', ''))
        # print(str(pinglun[0]).replace(' ', ''))
        # print(str(time[0]).replace(' ', ''))

        info_table.loc[i-1] = alist
    print(info_table)
    path = str(os.getcwd()+'\北京六里桥\第'+page+'页.csv')
    info_table.to_csv(path, encoding='gbk')

def main():
    global css_link,font_dict, href
    item = pp.temp_6
    url = 'http://www.dianping.com/guangzhou/ch10/r13880'
    headers = {
        'Cookie': '_lxsdk_cuid=1691a949bb8c8-04d8bc0c44962f-43450721-1fa400-1691a949bb8c8; _lxsdk=1691a949bb8c8-04d8bc0c44962f-43450721-1fa400-1691a949bb8c8; _hc.v=d0011738-9740-3959-10a9-7d59a7d1eeac.1585554729; s_ViewType=10; _dp.ac.v=233bd24e-3836-4e9d-b023-47c918642e39; ua=%E9%9C%9C%E4%B9%8B%E5%93%80%E4%BC%A4_5002; ctu=5bb9b42e931861c06bf91f192fd3934f0426b5a3d785d6b19d9e2f49df4ff481; dper=8a8675567db0e38b89d1148dc72799ed8e541f9fa3afac5fa6a75d949714971bec343a2c43b1122c8a4e03fc358e2b6d6d9cbf1f4e51fe1507858d40fd934600af2d3a18d71c25e1fac9ad39d1e85dda33387f594fc03f0ac7f47698c5028bc3; ll=7fd06e815b796be3df069dec7836c3df; _lx_utm=utm_source%3Dso.com%26utm_medium%3Dorganic; dplet=6150f58b4ca44ebb600b39f8eea92efc; cy=2; cye=beijing; _lxsdk_s=1713eee3b08-b07-cea-321%7C%7C5731',
        'Host': 'www.dianping.com',
        'Referer': 'http://www.dianping.com/guangzhou/ch10/r13880',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 UBrowser/6.2.4098.3 Safari/537.36'
    }
    html_text = get_url(url, headers)
    href_list = xpath_href(html_text)

    # href = 'http://www.dianping.com/shop/10648326/review_all'# 强行介入
    show_html = get_url(href, headers)
    # print(show_html)
    html = etree.HTML(show_html)
    h = html.xpath('/html/head/link[4]/@href')
    # print(h) # 获取css文件
    css_link = 'http:' + str(h[0])
    # print(css_link)
    # re_item(show_html, item)
    font_dict = get_css_info(css_link)
    # print(font_dict)
    get_comment()

if __name__ == '__main__':
    main()