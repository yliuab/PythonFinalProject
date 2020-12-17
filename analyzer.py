#-*- coding: utf-8 -*-
import sys
import pandas as pd
import numpy as np
import os
import getopt
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif']=['SimHei'] #用来正常显示中文标签
plt.rcParams['axes.unicode_minus']=False #用来正常显示负号

def plot_price_hist(df):
    plt.hist(df['价格'], 50)
    plt.xlabel('价格')
    plt.ylabel('产品数量')
    plt.title('价格直方图')
    plt.grid(True)


def plot_top_stores(df, top):
    df.astype({'评论数量': 'int64'}).dtypes
    #以店铺名称为键，加总评论数量，再取最大的几个值
    grouped = df[['店铺名称','评论数量']].groupby(['店铺名称']).agg({'评论数量':sum}).reset_index().nlargest(top, '评论数量')

    #画一个水平方向的条形图
    fig, ax = plt.subplots(num=None, figsize=(16, 6), dpi=80, facecolor='w', edgecolor='k')
    y_pos = np.arange(len(grouped['店铺名称']))

    ax.barh(y_pos, grouped['评论数量'], align='center')
    ax.set_yticks(y_pos)
    ax.set_yticklabels(grouped['店铺名称'])
    ax.invert_yaxis()  # labels read top-to-bottom
    ax.set_xlabel('评论数量')
    ax.set_title('店铺热度Top' + str(top))


def main(argv):
    filename = 'jd_灯具_bak.csv'
    #尝试从参数中获取数据文件名
    try:
        opts, args = getopt.getopt(argv,"f:")
    except getopt.GetoptError:
        print('-f <filename>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-f':
            filename = arg
        else:
            print('-f <filename>')
            sys.exit()
    #如参数中无法获取文件名，则要求用户输入文件名
    if not filename:
        filename = input('请输入数据文件名: ')

    #判断文件是否存在
    if not os.path.exists(filename):
        print('找不到文件：' + filename + '，程序退出...')
        sys.exit()

    #尝试读取csv文件到pandas dataframe
    try:
        df = pd.read_csv(filename)
    except:
        print('读取csv文件出错...')

    #画价格直方图
    plot_price_hist(df)
    #画店铺热度条形图
    plot_top_stores(df, 5)
    plt.show()

    
if __name__ == "__main__":
    main(sys.argv[1:])
