import xml.etree.ElementTree as ET
import requests
from bs4 import BeautifulSoup
from lxml import etree


def obtener_datos(doc_xml):
    """Obtiene el texto de los archivos html contenidos en el xml.
    """
    # Comprobamos que el xml esté bien formado
    doc = etree.parse(doc_xml)
    xmlschema_doc = etree.parse("./data/webs_lenguajes.xsd")
    xmlschema = etree.XMLSchema(xmlschema_doc)
    if xmlschema.validate(doc)== False:
        raise ValueError(f"El documento {doc_xml} no está bien formado.")

    # Leemos del xml los lenguajes y sus webs
    arbol = ET.parse(doc_xml)
    root = arbol.getroot()
    webs_lenguajes = {}
    for lenguaje in root:
        webs_lenguajes[lenguaje.attrib.get("nombre")] = [web.text for web in lenguaje]
    
    # Obtenemos los datos para cada lenguaje
    cotenidos = []
    contenido_lenguaje = {}
    for leng, pags in webs_lenguajes.items():
        datos = ""
        for pag in pags:
            response = requests.get(pag)
            soup = BeautifulSoup(response.text, 'html.parser')
            p = soup.find_all("p")
            for parrafo in p:
                datos = " ".join([datos, parrafo.text])
        contenido_lenguaje[leng] = datos

    return contenido_lenguaje

def limpiar_datos(palabras):
    """Limpia las palabras que se encuentran entre las 100 + usadas en español
    
    Además, esta función devuelve un conjunto con las 200 palabras más
    usadas del lenguaje.
    """
    # Cargamos la lista de las 100 formas más usadas en castellano
    formas_usadas = []
    with open("./data/100_formas.csv", "r", encoding="utf8") as archivo:
        contenido = iter(archivo.readlines())
        next(contenido)
        for linea in contenido:
            formas_usadas.append(linea.strip())
        archivo.close()
    formas_usadas.append("")
    # Quitamos esas palabras del contenido
    palabras_limpiadas = []
    for palabra, frecuencia in palabras.items():
        if palabra in formas_usadas:
            pass
        else:
            palabras_limpiadas.append(palabra)
    # Devolvemos un conjunto con las 200 palabras más usadas
    palabras200 = set()
    for i, palabra in enumerate(palabras_limpiadas):
        if i >= 200: break
        palabras200.add(palabra)
    return palabras200

def contar_palabras(cadena):
    """ Cuenta las veces que cada palabra se repite en una cadena de texto."""

    # Este diccionario contendrá la palabra y el número de veces que se repite
    palabras = {}
    # Eliminamos los signos de puntuación
    puntuacion = (
        ".", ",", ":", ";", "-", "_", "¿",
        "?", "¿", "!", "(", ")", "|", "\"", "'"
    )
    
    # Recorremos las palabras
    for palabra in cadena.split():
        # Pasamos las palabras a minúsuclas
        palabra = palabra.lower()
        # Eliminamos los signos de puntuación al final de las palabra
        while palabra.endswith(puntuacion):
            palabra = palabra[:-1]
        # Eliminamos los signos de puntuación al principio de las palabra
        while palabra.startswith(puntuacion):
            palabra = palabra[1:]
        # Si la palabra no ha sido añadida, la añadimos
        if palabras.get(palabra) is None:
            palabras[palabra] = 1
        # Si ya existe en nuestro diccionario, añadimos + 1 a su valor
        else:
            palabras[palabra] += 1
    # Devolvemos el diccionario ordenado según el número de repeticiones
    return {k: v for k, v in sorted(palabras.items(), key=lambda item: item[1], reverse=True)}

def mostrar_resultados(lenguajes):
    """Crea un html con el resultado del estudio dentro de una tabla"""

    # Creamos el texto que contendrá el documento HTML
    titulo ="Comparando lenguajes"
    resultado = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{titulo}</title>
    </head>
    <body>
        <h1>{titulo}</h1>
        <p>Vamos a ver el número de palabras que comparten los distingos
        lenguajes buscando en diversas fuentes. No hablamos de su sintaxis,
        sino de las palabras usadas en dichas fuentes.</p>
        <table border="1" width="40%">
            <thead>
                <tr>
                    <th>Lenguajes</th>
    """
    # Rellenamos los encabezados de la lista
    for lenguaje in lenguajes:
        resultado = "\n".join([resultado, f"""<th>{lenguaje["lenguaje"].capitalize()}</th>"""])
    
    # Cerramos la fila de encabezados y abrimos la del cuerpo de la tabla.
    resultado = "".join([resultado, """
        </tr>
        </thead>
        <tbody>
        """])

    # Para cada lenguaje creamos una fila con las comparaciones.
    for lenguaje in lenguajes:
        nombre1 = lenguaje["lenguaje"]
        palabras1 = lenguaje["palabras"]
        resultado = "\n".join([resultado, f"<tr><td>{nombre1.capitalize()}</td>"])
        
        for lenguaje in lenguajes:
            if lenguaje["lenguaje"] == nombre1:
                resultado = "\n".join([resultado, "<td>NC</td>"])
                continue
            nombre2 = lenguaje["lenguaje"]
            palabras2 = lenguaje["palabras"]
            
            comparten = len(palabras1.intersection(palabras2))
            resultado = "\n".join([resultado, f"<td>{comparten}</td>"])
        
        resultado = "\n".join([resultado, "</tr>"])
    resultado = "\n".join([resultado, """
    </tbody>
    </table>
    </body>
    </html>"""])

    # Creamos el documento HTML, escribimos en él y lo cerramos.
    html = open("./data/resultado.html", "w", encoding="utf8")
    html.write(resultado)
    html.close()


if __name__ == "__main__":
    xml = "./data/webs_lenguajes.xml"
    try:
        datos = obtener_datos(xml)
        palabras_por_lenguaje = []
        for lenguaje, contenido in datos.items():
            leng_palabras = {}
            leng_palabras["lenguaje"] = lenguaje
            leng_palabras["palabras"] = limpiar_datos(contar_palabras(contenido))
            palabras_por_lenguaje.append(leng_palabras)

        mostrar_resultados(palabras_por_lenguaje)
        print("El archivo con el resultado ha sido creado con éxito.")
    except FileNotFoundError as fnfe:
        print("No existe el archivo xml indicado")
    except ValueError as ve:
        print(ve)

