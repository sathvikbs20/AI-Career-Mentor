let currentConversationId = null;

function appendUser(msg){
    const box=document.getElementById("chat-box");
    box.innerHTML += `<div class="user"><strong>You:</strong> ${msg}</div>`;
    box.scrollTop=box.scrollHeight;
}

function appendBot(html){
    const box=document.getElementById("chat-box");
    const div=document.createElement("div");
    div.className="bot";
    div.innerHTML=`<strong>Bot:</strong><br>`+html;
    box.appendChild(div);
    box.scrollTop=box.scrollHeight;
}

async function newChat(){

    const title = prompt("Conversation title","New Chat");

    if(title===null) return;

    await fetch("/new_chat",{
        method:"POST",
        headers:{
            "Content-Type":"application/json"
        },
        body:JSON.stringify({
            title:title
        })
    });

    document.getElementById("chat-box").innerHTML="";
    document.getElementById("user-input").value="";

    loadConversations();
}

async function loadConversations(){

    const response = await fetch("/conversations");

    const conversations = await response.json();

    const history =
        document.getElementById("history-list");

    history.innerHTML="";

    conversations.forEach(chat=>{

        const item=document.createElement("div");

        item.className="history-item";

        item.innerText=chat.title;

        item.onclick=()=>{
            openConversation(chat.id);
        };

        history.appendChild(item);

    });

}

async function openConversation(id){

    currentConversationId = id;

    const response = await fetch("/conversation/" + id);

    const messages = await response.json();

    const chatBox =
        document.getElementById("chat-box");

    chatBox.innerHTML = "";

    messages.forEach(message=>{

        chatBox.innerHTML += `
            <div class="user">
                <strong>You:</strong>
                ${message.user}
            </div>

            <div class="bot">
                <strong>Bot:</strong><br>
                ${marked.parse(message.bot)}
            </div>
        `;

    });

    chatBox.scrollTop =
        chatBox.scrollHeight;

}

async function sendMessage(){

    const input =
        document.getElementById("user-input");

    const message =
        input.value.trim();

    if(!message) return;

    appendUser(message);

    input.value="";

    const chatBox =
        document.getElementById("chat-box");

    const typing =
        document.createElement("div");

    typing.className="bot";

    typing.innerHTML="<strong>Bot:</strong> Typing...";

    chatBox.appendChild(typing);

    const response = await fetch("/chat",{

        method:"POST",

        headers:{
            "Content-Type":"application/json"
        },

        body:JSON.stringify({
            message:message
        })

    });

    const reader =
        response.body.getReader();

    const decoder =
        new TextDecoder();

    let text="";

    while(true){

        const {done,value}=await reader.read();

        if(done) break;

        text += decoder.decode(value,{
            stream:true
        });

        typing.innerHTML =
            "<strong>Bot:</strong><br>" +
            marked.parse(text);

        chatBox.scrollTop =
            chatBox.scrollHeight;
    }

    loadConversations();

}

async function loadHistory(){

    const response = await fetch("/history");

    const messages = await response.json();

    const chatBox =
        document.getElementById("chat-box");

    chatBox.innerHTML = "";

    messages.forEach(message=>{

        chatBox.innerHTML += `
            <div class="user">
                <strong>You:</strong>
                ${message.user}
            </div>

            <div class="bot">
                <strong>Bot:</strong><br>
                ${marked.parse(message.bot)}
            </div>
        `;

    });

    chatBox.scrollTop =
        chatBox.scrollHeight;

}

async function clearChat(){

    await fetch("/clear",{
        method:"POST"
    });

    document.getElementById("chat-box").innerHTML="";

}

async function uploadResume(){

    const file =
        document.getElementById("resume-file");

    if(file.files.length===0){

        alert("Please select a PDF.");

        return;

    }

    const formData =
        new FormData();

    formData.append(
        "resume",
        file.files[0]
    );

    const response =
        await fetch("/upload_resume",{
            method:"POST",
            body:formData
        });

    const data =
        await response.json();

    appendBot(
        marked.parse(data.reply)
    );

}

window.onload=function(){

    loadConversations();

    loadHistory();

    document
        .getElementById("user-input")
        .addEventListener(
            "keypress",
            function(e){

                if(e.key==="Enter"){

                    sendMessage();

                }

            }
        );

};

