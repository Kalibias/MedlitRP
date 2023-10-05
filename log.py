import pymongo, json

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["chat_pages"]

chat_names = mydb.list_collection_names()

rooms = {}


for y in chat_names:
    print(f"The name of the chat is: {y}")
    rooms[y] = {"messages":[]}
    for j in mydb[y].find({},{ "_id": 0 }):
        # y.append(j)
        print(f"{j} \n THIS IS LOG")

        content = {
        "name": j["name"],
        "message": j["message"],
        "timed": j["timed"]
    }
        rooms[y]["messages"].append(content)
    


print(rooms, "the fuck")




for x in mydb["PXIT"].find({},{ "_id": 0 }):
    print(x)
# raw_logs = open("log.txt", "r")
# logs = json.loads(raw_logs.read())
# print(logs)
# rooms = logs
# raw_logs.close()
