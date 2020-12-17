'''
2020-lingnanMBA-python选修课-Group1
2020-12-15
使用selenium模拟用户输入，并将网页返回的信息格式化读入csv文件中
操作步骤如下：
1.使用脚本调起Chrome浏览器，并访问jd.com（无需登录）；
2.找到搜索所用的字符串，将要搜索的关键词拼接进去
3.模拟点击查询按钮
4.模拟拖动页面到最下面
5.获取查询结果的总页数
6.逐页获取页面商品信息，并写入csv文件中

'''

from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from pyquery import PyQuery as pq
import time
import csv
import random
import sys
import getopt
import yaml

#读取配置文件
fs = open('config.yml',encoding='UTF-8')
config = yaml.load(fs,Loader=yaml.FullLoader)

#获取配置文件中的变量
default_keyword = config['default_keyword']
wait_time = config['wait_time']
max_page_num = config['max_page_num']
root_url = config['root_url']
save_prefix = config['save_prefix']


#创建csv文件表头
def file_header(filename):
    with open(filename, 'a', newline='', encoding='utf-8-sig')as hf:
        write = csv.writer(hf)
        write.writerow(['商品名称','店铺名称','价格', '评论数量','图片地址'])
    hf.close()

#定义一个清洗评论数量的函数
def commit_clear(p_commit):
    if len(p_commit) == 4:
        #格式形同「4条评论」的处理
        p_comment = p_commit[0]
    elif (p_commit[0:].find('万') != -1) and len(p_commit) > 4:
        #格式形同「4万+条评论」的处理
        #print(p_commit[:p_commit.index('万')])
        p_comment = str(float(p_commit[:p_commit.index('万')]) * 10000)
    elif (p_commit[0:].find('+') == -1) and len(p_commit) > 4:
        #格式形同「40条评论」的处理，找不到+号时的处理
        p_comment = p_commit[:-3]
    else:
        #格式形同「xx+条评论」的处理，xx不带万字
        p_comment = p_commit[:-4]
    return p_comment

def crawl_website(keyword,filename):
    # 将chrome的驱动程序(https://chromedriver.storage.googleapis.com/index.html?path=87.0.4280.88/)放到/usr/local/bin下
    # 可以用脚本调起浏览器
    browser = webdriver.Chrome()
    # 访问京东网站
    browser.get(root_url)
    # 等待wait_time秒
    wait = WebDriverWait(browser, wait_time)
    # 通过css选择器的id属性获得输入框。until方法表示浏览器完全加载到对应的节点，才返回相应的对象。
    # presence_of_all_elements_located是通过css选择器加载节点
    search_word = wait.until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, '#key'))
    )
    search_word[0].send_keys(keyword)
    # 查询按钮完全加载完毕，返回查询按钮对象
    submit_button = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, '.button'))
    )
    # 点击查询按钮
    submit_button.click()

    # 模拟下滑到底部操作
    for i in range(0,3):
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # 等待时间随机生成，尝试突破反爬虫
        time.sleep(3)


    # 商品列表的总页数
    total_pages = wait.until(
        EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, '#J_bottomPage > span.p-skip > em:nth-child(1) > b')
        )
    )
    html = browser.page_source.replace('xmlns', 'another_attr')
    #获取第一页
    get_goods_info(keyword,1,html,filename)
    #备用：页面上限
    #max_page_num = int(total_pages[0].text
    for page_num in range(2,max_page_num + 1):
        get_next_page(keyword,page_num,browser,wait,filename)

#翻页
def get_next_page(keyword,page_num,browser,wait,filename):

    next_page_button = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, '#J_bottomPage > span.p-num > a.pn-next > em'))
    )
    next_page_button.click()

    #拉到底部翻页
    for i in range(0,3):
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # 等待时间随机生成，尝试突破反爬虫
        time.sleep(3)

    #京东会在每个页面显示60个商品，其中后30个商品会在拖动过程中展示，"#J_goodsList > ul > li:nth-child(60)确保60个商品都正常加载出来。
    wait.until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#J_goodsList > ul > li:nth-child(60)"))
    )
    # 页面上展示的「第几页」表示的就是当前页数，如果显示的页数和page_num一样，表示翻页成功（即等待到翻页成功为止）。
    wait.until(
        EC.text_to_be_present_in_element((By.CSS_SELECTOR, "#J_bottomPage > span.p-num > a.curr"), str(page_num))
    )
    html = browser.page_source.replace('xmlns', 'another_attr')
    #调用获取商品信息
    get_goods_info(keyword, page_num, html, filename)

#获取页面信息
def get_goods_info(keyword,page,html,filename):
    doc = pq(html)
    li_list = doc('.gl-item').items()
    print('-------------------第' + str(page) + '页的'+keyword+'信息---------------------')
    for item in li_list:
        image_html = item('.gl-i-wrap .p-img')
        keyword_img_url = item.find('img').attr('data-lazy-img')
        if keyword_img_url == "done":
            keyword_img_url = item.find('img').attr('src')
        #去掉两个斜杠
        print('图片地址:' + keyword_img_url[2:])
        item('.p-name').find('font').remove()
        p_name = item('.p-name').find('em').text()
        print('商品名称：' + p_name)
        #价格在class = p-price中的i标签，如<i>99.00</i>
        p_price = str(item('.p-price').find('i').text())
        print('价格：' + p_price)
        # 评论在class = p-commit中的粗体，如<a id="J_comment_100000967034" target="_blank" href="//item.jd.com/100000967034.html#comment"
        # onclick="searchlog(1, '100000967034','0','3','','flagsClk=419904');">6.4万+</a>
        p_commit = item('.p-commit').find('strong').text()
        #调用评论的数据清理函数
        p_commit = commit_clear(p_commit)
        print('评价数量：' + p_commit)
        #店名在class = p-shop中的文字，如<a target="_blank" class="curr-shop hd-shopname" onclick="searchlog(1,'1000011183',0,58)"
        # href="//mall.jd.com/index-1000011183.html?from=pc" title="美的照明京东自营官方旗舰店">美的照明京东自营官方旗舰店</a>
        p_shopname = item('.p-shop').find('a').text()
        print('店铺名称：' + p_shopname)
        print('&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&')
        datas = ([p_name,p_shopname,p_price,p_commit,keyword_img_url])
        #调试使用的datas打印
        #print(datas)
        with open(filename, 'a', newline='', encoding='utf-8-sig')as f:
            write = csv.writer(f)
            write.writerow(datas)
        f.close()
 

def main(argv):
    keyword = ''
    #尝试从参数中获取搜索关键词
    try:
        opts, args = getopt.getopt(argv,"s:")
    except getopt.GetoptError:
        print('-s <keyword>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-s':
            keyword = arg
        else:
            print('-s <keyword>')
            sys.exit()
    #如参数中无法获取，则从配置文件中获取
    if not keyword:
        keyword = default_keyword

    #数据储存的文件名
    save = save_prefix + keyword + '.csv'

    #创建文件头
    file_header(save)
    #爬取网页
    crawl_website(keyword, save)
    
    print('脚本结束，共爬取{0}页数据，储存为：{1}'.format(str(max_page_num), save))

if __name__ == "__main__":
    main(sys.argv[1:])
