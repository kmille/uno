$(document).ready(function() {
    $.notifyDefaults({
        placement: { from: "bottom", align: "right" },
    });


    var url = $(location).attr('href');
    var game_id = url.split("/")[4];
    var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
    var chatsock = new ReconnectingWebSocket(ws_scheme + '://' + window.location.host + "/game" + window.location.pathname);
    var your_turn = false;


    chatsock.onopen = function() { 
        var message = {
            action: "ping",
            game_id: game_id,
        }
        chatsock.send(JSON.stringify(message));
    };

    var display_state = function(data) {
        $("#your_cards").html("");
        for(i=0; i < data.cards.length; i++) {
            img = "<img id=\"" + data.cards[i].id + "\" style=\"width:30%;max-height:20%;\" src=\"/static/img/"+ data.cards[i].link + "\">";
            $("#your_cards").append(img);
        }
        
        $("#top").html("");
        img = "<img id=\"" + data.top.id + "\" style=\"width:30%;max-height:20%;\" src=\"/static/img/"+ data.top.link + "\">";
        $("#top").html(img);
        
        $("#players").html("");
        for(i=0; i < data.players.length; i++) {
            text = data.players[i]['name'] + " (" + data.players[i]['cards'] + ") <br>" 
            $("#players").append(text);
         }
         $("#players").append("<br>Turn: " + data.turn);
         if(data.your_turn == true) {
            your_turn = true;
            $("#players").append("<p style=\"color:red\" >It's your turn!</p>");
            $("#turn_small").html("<h4 style='color:red; text-align:center;'>It's your turn!</h4>");
         } else {
             your_turn = false;
            $("#turn_small").html("<h4 style='text-align:center;'>It's NOT your turn!</h4>");
         }
    };

    var send = function(message) {
        if(your_turn == true) {
            chatsock.send(JSON.stringify(message));
        } else {
            console.log("It's not your turn");
        }
    };

    chatsock.onmessage = function(message) {
        var data = JSON.parse(message.data);
        if(data.action == "game_state") {
            display_state(data);
        }
        if(data.action == "reload_state") {
           var message = {
               action: "get_state",
               game_id: game_id,
           }
           chatsock.send(JSON.stringify(message));
        }
        if(data.action == "get_color") {
		   $("#color-modal").modal('show');
        }
        if(data.action == "end_game") {
            $("#top").empty();
            $("#turn_small").empty();
            $("#players").empty()
            $("#your_cards").html(data.msg);
            $("#next").hide()
            $("#throw").hide()
        }
        if(data.action == "msg") {
            $.notify(data.content, { 
                            type: "info",
                            delay: 40,
            });
        }
    };
    
    
	
    $('[id^="color"]').click(function(data) {
       var color_id = data.currentTarget.id.match(/\d/);
	   var message = {
		   action: "set_color",
		   game_id: game_id,
		   color: color_id[0],
	   }
       send(message);
       $("#color-modal").modal("hide");
       return false;
    });

    $("#throw").click(function(data) {
        var message = {
            action: "throw",
            game_id: game_id,
        }
        send(message);
        return false;
    });
    
    $("#next").click(function(data) {
        var message = {
            action: "next",
            game_id: game_id,
        }
        send(message);
        return false;
    });
    
    $("body").on('click', 'img', function(data) {
        var message = {
            action: "move",
            game_id: game_id,
            id: data.target.id,
        }
        send(message);
        return false;
    });
});

