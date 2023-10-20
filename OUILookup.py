import subprocess
import getopt
import sys
#leer manuf.txt 
def leer_base_datos():
    with open("manuf.txt", 'r', encoding='utf-8') as archivo_entrada:
        lineas = [linea.strip() for linea in archivo_entrada.readlines() if linea.strip()]
    dic = {}
    for linea in lineas:
        if not linea.startswith("#"):
            escribir = linea.split()
            escribir = [elemento for elemento in escribir if elemento != '#'] 
            if(len(escribir) >2):
                partes2 = escribir[2:]
                dic[escribir[0]] = " ".join(partes2)
            elif(len(escribir) == 2):
                dic[escribir[0]] = escribir[1]
            else:
                print((escribir))
    return dic

# Función para obtener los datos de fabricación de una tarjeta de red por IP
def obtener_datos_por_ip(ip):
    diccionario_arp = obtener_tabla_arp() 
    ip_rango = ip.split(".")
    ip_rango_bool = "192" == ip_rango[0] and "168" == ip_rango[1] and "1" == ip_rango[2]
    if(ip_rango_bool):
        if(ip in diccionario_arp):
            mac = diccionario_arp[ip]
            cortado = mac.split(":")
            cortado = cortado[:3]
            cortado = ":".join(cortado)
            if(cortado in diccionario_mac):
                print(f"MAC Address : {mac}\nFabricante : {diccionario_mac[cortado]}")
            else:
                print(f"MAC Address : {mac}\nFabricante : Not found")
        else:
            print(f"Error: Not found in arp table")
    else:
        print(f"Error: ip is outside the host network")

# Función para obtener los datos de fabricación de una tarjeta de red por MAC

def obtener_datos_por_mac(mac):
    mac2 = mac.upper()
    mac2 = mac2.replace("-", ":")
    cortado = mac2.split(":")
    cortado = cortado[:3]
    cortado = ":".join(cortado)
    if(cortado in diccionario_mac):
        return mac2,diccionario_mac[cortado]
    else:
        return mac2,"Not found"

# Función para obtener la tabla ARP
def obtener_tabla_arp():
    dicc = {}
    try:
        tabla_arp = subprocess.check_output(['arp', '-a'], universal_newlines=True)
        arp_itt = tabla_arp.split('\n')
        for line in arp_itt:
            if 'Internet Address' in line or 'Interfaz' in line or 'Direcci¢n' in line or 'Direccion' in line or 'Interface' in line:  # Ignorar las 2 primeras líneas
                continue
            if line.strip():
                parts = line.split()
                if len(parts) >= 2:
                    cortado = parts[1]
                    cortado = cortado.split("-")
                    cortado = ":".join(cortado)
                    cortado = cortado.upper()
                    dicc[parts[0]] = cortado
        return dicc
    except subprocess.CalledProcessError as e:
        print(f"Error al obtener la tabla ARP: {e}")
        return None
    except Exception as e:
        print(f"Error inesperado: {e}")
        return None 

def main(argv):
    #Inicializar variables
    ayuda = """
Use: ./OUILookup --ip <IP> | --mac <IP> | --arp | [--help]
--ip : IP del host a consultar.
--mac: MAC a consultar. P.e. aa:bb:cc:00:00:00.
--arp: muestra los fabricantes de los host disponibles en la tabla arp.
--help: muestra este mensaje y termina.
"""
    #diccionario_arp = leer_tabla_arp()
    diccionario_mac = leer_base_datos()
    #ver si se ejecuta sin argumentos
    if len(argv) == 0:
        print(ayuda)
        sys.exit()
    #leer --argumentos
    try:
        opts, args = getopt.getopt(argv, "i:m:ah", ["ip=", "mac=","arp","help"])
    except getopt.GetoptError:
        print(ayuda)
        sys.exit(2)
    #iniciar lectura de argumentos
    for opt, arg in opts:
        #ejecutar comando --help
        if opt == '--help':
            print(ayuda)
            sys.exit()
        #Comando --ip
        elif opt in ("-i", "--ip"):
            if arg == '':
                print("La opción -i/--input no puede estar vacía.")
                sys.exit(2)
            obtener_datos_por_ip(arg)
        #Comando --mac
        elif opt in ("-m", "--mac"):
            if arg == '':
                print("La opción -o/--output no puede estar vacía.")
                sys.exit(2)
            mac,vendor = obtener_datos_por_mac(arg)
            print(f"MAC Address : {mac}\nFabricante : {vendor}")
        #Comando --arp
        elif opt in ("-a", "--arp"):
            diccionario_arp = obtener_tabla_arp()
            #diccionario_arp["192.168.1.500"] = "00:00:13:12:12:12"
            print("IP\t/\tMAC\t/\t/Vendor")
            for ip in diccionario_arp:
                mac,vendor = obtener_datos_por_mac(diccionario_arp[ip])
                print(f"{ip}\t {diccionario_arp[ip]}, {vendor}")
        
#INICIALIZAR BASE DE DATOS COMO VARIABLE GLOBAL 
diccionario_mac = leer_base_datos()
#
if __name__ == "__main__":
    main(sys.argv[1:])
 