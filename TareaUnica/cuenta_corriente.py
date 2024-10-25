import sqlite3
import pandas as pd
import xml.etree.ElementTree as ET
from tabulate import tabulate
from tkinter import Tk
from tkinter.filedialog import askopenfilename

# Conexión a la base de datos (se crea si no existe)
def connect_db():
    conn = sqlite3.connect('cuenta_corriente.db')
    return conn

# Crear tabla de clientes
def create_table():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY,
            nombre TEXT NOT NULL,
            saldo REAL NOT NULL,
            deuda REAL NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Agregar cliente
def agregar_cliente(nombre, saldo_inicial, deuda):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO clientes (nombre, saldo, deuda) VALUES (?, ?, ?)
    ''', (nombre, saldo_inicial, deuda))
    conn.commit()
    conn.close()

# Cargar clientes desde un archivo XML
def cargar_clientes(archivo):
    tree = ET.parse(archivo)
    root = tree.getroot()
    
    for cliente in root.findall('cliente'):
        nombre = cliente.find('nombre').text
        saldo = float(cliente.find('saldo').text)
        deuda = float(cliente.find('deuda').text)
        agregar_cliente(nombre, saldo, deuda)

# Función para seleccionar archivo XML
def seleccionar_archivo():
    Tk().withdraw()  # Ocultar la ventana principal de Tkinter
    archivo = askopenfilename(title="Seleccionar archivo XML", filetypes=[("Archivos XML", "*.xml")])
    return archivo

# Realizar pago
def realizar_pago(cliente_id, monto):
    conn = connect_db()
    cursor = conn.cursor()
    
    # Obtener el saldo actual y la deuda del cliente antes de hacer el pago
    cursor.execute('SELECT nombre, saldo, deuda FROM clientes WHERE id = ?', (cliente_id,))
    cliente = cursor.fetchone()
    
    if cliente:
        nombre, saldo_actual, deuda_actual = cliente
        nuevo_saldo = saldo_actual - monto
        
        # Verificar que el nuevo saldo no sea negativo
        if nuevo_saldo < 0:
            print(f"No se puede realizar el pago. El saldo actual de {nombre} es insuficiente.")
            conn.close()
            return
        
        cursor.execute('''
            UPDATE clientes SET saldo = ?, deuda = ? WHERE id = ?
        ''', (nuevo_saldo, deuda_actual, cliente_id))  # Actualiza el saldo y la deuda
        conn.commit()
        
        # Mostrar detalles de la transacción
        print(f"Pago de {monto} realizado para el cliente {nombre}.")
        print(f"Deuda anterior: {deuda_actual}")
        print(f"Saldo a abonar: {monto}")
        print(f"Saldo restante para {nombre} después del pago: {nuevo_saldo}")
    else:
        print("Cliente no encontrado.")

    conn.close()

# Verificar si hay clientes en la base de datos
def hay_clientes():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM clientes')
    count = cursor.fetchone()[0]
    conn.close()
    return count > 0

# Listar clientes y sus deudas
def listar_clientes():
    conn = connect_db()
    df = pd.read_sql_query('SELECT * FROM clientes', conn)
    conn.close()
    return df

# Imprimir listado de clientes
def imprimir_listado():
    if not hay_clientes():
        print("\n⚠️ Error: No hay clientes cargados. Por favor, cargue o agregue clientes primero.")
        return
    
    df = listar_clientes()
    print("\nListado de Clientes y Deudas:")
    
    # Imprimir en formato de tabla usando tabulate
    print(tabulate(df, headers='keys', tablefmt='pretty', showindex=False))
    
    # Guardar en un archivo HTML
    df.to_html('listado_clientes.html', index=False)
    print("Listado guardado en listado_clientes.html")

# Función para mostrar el menú
def mostrar_menu():
    print("\n" + "="*40)
    print("           SISTEMA DE CUENTA CORRIENTE           ")
    print("="*40)
    print("🔹 Opciones disponibles:")
    print("   1. 📂 Cargar Clientes desde archivo XML")
    print("   2. ➕ Agregar Cliente")
    print("   3. 💸 Realizar Pago")
    print("   4. 📋 Listar Clientes")
    print("   5. 🖨️ Imprimir Listado")
    print("   6. ❌ Salir")
    print("="*40)

# Función principal
def main():
    create_table()
    
    while True:
        mostrar_menu()
        opcion = input("\nSeleccione una opción: ")

        if opcion == '1':
            archivo = seleccionar_archivo()
            if archivo:
                cargar_clientes(archivo)
                print(f"Clientes cargados desde {archivo}.")
            else:
                print("⚠️ No se seleccionó ningún archivo.")
        
        elif opcion == '2':
            nombre = input("Ingrese el nombre del cliente: ")
            saldo_inicial = float(input("Ingrese el saldo inicial: "))
            deuda = float(input("Ingrese la deuda del cliente: "))
            agregar_cliente(nombre, saldo_inicial, deuda)
            print(f"Cliente {nombre} agregado con saldo inicial de {saldo_inicial} y deuda de {deuda}.")
        
        elif opcion == '3':
            if not hay_clientes():
                print("⚠️ Error: No hay clientes cargados. Por favor, cargue o agregue clientes primero.")
                continue
            cliente_id = int(input("Ingrese el ID del cliente: "))
            monto = float(input("Ingrese el monto a pagar: "))
            realizar_pago(cliente_id, monto)
        
        elif opcion == '4':
            if not hay_clientes():
                print("⚠️ Error: No hay clientes cargados. Por favor, cargue o agregue clientes primero.")
            else:
                print("\n" + str(listar_clientes()))
        
        elif opcion == '5':
            imprimir_listado()
        
        elif opcion == '6':
            print("👋 Saliendo del sistema. ¡Gracias por usar el sistema de cuenta corriente!")
            break
        
        else:
            print("⚠️ Opción no válida. Por favor, intente de nuevo.")

if __name__ == '__main__':
    main()