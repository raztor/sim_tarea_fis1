import pygame
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import math

# Dimensiones de la ventana de simulación
ANCHO_SIMULACION, ALTO_SIMULACION = 800, 400

# Colores
BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)
AZUL = (0, 0, 255)
ROJO = (255, 0, 0)
GRIS = (200, 200, 200)

# Configuración de Pygame
pygame.init()
ventana_simulacion = pygame.Surface((ANCHO_SIMULACION, ALTO_SIMULACION))

# Configuración de la ventana principal (Tkinter)
root = tk.Tk()
root.title("Simulación de Colisiones")

# Variables para los parámetros
masa1 = tk.DoubleVar(value=2.0)
masa2 = tk.DoubleVar(value=3.0)
velocidad1 = tk.DoubleVar(value=5.0)
velocidad2 = tk.DoubleVar(value=-3.0)
tipo_colision = tk.StringVar(value="elastica")  # Valor por defecto: "elastica"
tipo_movimiento = tk.StringVar(value="1D")  # Movimiento 1D o 2D
coef_roce = tk.DoubleVar(value=0.05)  # Coeficiente de roce
gravedad = tk.DoubleVar(value=0)  # Gravedad para movimiento 2D

# Variables para el movimiento en 2D
angulo1 = tk.DoubleVar(value=0.0)  # Ángulo de lanzamiento en grados para auto 1
angulo2 = tk.DoubleVar(value=0.0)  # Ángulo de lanzamiento en grados para auto 2

# Gráficos de energía y momento
fig, axs = plt.subplots(1, 2, figsize=(10, 4))  # Configuración para 1x2 gráficos lado a lado
(ax1, ax2) = axs
ax1.set_title("Energía Cinética")
ax1.set_xlabel("Tiempo")
ax1.set_ylabel("Energía (J)")
ax2.set_title("Momento Lineal")
ax2.set_xlabel("Tiempo")
ax2.set_ylabel("Momento (kg·m/s)")

# Variables para almacenar la energía y momento a lo largo del tiempo
tiempo = []
energia_auto1 = []
energia_auto2 = []
momento_auto1 = []
momento_auto2 = []

# Contadores de rebotes
rebotes_auto1 = 0
rebotes_auto2 = 0

# Variables para almacenar la trayectoria de las partículas
trayectoria_auto1 = []
trayectoria_auto2 = []

# Estado de la simulación
simulacion_activa = False
pausada = False

# Canvas de matplotlib dentro de Tkinter
canvas_fig = FigureCanvasTkAgg(fig, master=root)
canvas_fig.get_tk_widget().grid(row=6, column=0, columnspan=3, pady=10)

# Indicadores de estado
frame_estado = ttk.LabelFrame(root, text="Indicadores de Estado")
frame_estado.grid(row=7, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")

estado_velocidad1 = tk.StringVar(value="Velocidad Auto 1: 0.0 m/s")
estado_velocidad2 = tk.StringVar(value="Velocidad Auto 2: 0.0 m/s")
estado_energia1 = tk.StringVar(value="Energía Auto 1: 0.0 J")
estado_energia2 = tk.StringVar(value="Energía Auto 2: 0.0 J")
estado_rebotes1 = tk.StringVar(value="Rebotes Auto 1: 0")
estado_rebotes2 = tk.StringVar(value="Rebotes Auto 2: 0")

# Etiquetas para los indicadores
ttk.Label(frame_estado, textvariable=estado_velocidad1).grid(row=0, column=0, sticky="w")
ttk.Label(frame_estado, textvariable=estado_velocidad2).grid(row=1, column=0, sticky="w")
ttk.Label(frame_estado, textvariable=estado_energia1).grid(row=0, column=1, sticky="w")
ttk.Label(frame_estado, textvariable=estado_energia2).grid(row=1, column=1, sticky="w")
ttk.Label(frame_estado, textvariable=estado_rebotes1).grid(row=0, column=2, sticky="w")
ttk.Label(frame_estado, textvariable=estado_rebotes2).grid(row=1, column=2, sticky="w")

# Funciones para habilitar o deshabilitar parámetros según el tipo de movimiento
def actualizar_parametros_movimiento():
    if tipo_movimiento.get() == "2D":
        frame_2d_params.grid(row=2, column=0, padx=10, pady=10, columnspan=3)
        angulo1.set(45.0)
        angulo2.set(45.0)
        gravedad.set(0.5)
    else:
        frame_2d_params.grid_forget()
        angulo1.set(0.0)
        angulo2.set(0.0)
        gravedad.set(0.0)

# Función para iniciar la simulación
def iniciar_simulacion():
    global particula1, particula2, tiempo, energia_auto1, energia_auto2, momento_auto1, momento_auto2, rebotes_auto1, rebotes_auto2, trayectoria_auto1, trayectoria_auto2, simulacion_activa, pausada
    particula1 = {"x": 200, "y": ALTO_SIMULACION // 2, "masa": masa1.get(), "velocidad_x": velocidad1.get(),
                  "velocidad_y": 0}
    particula2 = {"x": 600, "y": ALTO_SIMULACION // 2, "masa": masa2.get(), "velocidad_x": velocidad2.get(),
                  "velocidad_y": 0}

    # Resetear datos de gráficos y contadores de rebotes
    tiempo = []
    energia_auto1 = []
    energia_auto2 = []
    momento_auto1 = []
    momento_auto2 = []
    rebotes_auto1 = 0
    rebotes_auto2 = 0
    trayectoria_auto1 = [(particula1["x"], particula1["y"])]
    trayectoria_auto2 = [(particula2["x"], particula2["y"])]
    simulacion_activa = True
    pausada = False

    # Configurar velocidades iniciales si es movimiento 2D
    if tipo_movimiento.get() == "2D":
        angulo_radianes1 = math.radians(angulo1.get())
        angulo_radianes2 = math.radians(angulo2.get())
        particula1["velocidad_x"] = velocidad1.get() * math.cos(angulo_radianes1)
        particula1["velocidad_y"] = -velocidad1.get() * math.sin(angulo_radianes1)
        particula2["velocidad_x"] = velocidad2.get() * math.cos(angulo_radianes2)
        particula2["velocidad_y"] = -velocidad2.get() * math.sin(angulo_radianes2)

    simulacion()

# Función para pausar/reanudar la simulación
def pausar_reanudar_simulacion():
    global pausada
    if simulacion_activa:
        pausada = not pausada

# Función para reiniciar la simulación
def reiniciar_simulacion():
    global simulacion_activa, pausada
    simulacion_activa = False
    pausada = False
    ventana_simulacion.fill(BLANCO)
    canvas_simulacion.delete("all")
    ax1.clear()
    ax2.clear()
    ax1.set_title("Energía Cinética")
    ax1.set_xlabel("Tiempo")
    ax1.set_ylabel("Energía (J)")
    ax2.set_title("Momento Lineal")
    ax2.set_xlabel("Tiempo")
    ax2.set_ylabel("Momento (kg·m/s)")
    canvas_fig.draw()
    estado_velocidad1.set("Velocidad Auto 1: 0.0 m/s")
    estado_velocidad2.set("Velocidad Auto 2: 0.0 m/s")
    estado_energia1.set("Energía Auto 1: 0.0 J")
    estado_energia2.set("Energía Auto 2: 0.0 J")
    estado_rebotes1.set("Rebotes Auto 1: 0")
    estado_rebotes2.set("Rebotes Auto 2: 0")

# Configuración de la sección de parámetros
frame_config = ttk.LabelFrame(root, text="Parámetros")
frame_config.grid(row=0, column=0, padx=10, pady=10, columnspan=2)

# Selección de tipo de movimiento
ttk.Label(frame_config, text="Tipo de movimiento:").grid(row=0, column=0, sticky="w")
ttk.Radiobutton(frame_config, text="1D", variable=tipo_movimiento, value="1D",
                command=actualizar_parametros_movimiento).grid(row=0, column=1, sticky="w")
ttk.Radiobutton(frame_config, text="2D", variable=tipo_movimiento, value="2D",
                command=actualizar_parametros_movimiento).grid(row=1, column=1, sticky="w")

# Parámetros para movimiento en 1D
ttk.Label(frame_config, text="Masa 1 (kg):").grid(row=2, column=0, sticky="w")
ttk.Entry(frame_config, textvariable=masa1).grid(row=2, column=1)

ttk.Label(frame_config, text="Velocidad 1 (m/s):").grid(row=3, column=0, sticky="w")
ttk.Entry(frame_config, textvariable=velocidad1).grid(row=3, column=1)

ttk.Label(frame_config, text="Masa 2 (kg):").grid(row=4, column=0, sticky="w")
ttk.Entry(frame_config, textvariable=masa2).grid(row=4, column=1)

ttk.Label(frame_config, text="Velocidad 2 (m/s):").grid(row=5, column=0, sticky="w")
ttk.Entry(frame_config, textvariable=velocidad2).grid(row=5, column=1)

# Selector de tipo de colisión
ttk.Label(frame_config, text="Tipo de colisión:").grid(row=6, column=0, sticky="w")
tk.Radiobutton(frame_config, text="Elástica", variable=tipo_colision, value="elastica").grid(row=6, column=1,
                                                                                             sticky="w")
tk.Radiobutton(frame_config, text="Inelástica", variable=tipo_colision, value="inelastica").grid(row=7, column=1,
                                                                                                 sticky="w")

# Coeficiente de roce
ttk.Label(frame_config, text="Coeficiente de roce:").grid(row=8, column=0, sticky="w")
ttk.Entry(frame_config, textvariable=coef_roce).grid(row=8, column=1)

# Botones de control
ttk.Button(frame_config, text="Iniciar Simulación", command=iniciar_simulacion).grid(row=9, column=0, columnspan=2,
                                                                                     pady=10)
ttk.Button(frame_config, text="Pausar/Reanudar", command=pausar_reanudar_simulacion).grid(row=10, column=0, columnspan=2, pady=10)
ttk.Button(frame_config, text="Reiniciar", command=reiniciar_simulacion).grid(row=11, column=0, columnspan=2, pady=10)

# Parámetros adicionales para movimiento en 2D
frame_2d_params = ttk.LabelFrame(root, text="Parámetros Movimiento 2D")
ttk.Label(frame_2d_params, text="Ángulo Auto 1 (grados):").grid(row=0, column=0, sticky="w")
ttk.Entry(frame_2d_params, textvariable=angulo1).grid(row=0, column=1)

ttk.Label(frame_2d_params, text="Ángulo Auto 2 (grados):").grid(row=1, column=0, sticky="w")
ttk.Entry(frame_2d_params, textvariable=angulo2).grid(row=1, column=1)

ttk.Label(frame_2d_params, text="Gravedad (m/s²):").grid(row=2, column=0, sticky="w")
ttk.Entry(frame_2d_params, textvariable=gravedad).grid(row=2, column=1)

# Zona de simulación
frame_simulacion = ttk.LabelFrame(root, text="Simulación")
frame_simulacion.grid(row=0, column=2, padx=10, pady=10)

# Contenedor de Pygame dentro de Tkinter
canvas_simulacion = tk.Canvas(frame_simulacion, width=ANCHO_SIMULACION, height=ALTO_SIMULACION, bg="white")
canvas_simulacion.pack()

# Función para la simulación con Pygame
def simulacion():
    global particula1, particula2, tiempo, energia_auto1, energia_auto2, momento_auto1, momento_auto2, rebotes_auto1, rebotes_auto2, trayectoria_auto1, trayectoria_auto2, simulacion_activa, pausada
    reloj = pygame.time.Clock()
    t = 0  # Tiempo inicial

    while simulacion_activa:
        if not pausada:
            ventana_simulacion.fill(BLANCO)

            # Dibujar la traza de las partículas
            for i in range(1, len(trayectoria_auto1)):
                pygame.draw.line(ventana_simulacion, GRIS, trayectoria_auto1[i - 1], trayectoria_auto1[i], 2)
            for i in range(1, len(trayectoria_auto2)):
                pygame.draw.line(ventana_simulacion, GRIS, trayectoria_auto2[i - 1], trayectoria_auto2[i], 2)

            # Mover partículas si no están detenidas
            if particula1["velocidad_x"] != 0 or particula1["velocidad_y"] != 0:
                particula1["x"] += particula1["velocidad_x"]
                particula1["y"] += particula1["velocidad_y"]
                particula1["velocidad_y"] += gravedad.get()  # Simular gravedad en movimiento 2D
                particula1["velocidad_x"] -= coef_roce.get() * particula1["velocidad_x"]  # Aplicar roce en X

                # Limitar el movimiento a los bordes de la simulación y detener por borde
                if particula1["x"] <= 0 or particula1["x"] >= ANCHO_SIMULACION:
                    particula1["velocidad_x"] = 0
                    rebotes_auto1 += 1
                if particula1["y"] <= 0 or particula1["y"] >= ALTO_SIMULACION:
                    particula1["velocidad_y"] = 0
                    rebotes_auto1 += 1

                trayectoria_auto1.append((particula1["x"], particula1["y"]))

            if particula2["velocidad_x"] != 0 or particula2["velocidad_y"] != 0:
                particula2["x"] += particula2["velocidad_x"]
                particula2["y"] += particula2["velocidad_y"]
                particula2["velocidad_y"] += gravedad.get()  # Simular gravedad en movimiento 2D
                particula2["velocidad_x"] -= coef_roce.get() * particula2["velocidad_x"]  # Aplicar roce en X

                # Limitar el movimiento a los bordes de la simulación y detener por borde
                if particula2["x"] <= 0 or particula2["x"] >= ANCHO_SIMULACION:
                    particula2["velocidad_x"] = 0
                    rebotes_auto2 += 1
                if particula2["y"] <= 0 or particula2["y"] >= ALTO_SIMULACION:
                    particula2["velocidad_y"] = 0
                    rebotes_auto2 += 1

                trayectoria_auto2.append((particula2["x"], particula2["y"]))

            # Detener la simulación si cualquier partícula ha rebotado dos veces
            if rebotes_auto1 >= 2 or rebotes_auto2 >= 2:
                simulacion_activa = False

            # Detectar colisión entre partículas y actualizar velocidades según el tipo de colisión
            distancia = math.sqrt((particula1["x"] - particula2["x"]) ** 2 + (particula1["y"] - particula2["y"]) ** 2)
            if distancia <= (math.sqrt(particula1["masa"]) + math.sqrt(particula2["masa"])):  # Tamaño de los radios según la masa
                v1_x = particula1["velocidad_x"]
                v2_x = particula2["velocidad_x"]
                v1_y = particula1["velocidad_y"]
                v2_y = particula2["velocidad_y"]
                m1 = particula1["masa"]
                m2 = particula2["masa"]

                if tipo_colision.get() == "elastica":
                    # Colisión elástica en ambas direcciones (x e y)
                    particula1["velocidad_x"] = ((m1 - m2) * v1_x + 2 * m2 * v2_x) / (m1 + m2)
                    particula2["velocidad_x"] = ((m2 - m1) * v2_x + 2 * m1 * v1_x) / (m1 + m2)
                    particula1["velocidad_y"] = ((m1 - m2) * v1_y + 2 * m2 * v2_y) / (m1 + m2)
                    particula2["velocidad_y"] = ((m2 - m1) * v2_y + 2 * m1 * v1_y) / (m1 + m2)
                elif tipo_colision.get() == "inelastica":
                    # Colisión inelástica (se unen y comparten la velocidad)
                    velocidad_final_x = (m1 * v1_x + m2 * v2_x) / (m1 + m2)
                    velocidad_final_y = (m1 * v1_y + m2 * v2_y) / (m1 + m2)
                    particula1["velocidad_x"] = velocidad_final_x
                    particula2["velocidad_x"] = velocidad_final_x
                    particula1["velocidad_y"] = velocidad_final_y
                    particula2["velocidad_y"] = velocidad_final_y

            # Dibujar partículas (como círculos cuyo tamaño depende de la masa)
            radio1 = int(math.sqrt(particula1["masa"]) * 5)  # Tamaño del círculo proporcional a la raíz de la masa
            radio2 = int(math.sqrt(particula2["masa"]) * 5)
            pygame.draw.circle(ventana_simulacion, AZUL, (int(particula1["x"]), int(particula1["y"])), radio1)
            pygame.draw.circle(ventana_simulacion, ROJO, (int(particula2["x"]), int(particula2["y"])), radio2)

            # Actualizar energías cinéticas y momento lineal si los autos se están moviendo
            energia1 = 0.5 * particula1["masa"] * (particula1["velocidad_x"] ** 2 + particula1["velocidad_y"] ** 2)
            energia2 = 0.5 * particula2["masa"] * (particula2["velocidad_x"] ** 2 + particula2["velocidad_y"] ** 2)
            momento1 = particula1["masa"] * math.sqrt(particula1["velocidad_x"] ** 2 + particula1["velocidad_y"] ** 2)
            momento2 = particula2["masa"] * math.sqrt(particula2["velocidad_x"] ** 2 + particula2["velocidad_y"] ** 2)

            tiempo.append(t)
            energia_auto1.append(energia1)
            energia_auto2.append(energia2)
            momento_auto1.append(momento1)
            momento_auto2.append(momento2)
            t += 1

            # Asegurar que las listas de energía y momento tengan la misma longitud que el tiempo
            while len(energia_auto1) < len(tiempo):
                energia_auto1.append(0)
            while len(energia_auto2) < len(tiempo):
                energia_auto2.append(0)
            while len(momento_auto1) < len(tiempo):
                momento_auto1.append(0)
            while len(momento_auto2) < len(tiempo):
                momento_auto2.append(0)

            # Actualizar gráficos
            ax1.clear()
            ax2.clear()
            ax1.plot(tiempo, energia_auto1, color='blue', label='Auto 1')
            ax1.plot(tiempo, energia_auto2, color='red', label='Auto 2')
            ax1.legend()
            ax2.plot(tiempo, momento_auto1, color='blue', label='Auto 1')
            ax2.plot(tiempo, momento_auto2, color='red', label='Auto 2')
            ax2.legend()
            ax1.set_title("Energía Cinética")
            ax1.set_xlabel("Tiempo")
            ax1.set_ylabel("Energía (J)")
            ax2.set_title("Momento Lineal")
            ax2.set_xlabel("Tiempo")
            ax2.set_ylabel("Momento (kg·m/s)")
            canvas_fig.draw()

            # Actualizar indicadores de estado
            estado_velocidad1.set(f"Velocidad Auto 1: {math.sqrt(particula1['velocidad_x'] ** 2 + particula1['velocidad_y'] ** 2):.2f} m/s")
            estado_velocidad2.set(f"Velocidad Auto 2: {math.sqrt(particula2['velocidad_x'] ** 2 + particula2['velocidad_y'] ** 2):.2f} m/s")
            estado_energia1.set(f"Energía Auto 1: {energia1:.2f} J")
            estado_energia2.set(f"Energía Auto 2: {energia2:.2f} J")
            estado_rebotes1.set(f"Rebotes Auto 1: {rebotes_auto1}")
            estado_rebotes2.set(f"Rebotes Auto 2: {rebotes_auto2}")

            # Convertir superficie de Pygame a imagen de PIL
            imagen_pygame = pygame.surfarray.array3d(ventana_simulacion)
            imagen_pil = Image.fromarray(imagen_pygame.transpose((1, 0, 2)))
            imagen_tk = ImageTk.PhotoImage(imagen_pil)

            # Renderizar imagen en el canvas de Tkinter
            canvas_simulacion.create_image(0, 0, anchor="nw", image=imagen_tk)
            canvas_simulacion.image = imagen_tk

            # Salir del bucle si ambos autos están detenidos
            if (particula1["velocidad_x"] == 0 and particula1["velocidad_y"] == 0) and (particula2["velocidad_x"] == 0 and particula2["velocidad_y"] == 0):
                simulacion_activa = False

        # Salir del bucle al cerrar la ventana
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                simulacion_activa = False

        root.update_idletasks()
        root.update()
        reloj.tick(60)

# Iniciar el loop principal de Tkinter
root.mainloop()
