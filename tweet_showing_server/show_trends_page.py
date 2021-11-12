from django.http.response import JsonResponse
import pymongo,arrow

myclient = pymongo.MongoClient("mongodb://localhost:27017/")

mydb = myclient["thai_analyze_db"]


basic_info_collection = mydb['basic_info']

key_words=[('การเมือง','政治'),('กษัตริย์','国王'),('รัฐมนตรี','部长'),('นโยบาย','政策'),('ขบวน','游行'),('ทหาร','士兵'),('ตำรวจ','警察'),('ประท้วง','抗议'),('ม็อบ','暴民'),('อันธพาล','暴徒'),('ประชาธิปไตย','民主')]
words_of_china=[('ประเทศจีน','中国'),('ฮ่องกง','香港'),('ปักกิ่ง','北京'),('เซี่ยงไฮ้','上海'),('สีจิ้นผิง','习近平'),('ซินเจียง','新疆'),('อุยกูร์','维吾尔'),('ไต้หวัน','台湾'),('ไจ่อิงเหวิน','蔡英文'),('พรรคคอมมิวนิสต์จีน','中国共产党'),('คนจีน','中国人'),('ชาวจีน','华人')]

def dict_sum_topics_format(dict_sum_topics,keys,topics_value):
    summary_keyword=''
    summary_china_keyword=''
    matched_key_words=[]
    matched_china_words=[]
    list=[]
    for x in dict_sum_topics:
        list.append({"word":x[0],"rank":x[1]})
    for x in list:
        this_word=x['word']
        this_rank=x['rank']
        if len(matched_key_words)<5:
            for v in key_words:
                if v[0] in this_word:
                    # print('keyword match!')
                    matched_key_words.append(v)
                    summary_keyword+='涉政关键词'+v[0]+'(含义为“'+str(v[1])+'”)在这段时间关注度较高，共被查询到'+str(this_rank)+'次。'
        for v in words_of_china:
            if v[0] in this_word:
                # print('China keyword match!')
                matched_china_words.append(v)
                summary_china_keyword+='中国关键词'+v[0]+'(含义为“'+str(v[1])+'”)在这段时间关注度较高，共被查询到'+str(this_rank)+'次。'

    ranks=[]
    for v in matched_key_words+matched_china_words:
        this_trend_value=[]
        for daily_topic in topics_value:
            if v[0] not in daily_topic.keys():
                this_trend_value.append(0)
            else:
                this_trend_value.append(daily_topic[v[0]])
        ranks.append({'value_name':'关键词'+v[0]+'(中文含义：'+v[1]+')热度(0表示热度在当天未达到前200)',"this_trend_value":this_trend_value,"this_trend_key":keys})
    return list, summary_keyword+summary_china_keyword,ranks
def get_trends(fromtime,totime):
    time=fromtime
    keys=[]
    tweets_count_value=[]
    retweet_value=[]
    favorite_value=[]
    reply_value=[]
    quote_value=[]
    hashtag_value=[]
    verified_value=[]
    media_value=[]
    length_avg_value=[]
    topics_value=[]
    while time<=totime:
        timestr=time.format('YYYY-MM-DD HH:mm:ss')
        summary=basic_info_collection.find_one({"datetime":timestr})
        keys.append(summary['datetime'])
        tweets_count_value.append(summary['tweets_count'])
        retweet_value.append(summary['retweet'])
        favorite_value.append(summary['favorite'])
        reply_value.append(summary['reply'])
        quote_value.append(summary['quote'])
        hashtag_value.append(summary['hashtag'])
        verified_value.append(summary['verified'])
        media_value.append(summary['media'])
        length_avg_value.append(summary['length_avg'])
        topic_dict={}
        for v in summary['topics']:
            topic_dict[v['word']]=v['rank']
        topics_value.append(topic_dict)
        time=time.shift(hours=+12)
    dict_sum_topics={}
    for v in topics_value:
        for key in v:
            value=v[key]
            if key not in dict_sum_topics.keys():
                dict_sum_topics[key]=value
            else:
                dict_sum_topics[key]+=value
    dict_sum_topics=sorted(dict_sum_topics.items(), key=lambda d:d[1], reverse = True )
    # print(dict_sum_topics)
    topics_info,summary_info,ranks=dict_sum_topics_format(dict_sum_topics,keys,topics_value)
    if len(topics_info)>20:
        topics_info=topics_info[:20]
    print(summary_info)
    return {
        "from_datetime": fromtime.format('YYYY-MM-DD HH:mm:ss'),
        "to_datetime": totime.format('YYYY-MM-DD HH:mm:ss'),
        "topics":topics_info,
        "summary":summary_info,
        "trends_results": [
            {
                "value_name": "推文数",
                "this_trend_value":tweets_count_value,
                "this_trend_key":keys,
            },
            {
                "value_name": "转发数",
                "this_trend_value":retweet_value,
                "this_trend_key":keys,
            },
            {
                "value_name": "点赞数",
                "this_trend_value":favorite_value,
                "this_trend_key":keys,
            },
            {
                "value_name": "回复数",
                "this_trend_value":reply_value,
                "this_trend_key":keys,
            },
            {
                "value_name": "引用数",
                "this_trend_value":quote_value,
                "this_trend_key":keys,
            },
            {
                "value_name": "话题数",
                "this_trend_value":hashtag_value,
                "this_trend_key":keys,
            },
            {
                "value_name": "认证用户推文数",
                "this_trend_value":verified_value,
                "this_trend_key":keys,
            },
            {
                "value_name": "媒体数",
                "this_trend_value":media_value,
                "this_trend_key":keys,
            },
            {
                "value_name": "平均长度",
                "this_trend_value":length_avg_value,
                "this_trend_key":keys,
            },
        ]+ranks
    }

def dump(request):
    _fromdate = request.GET.get("from")
    _todate = request.GET.get("to")
    res=get_trends(arrow.get(_fromdate),arrow.get(_todate))
    return JsonResponse(res)

'''filename = 'd:/pi_x.json'
with open (filename,'w') as f:
    json.dump(get_trends(arrow.get(2020,2,19),arrow.get(2020,2,28)),f)'''