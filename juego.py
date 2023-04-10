import pilasengine
import random
pilas = pilasengine.iniciar()

MENSAJE_AYUDA = """
En Space Atack, controlas una nave 
utilizando el teclado.El objetivo del
juego es disparar a los asteroides
y ovnis evitando que golpeen tu nave.
Para disparar debes que usar la
barra espaciadora y para mover la 
nave debes usar las flechas del teclado.
"""


class Estado:
	def actualizar(self):
		pass

class Iniciando(Estado):
	def __init__(self,juego,nivel):
		self.texto = pilas.actores.Texto("Iniciando el nivel %d" %(nivel))
		self.nivel = nivel
		self.texto.color = pilas.colores.blanco
		self.contador_de_segundos = 0
		self.juego = juego
		pilas.tareas.agregar(1,self.actualizar)
	
	def actualizar(self):
		self.contador_de_segundos += 1
		if self.contador_de_segundos > 2:
			self.juego.cambiar_estado(Jugando(self.juego,self.nivel))
			self.texto.eliminar()
			return False
		return True
				
class Jugando(Estado):
	def __init__(self,juego,nivel):
		self.nivel = nivel
		self.juego = juego
		self.juego.crear_piedras(cantidad=nivel*3)
		pilas.tareas.agregar(1,self.actualizar)
	def actualizar(self):
		if self.juego.ha_eliminado_todas_las_piedras():
			self.juego.cambiar_estado(Iniciando(self.juego,self.nivel+1))
			return False
		return True

class PierdeVida(Estado):
	def __init__(self,juego):
		self.contador_de_segundos = 0
		self.juego = juego
		if self.juego.contador_de_vidas.le_quedan_vidas():
			self.juego.contador_de_vidas.quitar_una_vida()
			pilas.tareas.agregar(1,self.actualizar)
		else:
			juego.cambiar_estado(PierdeTodoElJuego(juego))
	def actualizar(self):
		self.contador_de_segundos += 1
		if self.contador_de_segundos > 2:
			self.juego.crear_nave()
			return False
		return True
		
class PierdeTodoElJuego(Estado):
	def __init__(self,juego):
		self.juego = juego
		self.mensaje = pilas.actores.Texto("Lo siento, has perdido!")
		self.mensaje.color = pilas.colores.blanco
		self.mensaje.abajo = 240
		self.mensaje.abajo = [-20]
		pilas.tareas.agregar(2,self.actualizar)
	def actualizar(self):
		self.mensaje.eliminar()
		pregunta = pilas.actores.Texto("Reintentar?")
		pregunta.color = pilas.colores.blanco
		pregunta.abajo = 300
		pregunta.abajo = [20]
		opciones_gameover = [("Si",self.juego.volver_a_jugar),("No",self.juego.volver_al_menu_principal)]
		self.menu = pilas.actores.Menu(opciones_gameover, y = -50)
		


class ContadorDeVidas:
	
	def __init__(self,cantidad_de_vidas):
		self.crear_texto()
		self.cantidad_de_vidas = cantidad_de_vidas
		self.vidas = [pilas.actores.Actor(imagen="data/vida.png")for x in range(cantidad_de_vidas)]
		for indice,vida in enumerate(self.vidas):
			vida.x = -220+indice*30
			vida.arriba = 230
	
	def crear_texto(self):
		"Genera el texto que dice 'vidas'"
		self.texto = pilas.actores.Texto("Vidas:")
		self.texto.color = pilas.colores.blanco
		self.texto.magnitud = 20
		self.texto.izquierda = -310
		self.texto.arriba = 220
		
	
	def le_quedan_vidas(self):
		return self.cantidad_de_vidas > 0
	
	def quitar_una_vida(self):
		self.cantidad_de_vidas -= 1
		vida = self.vidas.pop()
		vida.eliminar()



class Ayuda(pilasengine.escenas.Escena):
	"Es la escena que da instrucciones de como jugar."
	def iniciar(self):
		pilas.fondos.Fondo("DATA/ayuda.png")
		self.crear_texto_ayuda()
		self.pulsa_tecla_escape.conectar(self.cuando_pulsa_tecla)
    
	def crear_texto_ayuda(self):
		pilas.actores.Texto("Ayuda",y = 200)
		pilas.actores.Texto(MENSAJE_AYUDA, y = 0)
		pilas.avisar("Pulsa ESC para recresar")
        
	def cuando_pulsa_tecla(self, *k, **kw):
		pilas.escenas.MenuPrincipal()

class Jugar(pilasengine.escenas.Escena):
	
	def iniciar(self):
		pilas.fondos.Espacio()
		self.piedras_grandes = pilas.actores.Grupo()
		self.piedras_medias = pilas.actores.Grupo()
		self.piedras_chicas = pilas.actores.Grupo()
		self.crear_nave()
		self.crear_contador_de_vidas()
		self.cambiar_estado(Iniciando(self,1))
		self.puntaje = pilas.actores.Puntaje(x=240,y=220,color=pilas.colores.blanco)
		pilas.avisar(u"Pulsa ESC para volver al Menu Principal.")
		self.pulsa_tecla_escape.conectar(self.volver_al_menu_principal)
	
	def cambiar_estado(self,estado):
		self.estado = estado
		
	def crear_nave(self):
		nave = pilas.actores.NaveRoja()
		nave.demora_entre_disparos = 25
		nave.aprender(pilas.habilidades.LimitadoABordesDePantalla)
		
		pilas.colisiones.agregar(nave.disparos,self.piedras_grandes, self.cuando_explota_asteroide_grande)
		pilas.colisiones.agregar(nave.disparos,self.piedras_medias, self.cuando_explota_asteroide_medio)
		pilas.colisiones.agregar(nave.disparos,self.piedras_chicas, self.cuando_explota_asteroide_chico)
		
		pilas.colisiones.agregar(nave,self.piedras_grandes, self.explotar_y_terminar)
		pilas.colisiones.agregar(nave,self.piedras_medias, self.explotar_y_terminar)
		pilas.colisiones.agregar(nave,self.piedras_chicas, self.explotar_y_terminar)
		
		nave.y = -200
		nave.escala = 0.5

	def crear_piedras(self,cantidad):
		fuera_de_la_pantalla = [-600,-650,-700,-750,-800]
		tamanos = ["grande","media","chica"]
		velocidades = [-10,-9,-8,-7,-6,-5,-4,-3,-2,2,3,4,5,6,7,8,9,10]
			
		for x in range(cantidad):
			x = random.choice(fuera_de_la_pantalla)
			y = random.choice(fuera_de_la_pantalla)
			dx = random.choice(velocidades)/10.0
			dy = random.choice(velocidades)/10.0
			t = random.choice(tamanos)
			
			self.rocas = pilas.actores.Piedra(x,y)
			self.rocas.aprender(pilas.habilidades.PuedeExplotarConHumo)
			self.rocas.definir_tamano(t)
			self.rocas.empujar(dx,dy)
			
			if t == "grande":
				self.piedras_grandes.agregar(self.rocas)
			elif t == "media":
				self.piedras_medias.agregar(self.rocas)
			else:
				self.piedras_chicas.agregar(self.rocas)
	
			
	def cuando_explota_asteroide_grande(self,disparos,piedra):
		self.x = piedra.x
		self.y = piedra.y
		velocidades = range(-10,2)+range(2,10)
		self.puntaje.aumentar(50)
		self.puntaje.escala = 2
		self.puntaje.escala = [1], 0.2
		self.puntaje.rotacion = random.randint(30, 60)
		self.puntaje.rotacion = [0], 0.2
		disparos.eliminar()
		piedra.eliminar()
		pilas.actores.ExplosionDeHumo(self.x,self.y)
		for x in range(2):
			dx = random.choice(velocidades)/10.0
			dy = random.choice(velocidades)/10.0
			self.rocas = pilas.actores.Piedra(self.x,self.y)
			self.rocas.definir_tamano("media")
			self.rocas.empujar(dx,dy)
			self.piedras_medias.agregar(self.rocas)
	
	def cuando_explota_asteroide_medio(self,disparos,piedra):
		self.x = piedra.x
		self.y = piedra.y
		velocidades = range(-10,2)+range(2,10)
		self.puntaje.aumentar(25)
		self.puntaje.escala = 2
		self.puntaje.escala = [1], 0.2
		self.puntaje.rotacion = random.randint(30, 60)
		self.puntaje.rotacion = [0], 0.2
		disparos.eliminar()
		piedra.eliminar()
		pilas.actores.ExplosionDeHumo(self.x,self.y)
		for x in range(2):
			dx = random.choice(velocidades)/10.0
			dy = random.choice(velocidades)/10.0
			self.rocas = pilas.actores.Piedra(self.x,self.y)
			self.rocas.definir_tamano("chica")
			self.rocas.empujar(dx,dy)
			self.piedras_chicas.agregar(self.rocas)
	
	def cuando_explota_asteroide_chico(self,disparos,piedra):
		self.x = piedra.x
		self.y = piedra.y
		self.puntaje.aumentar(5)
		self.puntaje.escala = 2
		self.puntaje.escala = [1], 0.2
		self.puntaje.rotacion = random.randint(30, 60)
		self.puntaje.rotacion = [0], 0.2
		disparos.eliminar()
		piedra.eliminar()
		pilas.actores.ExplosionDeHumo(self.x,self.y)
	
	
	def crear_contador_de_vidas(self):
		self.contador_de_vidas = ContadorDeVidas(3)

			
	def explotar_y_terminar(self,nave,piedra):
		"Responde a la colision entre la nave y una piedra."
		nave.eliminar()
		self.cambiar_estado(PierdeVida(self))


	def ha_eliminado_todas_las_piedras(self):
		return len(self.piedras_grandes) == 0 and len(self.piedras_medias) == 0 and len(self.piedras_chicas) == 0

	def volver_al_menu_principal(self, *k, **kw):
		pilas.escenas.MenuPrincipal()
	
	def volver_a_jugar(self, *k, **kw):
		pilas.escenas.Jugar()
	
class MenuPrincipal(pilasengine.escenas.Escena):
	
	def iniciar(self):
		pilas.fondos.Fondo("DATA/menu.png")
		self.crear_titulo_del_juego()
		pilas.avisar(u"Use el teclado para controlar el menu.")
		self.menu_principal()
		self.crear_asteroides()
		
	def crear_titulo_del_juego(self):
		logotipo = pilas.actores.Actor(imagen="Data/titulo1.png")
		logotipo.y = 300
		logotipo.y = [300,100]
		
		logotipo.x = [random.randrange(-10,11),random.randrange(-10,11)]*99,2
		logotipo.y = [random.randrange(90,111),random.randrange(90,111)]*99,2
				

	def comenzar_a_jugar(self):
		pilas.escenas.Jugar()
	
	def menu_ayuda(self):
		pilas.escenas.Ayuda()
    
	def salir_del_juego(self):
		pilas.terminar()

	def menu_principal(self):
		opciones_menu = [("Jugar",self.comenzar_a_jugar),("Ayuda",self.menu_ayuda),("Salir",self.salir_del_juego)]
		self.menu = pilas.actores.Menu(opciones_menu, y = -50)
    
	
		
	def crear_asteroides(self):
		fuera_de_la_pantalla = [-600,-650,-700,-750,-800]
		velocidades = range(-10,2)+range(2,10)
		for x in range(5):
			x = random.choice(fuera_de_la_pantalla)
			y = random.choice(fuera_de_la_pantalla)
			dx = random.choice(velocidades)/10.0
			dy = random.choice(velocidades)/10.0
			
			rocas = pilas.actores.Piedra(x,y)
			rocas.definir_tamano("chica")
			rocas.empujar(dx,dy)
			
			
pilas.escenas.vincular(Ayuda)
pilas.escenas.vincular(Jugar)
pilas.escenas.vincular(MenuPrincipal)
pilas.escenas.MenuPrincipal()        
pilas.ejecutar()
