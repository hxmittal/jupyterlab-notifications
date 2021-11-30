import sqlite3
import functools
import json
import os
from pathlib import Path
from typing import Tuple, Union
import time

import tornado
import tornado.websocket as websocketT
from jupyter_server.base.handlers import APIHandler
from jupyter_server.utils import url_path_join
from packaging.version import parse

wss = []

d = {}

class wsHandler(websocketT.WebSocketHandler):
    def open(self):
        print('Online')
        if self not in wss:
            wss.append(self)
            d[self] = ""
    def on_message(self, message):
        print(message, "onmessage")
        d[self] = message
        print("d", d) 
        for client in wss:
            if client != self:
                client.write_message(message)

    def on_close(self):
        print('Offline')
        if self in wss:
            wss.remove(self)


def wsSend(message, users = ["edge"]):
    print(d, users)
    if users == ["*"]:
        for ws in wss:
            ws.write_message(message)
    else:
            
        for ws in wss:
            if d[ws] in users:
                print(d, d[ws])
                ws.write_message(message)


NAMESPACE = "/api"


conn = sqlite3.connect('notif.db')
c = conn.cursor()
try:
    c.execute('''CREATE TABLE IF NOT EXISTS notifs (notificationId  INTEGER PRIMARY KEY, origin text, title text, body text, subject text, recipient text, linkUrl text, ephemeral boolean, notifTimeout INTEGER, notifType text, created INTEGER)''')
except sqlite3.OperationalError:
    pass
except:
    print("BOOM?")
c.close()


class notifyBaseHandler(APIHandler):
    @tornado.web.authenticated
    async def get(self, path: str = ""):

        args = (self.request.arguments)
        created, origin = "", ""
        con = sqlite3.connect('notif.db')
        cur = con.cursor()
        data = ""
        print(args, "arguments")
        if "created" in args and "origin" in args and "recipient" in args:
            created, origin, recipient = args["created"][0].decode(
            ), args["origin"][0].decode(), args["recipient"][0].decode() 
            cur.execute('SELECT * FROM notifs where created > ? and origin = ? and (recipient = ? or recipient = "*")',
                        (str(created), str(origin), str(recipient)))
            data = cur.fetchall()
        if "created" in args and "origin" in args:
            created, origin = args["created"][0].decode(
            ), args["origin"][0].decode()
            cur.execute('SELECT * FROM notifs where created > ? and origin = ?',
                        (str(created), str(origin)))
            data = cur.fetchall()
        if "created" in args and "recipient" in args:
            created, recipient = args["created"][0].decode(
            ), args["recipient"][0].decode()
            cur.execute('SELECT * FROM notifs where created > ? and (recipient = ? or recipient = "*")',
                        (str(created), str(recipient)))
            data = cur.fetchall()
        if "origin" in args and "recipient" in args:
            origin, recipient = args["origin"][0].decode(
            ), args["recipient"][0].decode()
            cur.execute('SELECT * FROM notifs where origin = ? and (recipient = ? or recipient = "*")',
                        (str(origin), str(recipient)))
            data = cur.fetchall()
        elif "created" in args:
            created = args["created"][0].decode()
            cur.execute('SELECT * FROM notifs where created > ?',
                        (str(created),))
            data = cur.fetchall()
        elif "origin" in args:
            origin = args["origin"][0].decode()
            cur.execute('SELECT * FROM notifs where origin = ?',
                        (str(origin),))
            data = cur.fetchall()
        elif "recipient" in args:
            recipient = args["recipient"][0].decode()
            cur.execute('SELECT * FROM notifs where (recipient = ? or recipient = "*")',
                        (str(recipient),))
            data = cur.fetchall()
        else:
            cur.execute('SELECT * FROM notifs')
            data = cur.fetchall()[-20:]
        responses = []
        for row in data:
            response = {"notificationId": row[0], "origin": row[1], "title": row[2], "body": row[3],
                        "subject": row[4], "recipient": row[5] ,"linkUrl": row[6], "ephemeral": row[7], 
                        "notifTimeout": row[8], "notifType": row[9], "created": row[10]}
            responses.append(response)
        self.finish(json.dumps({"Response": responses[::-1]}))

    @tornado.web.authenticated
    async def post(self, path: str = ""):
        con = sqlite3.connect('notif.db')
        cur = con.cursor()
        # input_data = self.get_json_body()
        # data = {"greetings": "Hello {}, enjoy JupyterLab!".format(input_data["name"])}
        # self.finish(json.dumps(data))
        data = self.get_json_body()["INotificationEvent"]
        # print(data)
        origin = data["origin"]
        title = data["title"]
        body = data["body"]
        subject = data["subject"]
        recipients = data["recipient"] 
        linkUrl = data["linkUrl"]
        ephemeral = data["ephemeral"]
        notifTimeout = data["notifTimeout"]
        notifType = data["notifType"]
        created = time.time_ns()
        # print(recipients, "recep", type(recipients))
        for recipient in recipients:
            insertData = (origin, title, body, subject, recipient, linkUrl, ephemeral,
                        notifTimeout, notifType, created)
            cur.execute(
                "INSERT INTO notifs (origin, title, body, subject, recipient, linkUrl, ephemeral, notifTimeout, notifType, created) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", insertData)
            rowId = cur.lastrowid
        con.commit()
        con.close()
        self.set_status(201)
        self.add_header("location", str(rowId))
        # self.write(json.dumps({"RowId":str(rowId)}))
        self.finish(json.dumps({"RowId": str(rowId)}))
        self.flush()
        # tornado.ioloop.IOLoop.make_current()
        # time.sleep(3)
        # tornado.ioloop.IOLoop.current().spawn_callback(wsSend, str(rowId))
        # print("here sennding ws")
        wsSend(str(rowId), recipients)


class notifyIDHandler(APIHandler):
    @tornado.web.authenticated
    async def get(self, notificationId):
        if (not notificationId.isnumeric()):
            raise tornado.web.HTTPError(400)
        print(notificationId, "THIS WHAT I GOT")
        con = sqlite3.connect('notif.db')
        cur = con.cursor()

# Create table
        cur.execute('SELECT * FROM notifs where notificationId = ?',
                    (notificationId, ))
        data = cur.fetchall()
        response = {}
        for row in data:
            response = {"notificationId": row[0], "origin": row[1], "title": row[2], "body": row[3],
                        "subject": row[4], "recipient": row[5] ,"linkUrl": row[6], "ephemeral": row[7], 
                        "notifTimeout": row[8], "notifType": row[9], "created": row[10]}
            # responses.append({"INotificationResponse": response})
        #print(response)
        self.finish(json.dumps({"Response": response}))


def setup_handlers(web_app):
    """
    Setups all of the git command handlers.
    Every handler is defined here, to be used in git.py file.
    """

    handlers = [
        ("/api/ws", wsHandler),
        ("/api/notifications", notifyBaseHandler),
        (r"/api/notifications/([^/]+)", notifyIDHandler),
    ]
    base_url = web_app.settings["base_url"]

    notify_handlers = [
        (url_path_join(base_url, NAMESPACE + endpoint), handler)
        for endpoint, handler in handlers
    ]

    web_app.add_handlers(".*", handlers)
