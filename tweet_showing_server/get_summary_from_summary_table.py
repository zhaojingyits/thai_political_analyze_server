from django.http.response import JsonResponse
import pymongo,arrow,json

myclient = pymongo.MongoClient("mongodb://localhost:27017/")

mydb = myclient["thai_analyze_db"]

summary_collection = mydb['summary']
from datetime import date, datetime

class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, date):
            return obj.strftime('%Y-%m-%d')
        else:
            return json.JSONEncoder.default(self, obj)


def get_summary_from_summary_table(time):
    summary=summary_collection.find_one({"datetime":time.format('YYYY-MM-DD HH:mm:ss')},{"_id":0})
    return summary

def dump(request):
    _fromdate = request.GET.get("from")
    res=get_summary_from_summary_table(arrow.get(_fromdate))
    return JsonResponse(res, encoder=ComplexEncoder)
'''filename = 'd:/pi_x.json'
with open (filename,'w') as f:
    json.dump(get_summary_from_summary_table(arrow.get(2021,2,19)),f, cls=ComplexEncoder)'''