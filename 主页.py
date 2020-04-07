import requests, re
from lxml import etree
import 密码表缓存 as pp

def get_url(url, headers):
    r = requests.get(url, headers=headers)
    # r.encoding = r.apparent_encoding
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
        print(txt)


def main():
    item = pp.temp_6
    url = 'http://www.dianping.com/guangzhou/ch10/r13880'
    headers = {
        'Cookie': 'navCtgScroll=0; _lxsdk_cuid=16cec6906cbc8-047c0f916a33a7-76212462-100200-16cec6906ccc8; _lxsdk=16cec6906cbc8-047c0f916a33a7-76212462-100200-16cec6906ccc8; _hc.v=b13839d4-ffa5-75e7-e9d3-93ffc6e5d2b8.1567334402; aburl=1; Hm_lvt_dbeeb675516927da776beeb1d9802bd4=1567404596; cy=4; cye=guangzhou; _lx_utm=utm_source%3DBaidu%26utm_medium%3Dorganic; s_ViewType=10; _lxsdk_s=16d064f44c2-2e3-76d-d4c%7C%7C116',
        'Host': 'www.dianping.com',
        'Referer': 'http://www.dianping.com/guangzhou/ch10',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 UBrowser/6.2.4098.3 Safari/537.36'
    }
    html_text = get_url(url, headers)
    href_list = xpath_href(html_text)
    for href in href_list:
        show_html = get_url(href, headers)
        re_item(show_html, item)


if __name__ == '__main__':
    main()