#!/usr/bin/env python
# -*- coding:utf-8 -*-
import tornado.web
from tornado.web import RequestHandler
from tornado.httpclient import AsyncHTTPClient   #异步的http请求客户端
import time
import json
from tornado.websocket import WebSocketHandler

class StaticHandler(tornado.web.StaticFileHandler):
    def __init__(self,*args,**kwargs):
        super(StaticHandler,self).__init__(*args,**kwargs)
        self.xsrf_token


class HomeHandler(RequestHandler):
    def get(self, *args, **kwargs):
        self.render('home.html')




    def on_message(self, message):  #客户端发送消息过来时服务器调用on_message
        for user in self.users:
            user.write_message(u'{}说：{}'.format(self.request.remote_ip,message))   #write_message的消息会被前端ws.onmessage方法接收




