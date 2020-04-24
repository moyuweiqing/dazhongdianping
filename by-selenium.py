from selenium import webdriver
from bs4 import BeautifulSoup as bs
import pandas as pd
import requests, re
import os
import time
import pandas as pd

page = 15
name = '北京朝阳大悦城'

info_table = pd.DataFrame(columns=['昵称', '口味', '环境', '服务', '时间', '评论'])

css_headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'}
font_size = 14
start_y = 23

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
    # print(font_dict)
    return font_dict

def get_css_info(url):
    global css_headers
    res = requests.get(url, headers=css_headers)
    html = res.text

    background_image_link = re.findall(r'background-image:.*?\((.*?svg)\)', html)
    # print(background_image_link)
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

def getdata():
    pre = '//*[@id="review-list"]/div[2]/div[3]/div[3]/div[3]/ul/li['
    # a = driver.find_element_by_xpath('//*[@id="review-list"]/div[2]/div[3]/div[3]/div[3]/ul/li[1]/div/div[4]')
    # print(a.text)
    thelist = []
    for i in range(1, 16):
        alist = []
        name_xpath = pre + str(i) + ']/div/div[1]/a'
        kouwei_xpath = pre + str(i) + ']/div/div[2]/span[2]/span[1]'
        huanjing_xpath = pre + str(i) + ']/div/div[2]/span[2]/span[2]'
        fuwu_xpath = pre + str(i) + ']/div/div[2]/span[2]/span[3]'
        time_xpath = pre + str(i) + ']/div/div[7]/span[1]'

        name = driver.find_element_by_xpath(name_xpath).text
        time.sleep(0.5)
        try:
            kouwei = driver.find_element_by_xpath(kouwei_xpath).text
        except:
            try:
                kouwei_xpath = pre + str(i) + ']/div/div[3]/span[2]/span[1]'
                kouwei = driver.find_element_by_xpath(kouwei_xpath).text
            except:
                kouwei = 'none'
        time.sleep(0.5)
        try:
            huanjing = driver.find_element_by_xpath(huanjing_xpath).text
        except:
            try:
                huanjing_xpath = pre + str(i) + ']/div/div[3]/span[2]/span[2]'
                huanjing = driver.find_element_by_xpath(huanjing_xpath).text
            except:
                huanjing = 'none'
        time.sleep(0.5)
        try:
            fuwu = driver.find_element_by_xpath(fuwu_xpath).text
        except:
            try:
                fuwu_xpath = pre + str(i) + ']/div/div[3]/span[2]/span[3]'
                fuwu = driver.find_element_by_xpath(fuwu_xpath).text
            except:
                fuwu = 'none'
        time.sleep(0.5)
        try:
            date = driver.find_element_by_xpath(time_xpath).text
        except:
            try:
                time_xpath = pre + str(i) + ']/div/div[6]/span[1]'
                date = driver.find_element_by_xpath(time_xpath).text
            except:
                date = 'none'
        time.sleep(0.5)

        alist.append(name)
        alist.append(str(kouwei).replace('口味：', ''))
        alist.append(str(huanjing).replace('环境：', ''))
        alist.append(str(fuwu).replace('服务：', ''))
        alist.append(date)

        # info_table.loc[i] = alist
        thelist.append(alist)
        time.sleep(1)
    return thelist

def next_page():
    # driver.find_element_by_xpath('//*[@id="review-list"]/div[2]/div[3]/div[3]/div[4]/div/a[10]').click()
    driver.find_element_by_class_name('NextPage').click()

# 展开评论
def zhankai():
    pre = '//*[@id="review-list"]/div[2]/div[3]/div[3]/div[3]/ul/li['
    for i in range(1, 16):
        try:
            zhankai_xpath = pre + str(i) + ']/div/div[3]/div/a'
            driver.find_element_by_xpath(zhankai_xpath).click()
        except:
            try:
                zhankai_xpath = pre + str(i) + ']/div/div[4]/div/a'
                driver.find_element_by_xpath(zhankai_xpath).click()
            except:
                print('没能成功展开')
        time.sleep(0.5)

# 滑动滑条，加载全部信息
def drop_down():
    for x in range(1, 15, 2):
        time.sleep(0.5)# 防止被预测到反爬
        h = x/14
        js = 'document.documentElement.scrollTop = document.documentElement.scrollHeight * %f' % h
        driver.execute_script(js)
    h = 0.1
    js = 'document.documentElement.scrollTop = document.documentElement.scrollHeight * %f' % h
    driver.execute_script(js)

def login():
    driver.find_element_by_xpath('//*[@id="top-nav"]/div/div[2]/span[1]/a[1]').click()
    time.sleep(15) # 登录

def get_comment():
    a = driver.page_source
    html_tree = bs(a, 'lxml')
    name_texts = html_tree.find_all("a", class_ = "name") # 找到所有的名字

    item_texts = html_tree.find_all("span", class_ = "item") # 找到所有的评分
    item_list = []
    for each in item_texts:
        if '人均' not in str(each.get_text()):
            item_list.append(str(each.get_text()).replace('口味：', '').replace('环境：', '').replace('服务：', '').replace('\n', '').replace(' ', ''))

    date_texts = html_tree.find_all("span", class_ = "time") # 找到所有的时间

    alist = []
    comment_texts = html_tree.find_all("div", class_="review-words")  # 找到所有的评论
    comment_list = []
    for comment_text in comment_texts:
        comment_text = str(comment_text)
        class_set = []
        # print(html_text)
        for span in re.findall(r'<svgmtsi class="([a-zA-Z0-9]{5,6})"></svgmtsi>', comment_text):
            class_set.append(span)
        for class_name in class_set:
            try:
                comment_text = re.sub(r'<svgmtsi class="%s"></svgmtsi>' % class_name, font_dict[class_name], comment_text)
                # print('{}已替换完毕_______________________________'.format(font_dict[class_name]))
            except:
                comment_text = re.sub(r'<svgmtsi class="%s"></svgmtsi>' % class_name, '', comment_text)
                print('替换失败…………………………………………………………………………&&&&&&&&&&&&&&&&&&&&&&&&')
        b = str(re.findall('[\u4e00-\u9fa5]+', comment_text)).replace('收起评论', '').replace('文字', '').replace('[', '').replace(']', '').replace('\'', '')
        comment_list.append(b)
    for i in range(1, 16):
        clist = []
        clist.append(str(name_texts[i].get_text()).replace(' ', '').replace('\n', ''))
        clist.append(item_list[i * 3])
        clist.append(item_list[i * 3 + 1])
        clist.append(item_list[i * 3 + 2])
        clist.append(str(date_texts[i - 1].get_text()).replace(' ', '').replace('\n', '')[:10])
        clist.append(comment_list[i - 1])
        alist.append(clist)
    print(alist)
    return alist

if __name__ == '__main__':
    driver = webdriver.Chrome(r'D:\360极速浏览器下载\chromedriver_win32\chromedriver.exe')
    driver.get('http://www.dianping.com/shop/6026269/review_all')
    time.sleep(3)
    login()

    # 获取密码表
    css_link = driver.find_element_by_xpath('/html/head/link[4]').get_attribute('href')
    font_dict = get_css_info(css_link)

    time.sleep(2)
    # drop_down()
    for i in range(0, page):
        zhankai()
        alist = get_comment()
        for j in range(0, 15):
            try:
                info_table.loc[i * 15 + j] = alist[j]
                print('  已完成' + str(i * 15 + j) + '个')
            except:
                info_table.to_csv('西贝筱面村' + name + '.csv', encoding='gbk')
        print('已完成' + str(i + 1) + '页')
        next_page()
    # print(info_table)
    info_table.to_csv('西贝筱面村' + name + '.csv', encoding='gbk')