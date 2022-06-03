from bs4 import BeautifulSoup

#Requerido para GET
from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from get_functions import *

#Requerido para enviarcorreo
#from sendmail import *
import datetime
from time import strftime
from datetime import datetime
from datetime import date


class CargosManager(): 

    def simple_get(url):
        """
        Attempts to get the content at `url` by making an HTTP GET request.
        If the content-type of response is some kind of HTML/XML, return the
        text content, otherwise return None.
        """
        try:
            with closing(get(url, stream=True)) as resp:
                if is_good_response(resp):
                    return resp.content
                else:
                    return None

        except RequestException as e:
            log_error('Error during requests to {0} : {1}'.format(url, str(e)))
            return None


    def is_good_response(resp):
        """
        Returns True if the response seems to be HTML, False otherwise.
        """
        content_type = resp.headers['Content-Type'].lower()
        return (resp.status_code == 200 
                and content_type is not None 
                and content_type.find('html') > -1)


    def log_error(e):
        """
        It is always a good idea to log errors. 
        This function just prints them, but you can
        make it do anything.
        """
        print(e)


    #--------------------------------------------
    # Lee la tabla de Cargos desde HTML y 
    # la convierte a una lista de diccionarios
    #--------------------------------------------
    def extraerCargos(html):
        global titulo
        cargos = []

        tablaCargos = html.select('table.table-bordered')
        tabla = tablaCargos[0]
        #print(tabla)

        filasCargos = tabla.findChildren('tr')


        for fila in filasCargos:

            tds = fila.findChildren('td')
            #print(tds)
            if len(tds) == 0:
                continue
            
            if len(tds) > 1:
                cargo = {}
                cargo_id = tds[0].text
                cargo_cierre_inscripcion = tds[1].text
                cargo_nivel = tds[2].text
                cargo_establecimiento = tds[3].text
                cargo_email = tds[4].text
                cargo_distrito = tds[5].text
                cargo_localidad = tds[6].text
                cargo_esc_cabecera = tds[7].text
                cargo_sit_rev = tds[8].text
                cargo_cant_hs = tds[9].text
                cargo_asignatura = tds[10].text
                cargo_grado = tds[11].text
                cargo_division = tds[12].text
                cargo_turno = tds[13].text
                cargo_secuencia = tds[14].text        

                cargo['id'] = cargo_id 
                cargo['cierre_inscripcion'] = cargo_cierre_inscripcion
                cargo['nivel'] = cargo_nivel
                cargo['establecimiento'] = cargo_establecimiento
                cargo['email'] = cargo_email
                cargo['distrito'] = cargo_distrito
                cargo['localidad'] = cargo_localidad
                cargo['esc_cabecera'] = cargo_esc_cabecera
                cargo['situacion_revista'] = cargo_sit_rev 
                cargo['cantidad_horas'] = cargo_cant_hs
                cargo['asignatura'] = cargo_asignatura
                cargo['grado'] = cargo_grado 
                cargo['division'] = cargo_division 
                cargo['turno'] = cargo_turno 
                cargo['secuencia'] = cargo_secuencia 
                
                cargos.append(cargo)
            
        return cargos

    #--------------------------------------------
    # Imprimie por pantalla los cargos
    # desde una lista de diccionarios
    #--------------------------------------------

    def imprimir_cargos(cargos):
        #print("ID   " + " "+ "CARGO   " + " " + "H" + " \t" + "D" + " \t" + "NIVEL        " + " " + "Establecimiento" + " \t\t\t" + "Asignatura/Cargo")
        i = 0
        for cargo in cargos:
            i+=1

        
            nivel_str = cargo['nivel'] + "         "
            nivel_str = nivel_str[:12]

            establecimiento_str = cargo['establecimiento'][:15] + "..." + cargo['establecimiento'][-15:]

            todo = str(i) + " " + cargo['id'] + " " + cargo['cantidad_horas'] + " \t" + cargo['distrito'] + " \t" + nivel_str + "  " + establecimiento_str + " \t"  + cargo['situacion_revista'] + "    " + cargo['asignatura']
            print(todo)	
        


    ##VER
    def get_cargos_str(cargos):
    #    print("get_cargos_str:")
        
        cargos_str = ""
        for cargo in cargos:
            if print_resumen:
                localidad_res = cargo['localidad'] + '               '
                modalidad_res = cargo['modalidad'] + '           '
                nombre_res = cargo['nombre']
                encabezado = cargo['numero']  + "\t\t" +  localidad_res[:10] + "\t\t" + modalidad_res[:9] + "\t\t" + nombre_res
                cargos_str+="\r\n"
                cargos_str+=encabezado
                #print(encabezado)
        return cargos_str


    #--------------------------------------------
    # Filtra una lista de diccionarios. Devuelve la lista filtrada
    # Recibe: - Lista de cargos, 
    #         - el nombre de campo filtro + valores
    #--------------------------------------------
    def filtrar_x_campo(cargos, campo, valores):
        filtrado = []
        for valor in valores:
            for cargo in cargos:
                if valor in cargo[campo]:
                    filtrado.append(cargo)
        return filtrado

    ##VER
    def preparar_correo(cargos_a_enviar, url, filtros_str):
    #    print("preparar_correo")
        mensaje = "" + url + "\n"
        fecha = datetime.datetime.now().strftime('%d-%m-%Y')
        asunto = titulo[:23] + "... - " + str(len(cargos_a_enviar)) + " cargos - " + fecha + " - " + filtros_str
        mensaje+=get_cargos_str(cargos_a_enviar)
        #enviar_correo(asunto,get_cargos_str(cargos).encode('utf-8').strip())
        enviar_correo(asunto,mensaje)


    #def procesar_fuente(raw_html, url, filtros):

    # Procesa una asamblea especifica y recorre las paginas
    # Devuelve todos los cargos
    def procesar_fuente(url_fuente):#, url, filtros):
        
        raw_html = simple_get(url_fuente)
        #print(url_fuente)

        html = BeautifulSoup(raw_html, 'html.parser')
        

        li_pagination = html.select('ul.pagination li')

        if li_pagination:
            cant_paginas = len(li_pagination) - 2
        else:
            cant_paginas = -2
        
        cargos_all = []

        if cant_paginas == -2:
            cant_paginas =1 
        #print(f'{cant_paginas} paginas')
        print(f' \t     {cant_paginas}   ', end = '')


        for x in range(1, cant_paginas+1): 
            #print(x)

            fuente_page = url_fuente + f'page={x}&'
            #print(fuente_page)

            raw_html = simple_get(fuente_page)
            html = BeautifulSoup(raw_html, 'html.parser')

            cargos = extraerCargos(html)
            cargos_all += cargos

        #print(f'Total cargos: {len(cargos_all)}')
        print(f' \t {len(cargos_all)} ', end='')
        #imprimir_cargos(cargos_all)

        return(cargos_all)

        
        #imprimir_cargos(get_cargos_filtrados(cargos))

    # Obtiene llamados vigentes de la lista de llamados
    def get_llamados_vigentes(self, fuente):
        raw_html = simple_get(fuente)

        html = BeautifulSoup(raw_html, 'html.parser')
        #Obtengo el primer llamado de la lista de llamados
        opciones_select = html.find("select", {"id": "viewlistadosearch-llamado_id"}).select("option")

        print("LLAMADOS TODOS")

        llamados_list = []
        for opcion in opciones_select:
            #print(opcion)
            llamado_txt = opcion.text
            #print(llamado_txt)
            if "Seleccione" in llamado_txt:
                continue 
            fecha_ini = llamado_txt.split(":")[1].split(" ")[0]
            fecha_fin = llamado_txt.split(":")[2].split(" ")[0]
            nivel = llamado_txt.split(":")[3]
            id_llamado = opcion['value']
            #print(id_llamado)


            llamado = {}
            llamado['id'] = id_llamado
            llamado['fecha_inicio'] = fecha_ini
            llamado['fecha_fin'] = fecha_fin
            llamado['texto'] = opcion.text
            llamado['nivel'] = nivel

            llamados_list.append(llamado)

        #print ("END FOR")

        #print(llamados_list)

        # dd/mm/YY
        today = date.today()

        hoy = today.strftime("%d-%m-%Y")
        #print("Hoy =", hoy)
        # Filtra llamados vigentes
        hoy = datetime.strptime(hoy, '%d-%m-%Y')
        llamados_vigentes = []
        for llamado in llamados_list:
        
            #asamblea['fecha_fin'] = '05-05-2022' # Prueba fecha fija

            # Date Cast
            llamado['fecha_fin'] = datetime.strptime(llamado['fecha_fin'], '%d-%m-%Y')
            llamado['fecha_inicio'] = datetime.strptime(llamado['fecha_inicio'], '%d-%m-%Y')

            if  llamado['fecha_inicio'] <= hoy and llamado['fecha_fin'] >= hoy:
                #print("LLAMADO VIGENTE")
                llamados_vigentes.append(llamado)

        #print("LLAMADOS VIGENTES")
        #for llamado_vigente in llamados_vigentes:
        #    print(llamado_vigente)

        return llamados_vigentes



    # Obtiene el primer llamado de la lista de llamados. El primer llamado es el más reciente
    def get_llamado_reciente(fuente):

        raw_html = simple_get(fuente)

        html = BeautifulSoup(raw_html, 'html.parser')
        #Obtengo el primer llamado de la lista de llamados
        llamados_select = html.find("select", {"id": "viewlistadosearch-llamado_id"}).select("option")[1]

        print(llamados_select.text)
        llamado_txt = llamados_select.text
        fecha_ini = llamado_txt.split(":")[1].split(" ")[0]
        fecha_fin = llamado_txt.split(":")[2].split(" ")[0]
        nivel = llamado_txt.split(":")[3]
        id_llamado_mayor = llamados_select['value']

        #print(fecha_ini)
        #print(fecha_fin)
        #print(nivel)


        llamado = {}
        llamado['id'] = id_llamado_mayor
        llamado['fecha_inicio'] = fecha_ini
        llamado['fecha_fin'] = fecha_fin
        llamado['texto'] = llamados_select.text
        llamado['nivel'] = nivel

        #print(llamado)


        print(type(llamado))
        
        return llamado

    # Para un tipo de llamado, busca el ultimo llamado
    # arma los filtros por nivel y distrito y llama a procesar_fuente
    # imprime el resultado
    def procesar_llamado(url_tipo_llamado):

        fuente = url_tipo_llamado + '?tipo=1'

        # procesa SOLO el llamado más reciente de la lista
        id_llamado = get_llamado_reciente(url_tipo_llamado)['id']
        
        #POC para todos los llamados
        llamados_vigentes = get_llamados_vigentes(url_tipo_llamado)
        #print("END TODOS LOS LLAMADOS")



        #niveles: 2: MEDIA 3:SUPERIOR 4:ADULTOS 6:TECNICA 7:ARTISTICA
        niveles = ['3','4', '6', '7'] #
        distritos = ['1', '8', '6']

        # valores filtro cargos
        valores_filtro = ['RESID', 'ATENE', 'TEA','Tea', 'CORP','Corp', 'ARTE','Arte', 
        'ARTI','Arti', 'ARTÍ','Artí', 'ACTO','Acto', 'JUE','Jue', 'CULT','Cult', 
        'VOZ', 'Voz', 'VOCAL', 'Vocal', 'DOCENTE', 'Docente', 'AMB', 'Amb']


        #fuente_llamado = fuente + f'&ViewlistadoSearch%5Bllamado_id%5D={id_llamado}'

        print(f'Nivel | Distrito | Paginas | Cargos | Filtrados')

        for llamado_vigente in llamados_vigentes:

            fuente_llamado = fuente + f'&ViewlistadoSearch%5Bllamado_id%5D={llamado_vigente["id"]}'
            print(llamado_vigente['texto'])
            for nivel in niveles:
                
                for distrito in distritos:

                    #print(f'Nivel: {nivel} Distrito: {distrito}')
                    print(f'  {nivel} \t    {distrito}', end='')

                    fuente_llamado_distrito = fuente_llamado + f'&ViewlistadoSearch%5Bdistrito%5D={distrito}'
                    fuente_llamado_distrito_nivel = fuente_llamado_distrito + f'&ViewlistadoSearch%5Bnivel%5D={nivel}'
                    fuente_llamado_distrito_nivel += '&'
                    #print(fuente_llamado_distrito_nivel)
                    #continue
                    cargos_all = procesar_fuente(fuente_llamado_distrito_nivel)


                    # Filtro nombre cargos
                    cargos_filtrados = filtrar_x_campo(cargos_all, 'asignatura', valores_filtro)

                    if len(cargos_filtrados) > 0:
                        print(f' \t {len(cargos_filtrados)}')
                        imprimir_cargos(cargos_filtrados)
                        #print(f'Cargos filtrados: {len(cargos_filtrados)}')

                    if len(cargos_all) > 0:
                        print("")
                        print(fuente_llamado_distrito_nivel)

                print("")




tipos_llamados = ['https://coberturas.neuquen.edu.ar/asambleas/frontend/web/index.php/vacante/listado',
'https://coberturas.neuquen.edu.ar/asambleas/frontend/web/index.php/vacante/listado24hs',
'https://coberturas.neuquen.edu.ar/asambleas/frontend/web/index.php/vacante/listadopublico',
'https://coberturas.neuquen.edu.ar/asambleas/frontend/web/index.php/vacante/listadoedi',
'https://coberturas.neuquen.edu.ar/asambleas/frontend/web/index.php/vacante/listadoedi24hs']

cargos = CargosManager()

tipos_llamados_vigentes = []
for tipo_llamado in tipos_llamados:
    vigentes = cargos.get_llamados_vigentes(tipo_llamado)
    
    if len(vigentes) > 0:
        print ("hay vigentes")
        tipos_llamados_vigentes.append(tipo_llamado)

    for v in vigentes:
        
        print(v['texto'] )

print("FIN VIGENTES")

# # dd/mm/YY
# today = date.today()

# hoy = today.strftime("%d-%m-%Y")
# print("Hoy =", hoy)


# # Entra a cada tipo de llamado 
# # y encuentra los que tengan un llamado vigente
# hoy = datetime.strptime(hoy, '%d-%m-%Y')
# #tipos_llamados_vigentes = []
# for tipo_llamado in tipos_llamados:
#     break
#     asamblea = get_llamado_reciente(tipo_llamado)


    
#     #asamblea['fecha_fin'] = '05-05-2022' # Prueba fecha fija

#     # Date Cast
#     asamblea['fecha_fin'] = datetime.strptime(asamblea['fecha_fin'], '%d-%m-%Y')
#     asamblea['fecha_inicio'] = datetime.strptime(asamblea['fecha_inicio'], '%d-%m-%Y')

#     if  asamblea['fecha_inicio'] <= hoy and asamblea['fecha_fin'] >= hoy:
#         print("VIGENTE")
#         tipos_llamados_vigentes.append(tipo_llamado)

# #print(tipos_llamados_vigentes)

# Procesa los tipos de llamados 
for llamado in tipos_llamados_vigentes:
    print("")
    cargos.procesar_llamado(llamado)



#llamado_normal = 'https://coberturas.neuquen.edu.ar/asambleas/frontend/web/index.php/vacante/listado'
#procesar_llamado(llamado_normal)

#llamado_24hs = 'https://coberturas.neuquen.edu.ar/asambleas/frontend/web/index.php/vacante/listado24hs'
#procesar_llamado(llamado_24hs)

#llamado_publico = 'https://coberturas.neuquen.edu.ar/asambleas/frontend/web/index.php/vacante/listadopublico'
#procesar_llamado(llamado_publico)

#llamado_edi ='https://coberturas.neuquen.edu.ar/asambleas/frontend/web/index.php/vacante/listadoedi'
#procesar_llamado(llamado_edi)

#llamado_edi_24hs = 'https://coberturas.neuquen.edu.ar/asambleas/frontend/web/index.php/vacante/listadoedi24hs'
#procesar_llamado(llamado_edi_24hs)



