#!/usr/bin/env python
# -*- coding:utf-8 -*-
import logging
import tornado.escape
import tornado.ioloop
import tornado.options
import tornado.web
from tornado.websocket import WebSocketHandler
import os.path

from tornado.options import define, options
define("port", default=8888, help="run on the given port", type=int)

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", MainHandler),
            (r"/chat", ChatSocketHandler),
        ]
        settings = dict(
            cookie_secret="__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies=True,
        )
        tornado.web.Application.__init__(self, handlers, **settings)


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("home.html")


class ChatSocketHandler(WebSocketHandler):
    # 存储每一个人的信息。存储的是所有登录这个网站服务器的人的信息。服务器发送信息给所有人。
    waiters = set()
    # 存放指定的人，以便于服务器发送信息给某一个人或者指定的人。
    usersockets = {}

    cache = []
    cache_size = 256

    devlist = {}
    dev_size = 256
    dev = None

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
        ChatSocketHandler.waiters.add(self)
        ChatSocketHandler.send_updates("我们组建一个大家庭！！！")

    # 客户端断开链接调用on_close
    def on_close(self):
        print "new client closed===>"
        ChatSocketHandler.waiters.remove(self)

    @classmethod
    def update_cache(cls, chat):
        cls.cache.append(chat)
        if len(cls.cache) > cls.cache_size:
            cls.cache = cls.cache[-cls.cache_size:]

    @classmethod
    def update_dev(cls, dev):
        cls.devlist[dev.get("devid")] = dev

    @classmethod
    def send_updates(cls, chat):
        logging.info("sending message to %d waiters", len(cls.waiters))
        for waiter in cls.waiters:
            try:
                waiter.write_message(chat)
            except:
                logging.error("Error sending message", exc_info=True)

    # 客户端发送消息过来时服务器调用on_message
    def on_message(self, message):
        # 如果前端发的数据是字典，需要转一下
        parsed = tornado.escape.json_decode(message)
        ChatSocketHandler.send_updates("有消息进来啦")
        if (parsed["msgid"] == 1):
            user = {
                "msgid": parsed.get("msgid"),
                "id": parsed.get("id"),
                "content": parsed.get("content"),
            }
            ChatSocketHandler.usersockets[parsed["id"]] = self
            ChatSocketHandler.send_updates(user)
            return

        if (parsed["msgid"] == 2):
            chat = {
                "msgid": parsed.get("msgid"),
                "id": parsed.get("id"),
                "content": parsed.get("content"),
                "to":parsed.get("to"),
            }
            ChatSocketHandler.update_cache(chat)
            for i in parsed.get("to"):
                chat["to"] = i
                ChatSocketHandler.usersockets[i].write_message(chat)
            return


if __name__ == "__main__":
    tornado.options.parse_command_line()
    app = Application()
    # app.listen(8080)
    app.listen(options.port)
    print("visit at", "http://127.0.0.1:%s" % options.port)
    tornado.ioloop.IOLoop.instance().start()
