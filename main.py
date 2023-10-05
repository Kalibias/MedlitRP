from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import join_room, leave_room, send, SocketIO
import random, json, datetime
from string import ascii_uppercase
import pymongo

log_client = pymongo.MongoClient("mongodb://localhost:27017/")

log_db = log_client["chat_pages"]
# mycol = log_db["PXIT"]


app = Flask(__name__)
app.config["SECRET_KEY"] = "hjhjsdahhds"
socketio = SocketIO(app)



rooms = {}
room_list = log_db.list_collection_names()

for y in room_list:
    rooms[y] = {"messages":[]}
    for j in log_db[y].find({},{ "_id": 0 }):
        
        content = {
        "name": j["name"],
        "message": j["message"],
        "timed": j["timed"]
    } 
        rooms[y]["messages"].append(content)
        
        
print(rooms)


def generate_unique_code(length):
    while True:
        code = ""
        for _ in range(length):
            code += random.choice(ascii_uppercase)
        
        if code not in rooms:
            break
    
    return code

@app.route("/", methods=["POST", "GET"])
def home():
    session.clear()
    if request.method == "POST":
        name = request.form.get("name")
        code = request.form.get("code")
        room_name = request.form.get("room")
        join = request.form.get("join", False)
        create = request.form.get("create", False)

        if not name:
            return render_template("home.html", error="Please enter a name.", code=code, name=name)

        if join != False and not code:
            return render_template("home.html", error="Please enter a room code.", code=code, name=name)
        
        room = code
        if create != False:
            room = generate_unique_code(4)
            rooms[room] = {"messages": []}
            new_col = log_db[f"{room}"]
            time = datetime.datetime.now()
            content = {
                "name": "DIATTA",
                "message": "Welcome.",
                "timed" : time.strftime("%m/%d/%y, %H:%M:%S %p")
                # 10/3/2023, 2:32:43 PM
                 }
            new_col.insert_one(content)

        elif code not in rooms:
            return render_template("home.html", error="Room does not exist.", code=code, name=name)
        
        session["room"] = room
        session["name"] = name
        return redirect(url_for("room"))

    return render_template("home.html", name="Nexhi")

@app.route("/room")
def room():
    room = session.get("room")
    if room is None or session.get("name") is None or room not in rooms:
        return redirect(url_for("home"))

    return render_template("room.html", code=room, messages=log_db[room].find({},{ "_id": 0 }))

@socketio.on("message")
def message(data):
    room = session.get("room")
    if room not in room_list:
        return 
    time = datetime.datetime.now()
    content = {
        "name": session.get("name"),
        "message": data["data"],
        "timed" : time.strftime("%m/%d/%y, %H:%M:%S %p")
        # 10/3/2023, 2:32:43 PM
    }
    send(content, to=room)
    
    # Logs the messages into the room.
    chat_room = log_db[room]
    chat_room.insert_one(content)

    

    print(f"{session.get('name')} said: {data['data']}")
    print(rooms)

@socketio.on("connect")
def connect(auth):
    room = session.get("room")
    name = session.get("name")
    if not room or not name:
        return
    if room not in rooms:
        leave_room(room)
        return
    
    join_room(room)
    send({"name": name, "message": "has entered the room"}, to=room)
    print(f"{name} joined room {room}")

@socketio.on("disconnect")
def disconnect():
    room = session.get("room")
    name = session.get("name")
    leave_room(room)
    
    send({"name": name, "message": "has left the room"}, to=room)
    print(f"{name} has left the room {room}")
    

if __name__ == "__main__":
    socketio.run(app, debug=True)
    