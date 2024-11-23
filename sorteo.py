#!/usr/bin/env python3

import tkinter as tk
from tkinter import messagebox
import sqlite3
import datetime


# Crear la base de datos y las tablas necesarias
def create_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT,
            animal1 TEXT,
            animal2 TEXT,
            animal3 TEXT,
            monto REAL,
            timestamp TEXT
        )
    """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS sorteos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hora TEXT,
            resultado TEXT
        )
    """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS acumulado (
            id INTEGER PRIMARY KEY,
            monto REAL DEFAULT 0
        )
    """
    )

    # Inicializar acumulado si no existe
    cursor.execute("INSERT OR IGNORE INTO acumulado (id, monto) VALUES (1, 0)")
    conn.commit()
    conn.close()


# Actualizar o crear archivo jugadores.txt
def actualizar_archivo_jugadores(nombre, animal1, animal2, animal3):
    with open("jugadores.txt", "a") as archivo:
        archivo.write(f"Jugador: {nombre}\n")
        archivo.write(f"Animales: {animal1}, {animal2}, {animal3}\n")
        archivo.write("-" * 30 + "\n")


# Agregar un nuevo ticket
def agregar_ticket(nombre, animal1, animal2, animal3, monto):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        """
        INSERT INTO tickets (nombre, animal1, animal2, animal3, monto, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
    """,
        (nombre, animal1, animal2, animal3, monto, timestamp),
    )

    # Actualizar el monto acumulado
    cursor.execute("UPDATE acumulado SET monto = monto + ?", (monto,))
    conn.commit()
    ticket_id = cursor.lastrowid
    conn.close()

    # Actualizar archivo jugadores.txt
    actualizar_archivo_jugadores(nombre, animal1, animal2, animal3)

    return ticket_id, timestamp


# Agregar un nuevo resultado del sorteo
def agregar_resultado(hora, resultado):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO sorteos (hora, resultado)
        VALUES (?, ?)
    """,
        (hora, resultado),
    )
    conn.commit()
    conn.close()


# Calcular el monto total jugado (80% después del descuento)
def calcular_monto_total():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT monto FROM acumulado WHERE id = 1")
    total = cursor.fetchone()[0]
    conn.close()
    return total * 0.8  # Descontar el 20%


# Verificar si hay tickets ganadores
def verificar_ganador():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # Obtener los resultados de los sorteos
    cursor.execute("SELECT resultado FROM sorteos")
    resultados = [row[0] for row in cursor.fetchall()]

    # Buscar tickets ganadores
    cursor.execute("SELECT * FROM tickets")
    tickets = cursor.fetchall()

    ganadores = []
    for ticket in tickets:
        _, nombre, animal1, animal2, animal3, _, _ = ticket
        if animal1 in resultados and animal2 in resultados and animal3 in resultados:
            ganadores.append(ticket)

    conn.close()
    return ganadores


# Mostrar jugadores que están a 1 o 2 animales de ganar y los animales faltantes
def jugadores_cerca_de_ganar():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # Obtener los resultados de los sorteos
    cursor.execute("SELECT resultado FROM sorteos")
    resultados = [row[0] for row in cursor.fetchall()]

    # Buscar jugadores cerca de ganar
    cursor.execute("SELECT * FROM tickets")
    tickets = cursor.fetchall()

    cerca_de_ganar = []
    for ticket in tickets:
        _, nombre, animal1, animal2, animal3, _, _ = ticket
        animales = [animal1, animal2, animal3]
        faltantes = [animal for animal in animales if animal not in resultados]
        if len(faltantes) in [1, 2]:
            cerca_de_ganar.append((nombre, len(faltantes), faltantes))

    conn.close()
    return cerca_de_ganar


# Reiniciar la base de datos pero mantener el acumulado
def reiniciar_base_datos():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tickets")
    cursor.execute("DELETE FROM sorteos")
    conn.commit()
    conn.close()


# Copiar texto al portapapeles
def copiar_al_portapapeles(texto):
    window.clipboard_clear()
    window.clipboard_append(texto)
    messagebox.showinfo("Copiado", "El texto ha sido copiado al portapapeles.")


# Generar ticket en formato legible
def generar_ticket(ticket):
    id_ticket, nombre, animal1, animal2, animal3, monto, timestamp = ticket
    return f"""
TICKET 
La Millonaria
Serial #{id_ticket}
Fecha: {timestamp}
Jugador: {nombre}
_____POLLA MILLONARIA_____
Jugadas:
  - {animal1}
  - {animal2}
  - {animal3}
Monto: {monto} SOL
    """


# Interfaz gráfica
def interfaz():
    def agregar_ticket_action():
        nombre = entry_nombre.get()
        animal1 = entry_animal1.get()
        animal2 = entry_animal2.get()
        animal3 = entry_animal3.get()
        try:
            monto = float(entry_monto.get())
            ticket_id, timestamp = agregar_ticket(
                nombre, animal1, animal2, animal3, monto
            )
            ticket = (ticket_id, nombre, animal1, animal2, animal3, monto, timestamp)
            ticket_info = generar_ticket(ticket)
            messagebox.showinfo(
                "Ticket creado", f"El ticket ha sido creado:\n\n{ticket_info}"
            )

            # Copiar al portapapeles
            if messagebox.askyesno(
                "Copiar Ticket", "¿Deseas copiar el ticket al portapapeles?"
            ):
                copiar_al_portapapeles(ticket_info)
        except ValueError:
            messagebox.showerror("Error", "Por favor ingresa un monto válido.")

    def agregar_resultado_action():
        hora = entry_hora.get()
        resultado = entry_resultado.get()
        agregar_resultado(hora, resultado)

        ganadores = verificar_ganador()
        if ganadores:
            total = calcular_monto_total()
            premio_por_ganador = total / len(ganadores)
            ganador_info = "\n\n".join(
                generar_ticket(ganador) + f"\nPremio: {premio_por_ganador:.2f} SOL"
                for ganador in ganadores
            )
            messagebox.showinfo(
                "¡Ganadores!", f"{ganador_info}\nPremio total: {total:.2f} SOL"
            )
            reiniciar_base_datos()
        else:
            messagebox.showinfo("Sin ganadores", "No hay ganadores para este sorteo.")

    def ver_monto_total_action():
        total = calcular_monto_total()
        mensaje = f"Premio a repartir: {total:.2f} SOL"
        messagebox.showinfo("Monto acumulado", mensaje)
        if messagebox.askyesno(
            "Copiar Monto", "¿Deseas copiar el monto al portapapeles?"
        ):
            copiar_al_portapapeles(mensaje)

    def jugadores_cerca_action():
        cerca = jugadores_cerca_de_ganar()
        if cerca:
            lista = "\n".join(
                f"{nombre} está a {coincidencias} animal(es) de ganar. Faltan: {', '.join(faltantes)}"
                for nombre, coincidencias, faltantes in cerca
            )
            messagebox.showinfo("Jugadores cerca de ganar", lista)
            if messagebox.askyesno(
                "Copiar Lista", "¿Deseas copiar la lista al portapapeles?"
            ):
                copiar_al_portapapeles(lista)
        else:
            messagebox.showinfo(
                "Sin jugadores cerca", "No hay jugadores cerca de ganar."
            )

    # Crear ventana principal
    global window
    window = tk.Tk()
    window.title("Sistema de Sorteos")

    # Widgets
    tk.Label(window, text="Nombre del jugador:").grid(row=0, column=0)
    entry_nombre = tk.Entry(window)
    entry_nombre.grid(row=0, column=1)

    tk.Label(window, text="Animal 1:").grid(row=1, column=0)
    entry_animal1 = tk.Entry(window)
    entry_animal1.grid(row=1, column=1)

    tk.Label(window, text="Animal 2:").grid(row=2, column=0)
    entry_animal2 = tk.Entry(window)
    entry_animal2.grid(row=2, column=1)

    tk.Label(window, text="Animal 3:").grid(row=3, column=0)
    entry_animal3 = tk.Entry(window)
    entry_animal3.grid(row=3, column=1)

    tk.Label(window, text="Monto jugado:").grid(row=4, column=0)
    entry_monto = tk.Entry(window)
    entry_monto.grid(row=4, column=1)

    tk.Button(window, text="Agregar Ticket", command=agregar_ticket_action).grid(
        row=5, column=0, columnspan=2
    )

    tk.Label(window, text="Hora del sorteo:").grid(row=6, column=0)
    entry_hora = tk.Entry(window)
    entry_hora.grid(row=6, column=1)

    tk.Label(window, text="Resultado:").grid(row=7, column=0)
    entry_resultado = tk.Entry(window)
    entry_resultado.grid(row=7, column=1)

    tk.Button(window, text="Agregar Resultado", command=agregar_resultado_action).grid(
        row=8, column=0, columnspan=2
    )
    tk.Button(window, text="Ver Monto Total", command=ver_monto_total_action).grid(
        row=9, column=0, columnspan=2
    )
    tk.Button(
        window, text="Jugadores Cerca de Ganar", command=jugadores_cerca_action
    ).grid(row=10, column=0, columnspan=2)

    window.mainloop()


if __name__ == "__main__":
    create_db()
    interfaz()
