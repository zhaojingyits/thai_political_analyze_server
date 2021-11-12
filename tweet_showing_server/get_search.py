import stweet as st
from django.http.response import JsonResponse
def tweet_to_dict(ex):
    medias=[]
    for med in ex.media:
        medias.append({'url':med.url,'type':med.type})
    return {"created_at": ex.created_at.format(),"id_str": ex.id_str,"conversation_id_str": ex.conversation_id_str,"full_text": ex.full_text,"lang": ex.lang,"favorited": ex.favorited,"retweeted": ex.retweeted,"retweet_count": ex.retweet_count,"favorite_count": ex.favorite_count,"reply_count": ex.reply_count,"quote_count": ex.quote_count,"quoted_status_id_str": ex.quoted_status_id_str,"quoted_status_short_url": ex.quoted_status_short_url,"quoted_status_expand_url": ex.quoted_status_expand_url,"user_id_str": ex.user_id_str,"user_name": ex.user_name,"user_full_name": ex.user_full_name,"user_verified": ex.user_verified,"in_reply_to_status_id_str": ex.in_reply_to_status_id_str,"in_reply_to_user_id_str": ex.in_reply_to_user_id_str,"hashtags":ex.hashtags,"urls":ex.urls,"media":medias}


def get_search_result(keyword,count):
    search_tweets_task = st.SearchTweetsTask(
        any_word=keyword,
        language=st.Language.THAI,
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
    tweets = tweets_collector.get_scrapped_tweets()
    tdicts=[]
    users={}
    for t in tweets:
        name=t.user_name
        if name in users:
            users[name]+=1
        else:
            users[name]=1
        tdicts.append(tweet_to_dict(t))
    users=sorted(users.items(), key=lambda d:d[1], reverse = True )
    u=[]
    for v in users:
        u.append({"name":v[0],"rank":v[1]})
    return tdicts,u

def get_search_result_dict(keyword,count):
    t,us=get_search_result(keyword,count)
    return {"keyword":keyword,"count":count,"users":us,"tweets_page":{
        "datetime":'1900-00-00 00:00:00',
        "continue_hours":12,
        "topic":'search',
        "page_number":1,
        "sorted_by":"none",
        "page_content":t
    }}

'''filename = 'd:/pi_x.json'
with open (filename,'w') as f:
    json.dump(get_search_result_dict('ไต้หวัน',80),f)'''

def dump(request):
    _keyword = request.GET.get("keyword")
    _count = request.GET.get("count")
    res=get_search_result_dict(_keyword,int(_count))
    return JsonResponse(res)