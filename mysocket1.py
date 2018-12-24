#!/usr/bin/env python
# -*- coding:utf-8 -*-
import logging
import tornado.escape
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.websocket
import json
from bson import ObjectId


class ChatSocketHandler(tornado.websocket.WebSocketHandler):
    # 存储每一个人的信息
    users = []

    cache = []
    cache_size = 256

    devlist = {}
    dev_size = 256
    dev = None

    usersockets = {}

    # 判断源origin，对于符合条件的请求源允许链接
    def check_origin(self, origin):
        return True

    def allow_draft76(self):
        # for iOS 5.0 Safari
        return True

    # 连接建立后被调用，客户端建立链接后调用open。
    def open(self):
        print "new client opened===>"
        # 链接上后再进行存储用户信息，self 为每个连接服务器的客户端的对象
        self.users.append(self)
        for user in self.users:
            print(self.request.remote_ip)
            # 主动向客户端发送message消息，message可以是字符串或者字典。
            user.write_message('u[{}]登陆了'.format(self.request.remote_ip))

    # 客户端断开链接调用on_close
    def on_close(self):
        print "new client closed===>"
        self.users.remove(self)
        for user in self.users:
            print(user)
            user.write_message('u[{}]退出登陆了'.format(self.request.remote_ip))


    @classmethod
    def update_dev(cls, dev):
        print "udpate_dev===>", dev
        cls.devlist[dev.get("devid")] = dev
        # if len(cls.devlist) > cls.dev_size:
        #     cls.devlist = cls.devlist[-cls.dev_size:]
        print "udpate_dev2===>", cls.devlist

    @classmethod
    def send_updates(cls, chat):
        print "send_updates====>"
        logging.info("sending message to %d waiters", len(cls.waiters))
        for waiter in cls.waiters:
            try:
                waiter.write_message(chat)
            except:
                logging.error("Error sending message", exc_info=True)



    @classmethod
    def push_task(cls, task):
        print "push_task===>"
        if not task:
            return

        playlists = task.get("playlist", {})
        if not playlists:
            return

        plists = [ObjectId(x) for x in playlists.keys()]

        db = database.database.getDB()
        playlists = db.tb_playlist_profile.find({"_id": {"$in": plists}})
        for v in playlists:
            v["_id"] = str(v.get("_id", None))
            v["worktime"] = task.get("worktime", None)
            print v, 369
            ChatSocketHandler.push_playlist(v)


    @classmethod
    def push_playlist(cls, playlist):
        print "push_playlist===>"
        if not playlist:
            return

        stores_ids = playlist.get("bind")
        db = database.database.getDB()
        terminals = list(db.tb_terminal_profile.find({"_id": {"$in": terminal_obj}}))

        del playlist["bind"]
        xjson = json.dumps(playlist)
        print xjson

        msg = {"msgid": 3, "playlist": xjson}
        print "============================================="
        for t in terminals:
            print t, 444
            for k, v in cls.devlist.iteritems():
                print k, v, t, 555
                print v.get("userid"), t.get("userid")
                if v.get("userid") == t.get("userid"):
                    print 333
                    print k, cls.usersockets[k], msg
                    print cls.usersockets[k].write_message(msg)
                    print "++++++++++++++++++++++++++++"

    def on_message(self, message):
        print "on_message====>"
        logging.info("got message %r", message)
        print "message=", message
        parsed = tornado.escape.json_decode(message)
        if parsed["msgid"] == 1:
            print 'adduser start ...'
            dev = {
                "msgid": parsed.get("msgid"),
                "userid": parsed.get("userid"),
                "devid": parsed.get("devid"),
            }

            ChatSocketHandler.usersockets[parsed["devid"]] = self
            ChatSocketHandler.update_dev(dev)
            return

        if parsed["msgid"] == 2:
            print "close"
            return

        if parsed["msgid"] == 4:
            print 'playlist push result ...'
            msg = {
                "msgid": parsed.get("msgid"),
                "userid": parsed.get("userid"),
                "devid": parsed.get("devid"),
                "result": parsed.get("result"),
            }
