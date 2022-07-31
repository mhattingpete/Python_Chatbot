$(function() {
	$("#chatbox__submit").click(function(e) {
		e.preventDefault();
		var msg = escapeHTML($("#chatbox__input").val());
		if(msg.trim() == ''){
			return false;
		}
		generate_message(msg, 'self');
		setTimeout(function() {      
			generate_repsonse(msg, 'bot');
		}, 1000)
	})
	
	function generate_message(msg, type) {
		var username;
		if(type == 'self'){
			$("#chatbox__input").val('');
			username = 'User';
		}
		else {
			username = 'Bot'
		}
		var e = $(".chatbox__messages").last().clone();
		e.find("p.name").val(username);
		e.find("p.message").text(msg);
		e.hide().fadeIn(300);
		$(".chatbox__logs").append(e);
		$(".chatbox__logs").stop().animate({ scrollTop: $(".chatbox__logs")[0].scrollHeight}, 1000);    
	}

	$.ajaxSetup({
		contentType: "application/json"
	});

	function generate_repsonse(msg) {
		$.post("/get_response", JSON.stringify({msg : msg})).done(function(response) {
			generate_message(response, 'bot');
		});
	}

	var escape = document.createElement('textarea');
	function escapeHTML(html) {
	    escape.textContent = html;
	    return escape.innerHTML;
	}

	function toggle_chatbox() {
		$("#chat__circle").toggle('scale');
		$(".chatbox").toggle('scale');
	}
	
	$("#chat__circle").click(function() {    
		toggle_chatbox();
	})
	
	$(".chatbox__toggle").click(function() {
		toggle_chatbox();
	})
	
})