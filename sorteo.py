#!/usr/bin/env python3

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

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
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

    conn.commit()
    conn.close()

# Agregar un nuevo ticket
def agregar_ticket(animal1, animal2, animal3, monto):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('''
        INSERT INTO tickets (animal1, animal2, animal3, monto, timestamp)
        VALUES (?, ?, ?, ?, ?)
    ''', (animal1, animal2, animal3, monto, timestamp))

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

    cursor.execute('''
        SELECT SUM(monto) FROM tickets
    ''')

    total = cursor.fetchone()[0]
    conn.close()

    return total if total else 0

# Verificar si hay un ticket ganador
def verificar_ganador():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute('SELECT resultado FROM sorteos')
    resultados = [row[0] for row in cursor.fetchall()]

    if len(resultados) < 3:
        return None

    cursor.execute('SELECT * FROM tickets')
    tickets = cursor.fetchall()
    
    for ticket in tickets:
        animal1, animal2, animal3 = ticket[1], ticket[2], ticket[3]
        if animal1 in resultados and animal2 in resultados and animal3 in resultados:
            if resultados.index(animal1) < resultados.index(animal2) < resultados.index(animal3):
                return ticket

    conn.close()
    return None

# Guardar el ticket ganador en un archivo .txt
def guardar_ticket_ganador(ticket_info):
    with open("ganadores.txt", "a") as file:
        file.write(ticket_info + "\n")

# Generar el ticket en el formato correcto
def generar_ticket(ticket):
    id_ticket, animal1, animal2, animal3, monto, timestamp = ticket
    ticket_info = f"""\
TICKET
La Millonaria
SERIAL #{id_ticket + 1000000}
TICKET #{id_ticket}
{timestamp}
---------CAJA FUERTE---------
01 {animal1} 02 {animal2} 03 {animal3}
-----------------------------

Monto: {monto} SOL
REVISE SU TICKET NO ACEPTAMOS RECLAMOS
"""
    return ticket_info

# Copiar texto al portapapeles
def copiar_al_portapapeles(texto):
    window.clipboard_clear()
    window.clipboard_append(texto)
    messagebox.showinfo("Copiado", "El texto ha sido copiado al portapapeles.")

# Interfaz gráfica
def interfaz():
    def agregar_ticket_action():
        animal1 = entry_animal1.get()
        animal2 = entry_animal2.get()
        animal3 = entry_animal3.get()
        try:
            monto = float(entry_monto.get())
            ticket_id, timestamp = agregar_ticket(animal1, animal2, animal3, monto)
            ticket_info = generar_ticket((ticket_id, animal1, animal2, animal3, monto, timestamp))
            messagebox.showinfo("Ticket creado", f"El ticket ha sido creado:\n\n{ticket_info}")
            
            # Opción para copiar el ticket
            if messagebox.askyesno("Copiar Ticket", "¿Deseas copiar el ticket al portapapeles?"):
                copiar_al_portapapeles(ticket_info)

        except ValueError:
            messagebox.showerror("Error", "Por favor ingresa un monto válido.")

    def agregar_resultado_action():
        hora = entry_hora.get()
        resultado = entry_resultado.get()
        agregar_resultado(hora, resultado)

        ganador = verificar_ganador()
        if ganador:
            ticket_info = generar_ticket(ganador)
            total = calcular_monto_total()
            premio_repartir = total * 0.9  # Total menos el 10%
            ticket_info += f"\nPremio a repartir: {premio_repartir:.2f} soles."
            messagebox.showinfo("¡Ticket ganador!", f"{ticket_info}\nPremio a repartir: {premio_repartir:.2f} soles.")
            
            # Copiar ticket y premio al portapapeles
            if messagebox.askyesno("Copiar Ticket", "¿Deseas copiar el ticket ganador al portapapeles?"):
                copiar_al_portapapeles(ticket_info)

            # Guardar el ticket ganador en un archivo .txt
            guardar_ticket_ganador(ticket_info)

            reiniciar_base_datos()

        else:
            messagebox.showinfo("Resultado agregado", f"El resultado del sorteo a las {hora} ha sido agregado. No hay ganador por ahora.")

    def ver_monto_total():
        total = calcular_monto_total()
        premio_repartir = total * 0.9
        mensaje_monto = f"Premio a repartir: {premio_repartir:.2f} soles."
        messagebox.showinfo("Monto acumulado", mensaje_monto)
        
        if messagebox.askyesno("Copiar Monto", "¿Deseas copiar el monto al portapapeles?"):
            copiar_al_portapapeles(mensaje_monto)

    def reiniciar_base_datos():
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM tickets')
        conn.commit()
        conn.close()
        messagebox.showinfo("Reiniciado", "La base de datos ha sido reiniciada.")

    # Crear la ventana principal
    global window
    window = tk.Tk()
    window.title("Sistema de Sorteos")

    # Campos para ingresar los animales
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

    # Campos para ingresar el resultado por hora
    tk.Label(window, text="Hora del sorteo (HH:MM):").pack()
    entry_hora = tk.Entry(window)
    entry_hora.pack()

    tk.Label(window, text="Resultado del sorteo:").pack()
    entry_resultado = tk.Entry(window)
    entry_resultado.pack()

    tk.Button(window, text="Agregar Resultado", command=agregar_resultado_action).pack()

    # Botón para ver el monto total acumulado
    tk.Button(window, text="Ver Monto Total", command=ver_monto_total).pack()

    window.mainloop()

# Ejecutar la creación de la base de datos y abrir la interfaz
create_db()
interfaz()
