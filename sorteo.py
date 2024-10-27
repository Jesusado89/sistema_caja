#!/usr/bin/env python3

import tkinter as tk
from tkinter import messagebox
import sqlite3
import datetime

# Crear la base de datos y las tablas necesarias
def create_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute('DROP TABLE IF EXISTS tickets')
    cursor.execute('DROP TABLE IF EXISTS sorteos')
    cursor.execute('DROP TABLE IF EXISTS acumulado')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT,
            animal1 TEXT,
            animal2 TEXT,
            animal3 TEXT,
            monto REAL,
            timestamp TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sorteos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hora TEXT,
            resultado TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS acumulado (
            id INTEGER PRIMARY KEY,
            monto REAL DEFAULT 0
        )
    ''')

    cursor.execute("INSERT INTO acumulado (id, monto) VALUES (1, 0)")
    conn.commit()
    conn.close()

# Agregar un nuevo ticket
def agregar_ticket(nombre, animal1, animal2, animal3, monto):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('''
        INSERT INTO tickets (nombre, animal1, animal2, animal3, monto, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (nombre, animal1, animal2, animal3, monto, timestamp))

    cursor.execute('UPDATE acumulado SET monto = monto + ?', (monto,))
    ticket_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return ticket_id, timestamp

# Agregar un nuevo resultado
def agregar_resultado(hora, resultado):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO sorteos (hora, resultado)
        VALUES (?, ?)
    ''', (hora, resultado))

    conn.commit()
    conn.close()

# Calcular el monto total jugado
def calcular_monto_total():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute('SELECT monto FROM acumulado WHERE id = 1')
    total = cursor.fetchone()[0]
    conn.close()

    return total * 0.8  # Descontar el 20%

# Verificar si hay tickets ganadores
def verificar_ganador():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute('SELECT resultado FROM sorteos')
    resultados = [row[0] for row in cursor.fetchall()]

    if len(resultados) < 3:
        return []

    cursor.execute('SELECT * FROM tickets')
    tickets = cursor.fetchall()
    
    ganadores = []
    for ticket in tickets:
        _, nombre, animal1, animal2, animal3, _, _ = ticket
        if animal1 in resultados and animal2 in resultados and animal3 in resultados:
            if resultados.index(animal1) < resultados.index(animal2) < resultados.index(animal3):
                ganadores.append(ticket)

    conn.close()
    return ganadores

# Generar el ticket en el formato correcto
def generar_ticket(ticket, premio_por_ganador=None):
    id_ticket, nombre, animal1, animal2, animal3, monto, timestamp = ticket
    premio_texto = f"Premio ganado: {premio_por_ganador:.2f} SOL" if premio_por_ganador else ""
    ticket_info = f"""\
TICKET
La Millonaria
SERIAL #{id_ticket + 1000000}
TICKET #{id_ticket}
{timestamp}
Nombre del Jugador: {nombre}
---------CAJA FUERTE---------
01 {animal1} 02 {animal2} 03 {animal3}
-----------------------------

Monto: {monto} SOL
REVISE SU TICKET NO ACEPTAMOS RECLAMOS
{premio_texto}
"""
    return ticket_info

# Copiar texto al portapapeles
def copiar_al_portapapeles(texto):
    window.clipboard_clear()
    window.clipboard_append(texto)
    messagebox.showinfo("Copiado", "El texto ha sido copiado al portapapeles.")

# Reiniciar la base de datos incluyendo el monto acumulado cuando hay un ganador
def reiniciar_base_datos_completa():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM tickets')
    cursor.execute('DELETE FROM sorteos')
    cursor.execute('UPDATE acumulado SET monto = 0')
    conn.commit()
    conn.close()
    messagebox.showinfo("Reiniciado", "La base de datos ha sido reiniciada completamente.")

# Interfaz gráfica
def interfaz():
    def agregar_ticket_action():
        nombre = entry_nombre.get()
        animal1 = entry_animal1.get()
        animal2 = entry_animal2.get()
        animal3 = entry_animal3.get()
        try:
            monto = float(entry_monto.get())
            ticket_id, timestamp = agregar_ticket(nombre, animal1, animal2, animal3, monto)
            ticket_info = generar_ticket((ticket_id, nombre, animal1, animal2, animal3, monto, timestamp))
            messagebox.showinfo("Ticket creado", f"El ticket ha sido creado:\n\n{ticket_info}")
            
            # Opción para copiar el ticket
            if messagebox.askyesno("Copiar Ticket", "¿Deseas copiar el ticket al portapapeles?"):
                copiar_al_portapapeles(ticket_info)

            # Guardar en jugadores.txt
            with open("jugadores.txt", "a") as f:
                f.write(f"Jugador {nombre}: {animal1}, {animal2}, {animal3}\n")

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
                generar_ticket(ganador, premio_por_ganador) for ganador in ganadores
            )
            messagebox.showinfo("¡Tickets Ganadores!", f"{ganador_info}\nPremio total a repartir: {total} soles.")

            if messagebox.askyesno("Copiar Tickets", "¿Deseas copiar los tickets ganadores al portapapeles?"):
                copiar_al_portapapeles(ganador_info)

            # Guardar en ganadores.txt bajo un solo sorteo
            with open("ganadores.txt", "a") as f:
                f.write(f"Ganadores del sorteo 1:\n")
                for ganador in ganadores:
                    f.write(f"{generar_ticket(ganador, premio_por_ganador)}\n\n")

            reiniciar_base_datos_completa()  # Reinicia todo incluyendo el acumulado
        else:
            # Verificar si hay 11 resultados sin ganador para reiniciar parcialmente
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM sorteos')
            if cursor.fetchone()[0] >= 11:
                cursor.execute('DELETE FROM tickets')
                conn.commit()
                messagebox.showinfo("Reinicio parcial", "No hubo ganador en 11 sorteos consecutivos. Los tickets han sido eliminados.")
            conn.close()
            messagebox.showinfo("Resultado agregado", f"El resultado del sorteo a las {hora} ha sido agregado. No hay ganador por ahora.")

    def ver_monto_total():
        total = calcular_monto_total()
        mensaje_monto = f"Premio a repartir: {total:.2f} soles."
        messagebox.showinfo("Monto acumulado", mensaje_monto)
        
        if messagebox.askyesno("Copiar Monto", "¿Deseas copiar el monto al portapapeles?"):
            copiar_al_portapapeles(mensaje_monto)

    # Crear la ventana principal
    global window
    window = tk.Tk()
    window.title("Sistema de Sorteos")

    # Campos para ingresar los detalles del ticket
    tk.Label(window, text="Nombre del jugador:").pack()
    entry_nombre = tk.Entry(window)
    entry_nombre.pack()

    tk.Label(window, text="Animal 1:").pack()
    entry_animal1 = tk.Entry(window)
    entry_animal1.pack()

    tk.Label(window, text="Animal 2:").pack()
    entry_animal2 = tk.Entry(window)
    entry_animal2.pack()

    tk.Label(window, text="Animal 3:").pack()
    entry_animal3 = tk.Entry(window)
    entry_animal3.pack()

    tk.Label(window, text="Monto (Soles):").pack()
    entry_monto = tk.Entry(window)
    entry_monto.pack()

    tk.Button(window, text="Agregar Ticket", command=agregar_ticket_action).pack()

    # Campos para agregar un resultado de sorteo
    tk.Label(window, text="Hora del sorteo:").pack()
    entry_hora = tk.Entry(window)
    entry_hora.pack()

    tk.Label(window, text="Resultado:").pack()
    entry_resultado = tk.Entry(window)
    entry_resultado.pack()

    tk.Button(window, text="Agregar Resultado", command=agregar_resultado_action).pack()

    # Ver el monto acumulado
    tk.Button(window, text="Ver Monto Acumulado", command=ver_monto_total).pack()

    window.mainloop()

# Ejecutar el código principal
create_db()
interfaz()
