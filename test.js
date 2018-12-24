$(document).ready(function() {
    if (!window.console) window.console = {};
    if (!window.console.log) window.console.log = function() {};
    var userid = "sz0005";
    var devid = "5bbb42f7f068b50a18077d96";
    wshandler.start(userid, devid);
});
var wshandler = {
    socket: null,
    start: function(userid,devid) {
        // 初始化一个 WebSocket 对象
	    wshandler.socket = new WebSocket("ws://" + location.host + "/websocket");

	    // 建立 web socket 连接成功触发事件
        wshandler.socket.onopen = function (event) {
            console.log("Connection open ...");
            wshandler.socket.send("Hello WebSockets!");
            // 使用 send() 方法发送数据
            var userobj = {"msgid":1,"userid":userid,"devid":devid};
            wshandler.socket.send(JSON.stringify(userobj));
        };

        // 断开 web socket 连接成功触发事件
        wshandler.socket.onclose = function (event) {
            console.log("Connection closed.");
            /*不一定能发送过去*/
            var userobj = {"msgid":2,"userid":userid,"devid":devid};
            wshandler.socket.send(JSON.stringify(userobj));
        };

	    // 接收服务端数据时触发事件
	    wshandler.socket.onmessage = function(event) {
	        console.log( "Received Message: " + evt.data);
            var rs = JSON.parse(event.data);
            wshandler.socket.send("发送数据");
            wshandler.socket.close()
	    }
    }
};




