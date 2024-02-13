

// chat.js

// ------------------------------------------------------------------------------------------
// 문자열 제어 관련 

var logTextArea = document.getElementById('logTextArea'); // 로그 텍스트 공간
var textArea = document.getElementById('textArea'); // 채팅 텍스트 공간
var textBox = document.getElementById('msg'); // 메시지 입력창
var hiddenUserId = document.getElementById('hidden_userId'); // 사용자 id hidden input
var hiddenChatId = document.getElementById('hidden_chatId'); // 채팅방 id hidden input
logTextArea.value = null;
textArea.value = null;
var LINE_STR = "----------------------------------------"
var SPACE_STR = "                                         "
var STR_MAX_SIZE = 20;

// ------------------------------------------------------------------------------------------
// 웹소켓 관련


//var webSocket = new WebSocket("ws://182.228.58.73:51954");
var webSocket = new WebSocket("ws://192.168.219.8:51954");
// 소켓 접속이 되면 호출되는 함수
webSocket.onopen = function(message){
    logTextArea.value += "server connect...\n";
    webSocket.send("chatId," + hiddenUserId.value);
    //webSocket.send("chatId," + window.sessionStorage.getItem("id"));
};

// 소켓 접속이 끝나면 호출되는 함수
webSocket.onclose = function(message){
    logTextArea.value += "server disconnect...\n";
};

// 소켓 통신중 오류가 발생하면 호출되는 함수
webSocket.onerror = function(message){
    logTextArea.value += "error...\n";
    
};

/*
// 소켓 서버로부터 메시지가 오면 호출되는 함수
webSocket.onmessage = function(message){
    logTextArea.value += "recieve data = " + message.data + "\n";
};
*/

/*
// 소켓 서버로 메시지 보내는 함수
function sendMessage(){
    var message = ;
    // 웹소켓 서버로 보냄
    webSocket.send(message.value);
    // 값 초기화
    message.value="";
}
*/

//webSocket.close() // 소켓 닫음

// ------------------------------------------------------------------------------------------

function autoScroll(){
    document.getElementById("textArea").scrollTop = document.getElementById("textArea").scrollHeight;
}

function makeMsg(data, userId){
    var inData = data;
    var printData = "";
    var spaceData = "";
    if(hiddenUserId.value == userId){
        printData = SPACE_STR;
        spaceData = SPACE_STR;
    }
    for(var i = 1; i <= inData.length; i++){
        printData += inData[i-1];
        if(i % STR_MAX_SIZE == 0){
            printData += "\n" + spaceData;
        }
    }
    printData += "\n\n";
    return printData;
}

function sendMsg(){
    var inData = textBox.value;
    textBox.value=null;
    printData = makeMsg(inData, hiddenUserId.value)
    webSocket.send(inData);
    textArea.value += printData;
    autoScroll()
}

webSocket.onmessage = function(message){
    var inData = message.data;
    var userId = "";
    textBox.value=null;
    printData = makeMsg(inData, userId)
    textArea.value += printData;
    autoScroll()
};

/*
function sendMsg(){
    var inData = textBox.value;
    var printData = SPACE_STR;
    if(inData.length < 1) return;
    for(var i = 1; i <= inData.length; i++){
        printData += inData[i-1];
        if(i % STR_MAX_SIZE == 0){
            printData += "\n" + SPACE_STR;
        }
    }
    textBox.value=null;
    webSocket.send(inData);
    textArea.value += printData + "\n\n";
    autoScroll()
}

webSocket.onmessage = function(message){
    var inData = message.data;
    var printData = "";
    var spaceData = "";
    if(inData.length < 1) return;
    for(var i = 1; i <= inData.length; i++){
        printData += inData[i-1];
        if(i % STR_MAX_SIZE == 0){
            printData += "\n";
        }
    }
    textBox.value=null;
    textArea.value += printData + "\n\n";
    autoScroll()
};
 */

function enterkey(){
    // 엔터키 눌렸을 때
    if(window.event.keyCode==13){
        //alert("엔터 감지");
        sendMsg();
    }
}

// ------------------------------------------------------------------------------------------








