<?php


$varnombre=$_POST['nombre'];
$varasunto=$_POST['asunto'];
$varmail=$_POST['email'];
$varmensaje=$_POST['mensaje'];


$header='From:'.$varmail."\r\n";
$header.="X-Mailer:PHP/".phpversion()."\r\n";
$header.="Mime-Version:1.0";
$header.="Content-Type:text/plain";

$mensaje="Has recibido un mensaje enviado por".$varnombre."\r\n";
$mensaje.="Su e-mail de contacto es:".$varmail."\r\n";
$mensaje.="Contenido: \r\n".$varmensaje."\r\n";

$para='bigdatastudium@gmail.com';
$asunto='Formulario web:'.$varasunto;

mail($para, $asunto, utf8_decode($mensaje),$header);



?>
<script language="javascript">
alert ("Tu mensaje se ha enviado correctamente.");
location.href="contacto_exito.html";
</script>