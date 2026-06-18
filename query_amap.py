"""查询真实 POI 坐标"""
# -*- coding: utf-8 -*-
import urllib.request, urllib.parse, json, io
PY3 = True

key = "47ff8f012ae1c05def4454f0285bbbc9"
queries = [
    u"上海临港万达广场",
    u"LIN舍临港泥城服务式公寓",
    u"上海交通大学附属浦东临港实验中学",
    u"临港泥城苑",
    u"万达未来城",
    u"鸿音路2555号",
    u"五岭路1301号",
    u"云鹃路",
    u"海基六路",
    u"蓝湾天地",
    u"临港人才公寓",
    u"鸿音广场",
    u"宝龙广场",
    u"宜浩欧景",
    u"馨悦名邸",
    u"正茂苑",
    u"临港家园",
    u"海事小区",
    u"水华路",
]

out = []
for q in queries:
    q_enc = urllib.parse.quote(q.encode('utf-8'))
    url = "https://restapi.amap.com/v3/place/text?key=" + key + "&keywords=" + q_enc + "&city=" + urllib.parse.quote(u"上海".encode('utf-8')) + "&extensions=base"
    try:
        req = urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as r:
            raw = r.read().decode('utf-8')
            data = json.loads(raw)
            pois = data.get('pois', [])
            for p in pois[:3]:
                out.append({
                    'query': q,
                    'name': p.get('name'),
                    'address': p.get('address'),
                    'location': p.get('location'),
                    'type': p.get('type'),
                    'adname': p.get('adname'),
                })
            if not pois:
                out.append({'query': q, 'error': 'no result', 'info': data.get('info'), 'raw_count': data.get('count')})
    except Exception as e:
        out.append({'query': q, 'error': str(e)})

with open(r"C:\Users\11390\Desktop\lingshe-petstore-bp\2026-06-16\final\poi_results.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)

print("done", len(out))