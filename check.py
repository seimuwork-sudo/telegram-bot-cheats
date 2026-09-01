import urllib.request, json

r = urllib.request.urlopen("https://api.telegram.org/bot8757096551:AAH8AU5FxY2-Zr1AgMek9_nM8fevB45gWJk/getUpdates?offset=-1", timeout=30)
d = json.loads(r.read())
print("Count:", len(d["result"]))
for u in d["result"][-3:]:
    msg = u.get("message", {})
    print(f"Update {u['update_id']}: text={msg.get('text')}, chat={msg.get('chat', {}).get('id')}")
