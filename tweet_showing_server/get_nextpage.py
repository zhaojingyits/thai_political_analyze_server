from django.http.response import JsonResponse
import pymongo,arrow,json,math
from datetime import date, datetime

class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, date):
            return obj.strftime('%Y-%m-%d')
        else:
            return json.JSONEncoder.default(self, obj)
myclient = pymongo.MongoClient("mongodb://localhost:27017/")

mydb = myclient["thai_analyze_db"]

tweets_collection = mydb['tweets']
china_related_tweets_collection = mydb['china_related_tweets']

def page_items_number_list(total_items, each_page_capacity, page_number):
    page_count = math.ceil(float(total_items)/each_page_capacity)
    return [x for x in range((page_number-1)*each_page_capacity, (page_number)*each_page_capacity)]

def get_page(_type, time, page_capacity, page_number,continue_hours):
    news_requirement = {
        "created_at":{
            "$gte":time.datetime,
            "$lt":time.shift(hours=+continue_hours).datetime,
        },
        "classify":"news",
    }
    discussion_requirement = {
        "created_at":{
            "$gte":time.datetime,
            "$lt":time.shift(hours=+continue_hours).datetime,
        },
        "classify":"discussion",
    }
    china_related_requirement = {
        "created_at":{
            "$gte":time.datetime,
            "$lt":time.shift(hours=+continue_hours).datetime,
        }
    }
    time_start = time.format('YYYY-MM-DD HH:mm:ss')

    if _type == 'news':
        tweets_list = list(tweets_collection.find(news_requirement,{"classify":0,"_id":0}).sort("retweet_count",-1))
    elif _type == 'discussion':
        tweets_list = list(tweets_collection.find(news_requirement,{"classify":0,"_id":0}).sort("retweet_count",-1))
    elif _type == 'china_related':
        tweets_list = list(china_related_tweets_collection.find(news_requirement,{"_id":0}).sort("retweet_count",-1))
    else:
        return Exception()
    total_items = len(tweets_list)
    number_list = page_items_number_list(
        total_items, page_capacity, page_number)
    content = []
    for num in number_list:
        if num < len(tweets_list):
            content.append(tweets_list[num])

    pages_dict = {
        "topic":_type,
        "page_number":page_number,
        "page_capacity":page_capacity,

        'datetime':time_start,
        'continue_hours':12,
        'sorted_by':'retweet',
        "page_content": content,
    }

    return pages_dict

def dump(request):
    _type = request.GET.get("type")
    _time = request.GET.get("time")
    _page_capacity = request.GET.get("capacity")
    _page_number = request.GET.get("num")
    
    res=get_page(_type,arrow.get(_time), int(_page_capacity), int(_page_number),12)
    return JsonResponse(res,encoder=ComplexEncoder)

'''filename = 'd:/nextpage.json'
with open (filename,'w') as f:
    json.dump(get_page('news', arrow.get(2021,2,19), 10, 2,12),f, cls=ComplexEncoder)'''