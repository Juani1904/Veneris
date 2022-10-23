from xmlrpc.server import SimpleXMLRPCServer
# El modulo xmlrpc.server y la clase SimpleXMLRPCServer me permiten establecer un servidor con protocolo XMLRPC
from threading import Thread
# Con este modulo y Thread podemos instanciar un objeto Thread o hilo que es el que va a mantener la ejecucion del sv y comunicaciones
# Basicamente es el que va a estar bloqueandose o esperando (en estado de escucha) a que un objeto se conecte
import socket
# El socket me va a permitir establecer el cinculo entre la aplicacion cliente (C++) y la aplicacion servidora (Python)

# La clase que vamos a definir ahora hace de interfaz entre el cliente y el servicio (en nuestro caso cliente y framework de Arduino)


class Servidor(object):
    server = None
    """
    Como servidor no se ha especificado a ninguno en particular, porque en el lanzamiento (instanciacion
    de self.server) le pasaremos todo
    """
    puerto = 8891  # Definimos un puerto. Puede ser cualquiera, simpre y cuando este libre en el host

    # Definimos el constructor
    def __init__(self, miRobot, puerto):
        # Con self.objeto_vinculado establecemnos la relacion entre la interfaz y el servicio. En este caso el framework de Arduino
        self.Robot = miRobot
        self.puerto_usado = puerto
        while True:
            try:
                """Creacion del servidor indicando el puerto deseado. Es importante esta instanciacion
                del objeto self.server, debido a que es la que me crea el vinculo entre mi clase
                interfaz XmlRpcEjemploserver con el servidor propiamente dicho (clase servidor SimpleXMLRPCServer)
                """
                self.server = SimpleXMLRPCServer(("localhost", self.puerto_usado), allow_none=True)
                if self.puerto_usado != puerto:
                    print(
                        "Servidor RPC ubicado en puerto no estandar [%d]" % self.puerto_usado)
                break

            except socket.error as e:

                if e.errno == 98:
                    self.puerto_usado += 1
                    continue
                else:
                    print("El servidor RPC no puede ser iniciado")
                    raise

        """# Se registra cada funcion que realiza el servicio (robot)
        # Los nombres que pongamos entre "" son con los que voy a tener que llamar a la funcion en mi
        codigo cliente. Pueden diferir estos a como estan referenciados en "rpc_objetos.py"
        # Luego los nombres do_saludar y do_calcular vienen de los metodos que vamos a definir mas
        abajo, junto con run_server y shutdown
        """
        #Cuando alguien en el cliente llame a la funcion saludar1, en el servidor se ejecutara el 
        # metodo do_saludar, lo mismo para do_calcular
        self.server.register_function(self.do_saludar, "saludar1")
        self.server.register_function(self.do_calcular, "calcular1")
        
        # Se lanza el servidor en un hilo de control mediante Thread

        """*target* is the callable object to be invoked by the run()
        method. Defaults to None, meaning nothing is called. En este caso el run method
        sera run_server y lo creamos a continuacion de esto"""

        self.thread = Thread(target=self.run_server) #Instanciamos el objeto thead

        self.thread.start() #Utilizamos atributo start() del objeto thread

        print("Servidor RPC iniciado en el puerto [%s]" % str(
            self.server.server_address))

    #Ahora definimos algunos otros metodos que tendra mi clase XmlEjemploServer

    #Metodo para iniciar el servidor
    def run_server(self):
        
        self.server.serve_forever()

    #Metodo para cerrar el servidor
    def shutdown(self):
        
        self.server.shutdown()
        self.thread.join()

    #Metodo para calcular.
    def do_calcular(self, prim=2, seg=5):
        # Funcion/servicio: sumar 2 numeros
        return self.Robot.calcular(prim, seg)
    """El cliente envia la peticion de llamar a la funcion calcular1 al servidor. Luego el servidor
    internamente llama a la funcion do_calcular. Luego vemos que esta funcion o metodo do_calcular
    retorna el metodo calcular() del objetoX."""

    #Metodo para saludar
    def do_saludar(self, quien='Programador'):
        # Funcion/servicio: mensaje al argumento provisto
        return self.Robot.saludar(quien)