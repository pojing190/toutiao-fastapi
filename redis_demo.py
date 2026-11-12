import redis

r = redis.Redis(host="127.0.0.1", port=6379, decode_responses=True)

print("ping :", r.ping())
r.set("demo:hello", "world", ex=60)
print("get  :", r.get("demo:hello"))
print("done : 连接成功，客户端工作正常")
