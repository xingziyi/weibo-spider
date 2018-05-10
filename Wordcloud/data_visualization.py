from scipy.misc import imread
from wordcloud import WordCloud, ImageColorGenerator
import redis
import matplotlib.pyplot as plt
import random
    # 设置词云属性
color_mask = imread('background.jfif')
redis_connection = redis.Redis(host='127.0.0.1', port=6379, db=0)
wordsnum = redis_connection.dbsize()
wordcloud = WordCloud(font_path="simhei.ttf",   # 设置字体可以显示中文
                    background_color="white",       # 背景颜色
                    max_words=7000,                  # 词云显示的最大词数
                    mask=color_mask,                # 设置背景图片
                    max_font_size=40,              # 字体最大值
                    random_state=42,
                    width=1920, height=1080, margin=0,# 设置图片默认的大小,但是如果使用背景图片的话,                                                   # 那么保存的图片大小将会按照其大小保存,margin为词语边缘距离
                    )


    # 生成词云, 可以用generate输入全部文本,也可以我们计算好词频后使用generate_from_frequencies函数
redis_connection = redis.Redis(host='127.0.0.1', port=6379, db=0)
word_frequence = dict()
for i in range(1,7000):
    word_frequence[redis_connection.get(i).decode('utf-8')] = random.randint(1,50);

#word_frequence = {for x in words_stat.head(100).values}
# word_frequence_dict = {}
# for key in word_frequence:
#     word_frequence_dict[key] = word_frequence[key]

wordcloud.generate_from_frequencies(word_frequence)#word_frequence_dict)
    # 从背景图片生成颜色值  
image_colors = ImageColorGenerator(color_mask) 
    # 重新上色
wordcloud.recolor(color_func=image_colors)
    # 保存图片
wordcloud.to_file('output.png')
plt.imshow(wordcloud)
plt.axis("off")
plt.show()