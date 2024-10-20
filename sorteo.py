#!/usr/bin/env python3

import sqlite3
import tkinter as tk
from tkinter import messagebox


def interfaz():
    def agregar():
        animal1 = entry_animal1.get()
        animal2 = entry_animal2.get()
        animal3 = entry_animal3.get()
        monto = float(entry_monto.get())

        agregar_ticket(animal1, animal2, animal3, monto)
        messagebox.showinfo(
            "Ticket agregado", "El ticket ha sido agregado exitosamente."
        )

    def mostrar_total():
        total = calcular_monto_total()
        messagebox.showinfo(
            "Monto total jugado", f"El monto total jugado es: {total} soles."
        )

    def verificar():
        ganador = verificar_ganador()
        if ganador:
            messagebox.showinfo("¡Ticket ganador!", f"El ticket ganador es: {ganador}")
            reiniciar_base_datos()
        else:
            messagebox.showinfo("Sin ganadores", "No hay ningún ticket ganador.")

    def reiniciar_base_datos():
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tickets")
        conn.commit()
        conn.close()
        messagebox.showinfo("Reiniciado", "La base de datos ha sido reiniciada.")

    window = tk.Tk()
    window.title("Sistema de Sorteos")

    # Campos para ingresar los animales/números
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

    # Botones para las funciones
    tk.Button(window, text="Agregar Ticket", command=agregar).pack()
    tk.Button(window, text="Verificar Ganador", command=verificar).pack()
    tk.Button(window, text="Mostrar Monto Total", command=mostrar_total).pack()

    window.mainloop()


interfaz()


def create_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # Creamos la tabla de tickets
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            animal1 TEXT,
            animal2 TEXT,
            animal3 TEXT,
            monto REAL
        )
    """
    )

    conn.commit()
    conn.close()


create_db()


def agregar_ticket(animal1, animal2, animal3, monto):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO tickets (animal1, animal2, animal3, monto)
        VALUES (?, ?, ?, ?)
    """,
        (animal1, animal2, animal3, monto),
    )

    conn.commit()
    conn.close()


def verificar_ganador():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # Aquí se debe definir la condición ganadora (ejemplo: "gato", "perro", "ratón")
    cursor.execute(
        """
        SELECT * FROM tickets
        WHERE animal1 = 'gato' AND animal2 = 'perro' AND animal3 = 'ratón'
    """
    )

    ganador = cursor.fetchone()  # Obtiene el primer ticket que cumpla la condición

    conn.close()

    if ganador:
        return ganador
    return None


def calcular_monto_total():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT SUM(monto) FROM tickets")
    total = cursor.fetchone()[0]

    conn.close()

    return total if total else 0
