from django.http.response import JsonResponse
import stweet as st
import arrow
import json,pythainlp,pymongo
from nltk.book import FreqDist
from keras.preprocessing.sequence import pad_sequences
from keras.preprocessing.text import Tokenizer
from keras.models import load_model
import numpy as np
from pythainlp import word_tokenize
import pandas as pd
# 爬虫获取用户近期信息
def get_user_tweets(username,count):
    search_tweets_task = st.SearchTweetsTask(
        from_username=username,
        language=st.Language.THAI,
        since=arrow.get('2021-03-02T00:00:00.000+00:00'),
        until=arrow.get('2021-03-02T12:00:00.000+00:00'),
        tweets_limit=count
    )
    tweets_collector = st.CollectorTweetOutput()
    web_client = st.RequestsWebClient(
        proxy=st.RequestsWebClientProxyConfig(
            http_proxy='http://127.0.0.1:7890',
            https_proxy='http://127.0.0.1:7890'
        )
    )
    st.TweetSearchRunner(
        search_tweets_task=search_tweets_task,
        tweet_outputs=[tweets_collector, st.JsonLineFileTweetOutput(file_name='D:/thai/my_jl_file.jl')],
        web_client=web_client
    ).run()
    '''st.CsvTweetOutput('D:/thai/output_file_test_030200.csv')],'''
    tweets = tweets_collector.get_scrapped_tweets()
    return tweets


def read_data(file):
    texts = []
    labels = []
    max_len = 0
    data = pd.read_excel(file, engine='openpyxl')
    print(data)
    for idx, row in data.iterrows():
        label = row['label']
        text = row['words']
        cut_text = list(word_tokenize(text))
        max_len = max(max_len, len(cut_text))
        texts.append(' '.join(cut_text))
        labels.append(label)
    assert len(texts) == len(labels)
    print(max_len)
    return texts, labels


def predict(model,tokenizer,thai_str):
    model.load_weights('D:/thai/泰语文本分类/cnn_weights.best.hdf5')
    texts = [' '.join(list(word_tokenize(thai_str)))]
    # print(texts)
    texts = tokenizer.texts_to_sequences(texts)
    maxlen = 126
    X_test = pad_sequences(texts, padding='post', maxlen=maxlen)
    preds = np.argmax(model.predict(X_test), axis=-1)
    return preds


def get_info(tweets):
    texts, labels = read_data("D:/thai/泰语文本分类/comments_classify_dataset.xlsx")
    tokenizer = Tokenizer()
    tokenizer.fit_on_texts(texts)
    X = tokenizer.texts_to_sequences(texts)
    model = load_model('D:/thai/泰语文本分类/save.h5')

    stopwords = [line.rstrip() for line in open('D:/thai/stopwords-th-mod.txt',encoding='utf8')]
    key_words_list=['การเมือง','กษัตริย์','รัฐมนตรี','นโยบาย','สาธิต','นโยบาย','ขบวน','ทหาร','ตำรวจ','ประท้วง','ม็อบ','อันธพาล','ประชาธิปไตย']
    words_of_china=['ประเทศจีน','ฮ่องกง','ปักกิ่ง','เซี่ยงไฮ้','สีจิ้นผิง','ซินเจียง','อุยกูร์','ไต้หวัน','ไจ่อิงเหวิน','พรรคคอมมิวนิสต์จีน','คนจีน','ชาวจีน']
    total_num=len(tweets)
    political_tweets_count=0
    discussion_count=0
    china_related_count=0
    retweet_count=0
    favorite_count=0
    reply_count=0
    quote_count=0
    length_sum=0
    media_count=0
    hashtags_count=0
    #hashtags=[]
    texts=[]
    key_words=[]
    for tweet in tweets:
        # 统计数据
        retweet_count+=tweet.retweet_count
        favorite_count+=tweet.favorite_count
        reply_count+=tweet.reply_count
        quote_count+=tweet.quote_count
        length_sum+=len(tweet.full_text)
        media_count=len(tweet.media)
        hashtags_count=len(tweet.hashtags)
        # 分析文本
        political_flag=False
        china_flag=False
        discussion_flag=False
        text=tweet.full_text
        texts+=word_tokenize(text)
        for word in key_words_list:
            if word in text:
                political_flag=True
                break
        if political_flag:
            pred_res=predict(model,tokenizer,text)[0]
            if pred_res==1:
                discussion_flag=True
        for word in words_of_china:
            if word in text:
                china_flag=True
                break
        # 统计分析结果
        if political_flag:
            political_tweets_count+=1
        if china_flag:
            china_related_count+=1
        if discussion_flag:
            discussion_count+=1
    length_avg=length_sum/total_num
    texts=[w for w in texts if not w in stopwords and pythainlp.util.isthai(w)]
    fdist = FreqDist(texts)
    times=0
    for key in fdist:
        freq=fdist[key]
        if freq<=1 or times>=30:
            break
        key_words.append({"word_name":key,"rank":freq})
        times+=1
    return {
        "user_name": tweets[0].user_name,
        "user_full_name": tweets[0].user_full_name,
        "top_tweets":total_num,
        "key_words":key_words,
        "user_indexes_value":[
            {"mark_name":"政治内容占分析数量比例",
            "mark_description":"该用户有多少涉政推文。",
            "mark_rank":political_tweets_count,
            "full_mark":total_num,
            "mark_result":'该用户讨论政治内容较少。' if political_tweets_count/total_num<0.3 else '该用户讨论政治内容较多。'},
            {"mark_name":"讨论内容占涉政推文比例",
            "mark_description":"该用户有多少涉政推文是倾向性讨论。",
            "mark_rank":discussion_count,
            "full_mark":political_tweets_count,
            "mark_result":'该用户讨论政治内容中倾向性文段较少。' if discussion_count/(political_tweets_count+1)<0.3 else '该用户讨论政治内容中倾向性文段较多。'},
            {"mark_name":"涉华内容占分析数量比例",
            "mark_description":"该用户有多少涉华推文。",
            "mark_rank":china_related_count,
            "full_mark":total_num,
            "mark_result":'该用户讨论涉华内容较少。' if china_related_count/total_num<0.1 else '该用户讨论涉华内容较多。'},
            {"mark_name":"转发量",
            "mark_description":"该用户推文有多少转发量。",
            "mark_rank":retweet_count,
            "full_mark":retweet_count if retweet_count>total_num else total_num,
            "mark_result":'该用户转发量较小。' if retweet_count<total_num else '该用户转发量较大。'},
            {"mark_name":"点赞量",
            "mark_description":"该用户推文有多少点赞量。",
            "mark_rank":favorite_count,
            "full_mark":favorite_count if favorite_count>total_num else total_num,
            "mark_result":'该用户点赞量较小。' if favorite_count<total_num else '该用户点赞量较大。'},
            {"mark_name":"回复量",
            "mark_description":"该用户推文有多少回复量。",
            "mark_rank":reply_count,
            "full_mark":reply_count if reply_count>total_num else total_num,
            "mark_result":'该用户回复量较小。' if reply_count<total_num else '该用户回复量较大。'},
            {"mark_name":"引用量",
            "mark_description":"该用户推文有多少引用量。",
            "mark_rank":quote_count,
            "full_mark":quote_count if quote_count>total_num else total_num,
            "mark_result":'该用户引用量较小。' if quote_count<total_num else '该用户引用量较大。'},
            {"mark_name":"平均长度",
            "mark_description":"该用户推文的平均长度。",
            "mark_rank":length_avg,
            "full_mark":200 if length_avg<200 else length_avg,
            "mark_result":'该用户平均长度较小。' if length_avg<120 else '该用户平均长度处于一般水平。' if length_avg<130 else '该用户平均长度较大。'},
            {"mark_name":"媒体量",
            "mark_description":"该用户推文有多少媒体。",
            "mark_rank":media_count,
            "full_mark":media_count if media_count>total_num else total_num,
            "mark_result":'该用户媒体量较小。' if media_count<total_num*0.6 else '该用户媒体量较大。'},
            {"mark_name":"话题量",
            "mark_description":"该用户推文有多少引用量。",
            "mark_rank":hashtags_count,
            "full_mark":hashtags_count if hashtags_count>total_num else total_num,
            "mark_result":'该用户不经常使用话题。' if hashtags_count<total_num*0.6 else '该用户经常使用话题。'},
        ]
    }

def get_user_info(name,num):
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    mydb = myclient["thai_analyze_db"]
    user_collection = mydb['user']
    col=user_collection.find_one({"user_name":name},{"_id":0})
    if col is not None:
        print(col)
        return col

    t=get_user_tweets(name,num)
    if len(t)<1:
        return {"user_name": name,"user_full_name": '分析失败，缺少足够推文。',"top_tweets":0,"key_words":[],"user_indexes_value":[]}
    else:
        info=get_info(t)
        user_collection.insert_one(info)
        info=info.pop('_id')
        return info

def dump(request):
    _username = request.GET.get("username")
    res=get_user_info('judy_starkk',80)
    return JsonResponse(res)

'''filename = 'd:/pi_x3.json'
with open (filename,'w') as f:
    json.dump(get_user_info('judy_starkk',80),f)'''