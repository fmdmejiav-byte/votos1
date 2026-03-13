<!DOCTYPE html>
<html>
<head>
	<meta charset="utf-8">
	<title>Consultar</title>
	<link rel="stylesheet" href="/static/styles.css">
</head>
<body>
<div class="container">
	<h1>Ingrese su cédula</h1>
	<form action="/resultado" method="POST">
		<input type="text" name="cedula" required>
		<button type="submit">Buscar</button>
	</form>
	<a href="/">Volver al inicio</a>
</div>
</body>
</html>
