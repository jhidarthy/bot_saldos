# exportar_excel.py

import pandas as pd
from sqlalchemy import text
from database import SessionLocal
from datetime import datetime
from openpyxl import load_workbook
from openpyxl.styles import PatternFill

# La función para aplicar formato no necesita cambios.
def aplicar_formato_condicional(nombre_archivo: str):
    """
    Abre un archivo de Excel y aplica formato condicional.
    """
    try:
        workbook = load_workbook(nombre_archivo)
        sheet = workbook.active
        relleno_rojo = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")
        encabezados = [cell.value for cell in sheet[1]]
        try:
            col_saldo_idx = encabezados.index('saldo') + 1
            col_detalle_idx = encabezados.index('detalle') + 1
        except ValueError as e:
            print(f"Error: No se encontró la columna requerida en el Excel: {e}")
            return

        for fila in sheet.iter_rows(min_row=2):
            celda_detalle = fila[col_detalle_idx - 1]
            celda_saldo = fila[col_saldo_idx - 1]

            if celda_detalle.value == "Saldo expirado":
                for celda in fila:
                    celda.fill = relleno_rojo
                continue

            try:
                if celda_saldo.value is not None and float(celda_saldo.value) < 50.0:
                    for celda in fila:
                        celda.fill = relleno_rojo
            except (ValueError, TypeError):
                continue

        workbook.save(nombre_archivo)
        print("🎨 Se ha aplicado el formato condicional con éxito.")
    except Exception as e:
        print(f"❌ Ocurrió un error al aplicar el formato: {e}")


# --- ✅ FUNCIÓN PRINCIPAL MODIFICADA ---
def exportar_consultas_a_excel(fecha_str: str):
    """
    Consulta los registros de un día, aplica la lógica de redundancia y
    exporta el resultado a un archivo de Excel.
    """
    try:
        fecha_obj = datetime.strptime(fecha_str, '%Y-%m-%d').date()
    except ValueError:
        print("❌ Error: El formato de la fecha es incorrecto. Usa AAAA-MM-DD.")
        return

    db = SessionLocal()
    try:
        # 1. Obtenemos TODOS los registros del día
        consulta_sql = text("""
            SELECT unidad, numero_celular, saldo, fecha_vencimiento, 
                   fecha_consulta, estado_consulta, detalle 
            FROM unidad 
            WHERE CAST(fecha_consulta AS DATE) = :fecha_a_buscar
        """)
        df_completo = pd.read_sql(consulta_sql, db.bind, params={"fecha_a_buscar": fecha_obj})

        if df_completo.empty:
            print(f"⚠️ No se encontraron registros para la fecha {fecha_str}.")
            return

        print(f"Se encontraron {len(df_completo)} registros en total. Aplicando lógica de consolidación...")

        # 2. Lógica de consolidación con Pandas (ACTUALIZADA)
        def obtener_registro_definitivo(grupo):
            """
            Prioriza el registro 'Exitoso' MÁS RECIENTE del día.
            Si no hay ninguno 'Exitoso', devuelve el 'Fallido' MÁS RECIENTE.
            """
            # Ordena los registros del grupo del más nuevo al más viejo
            grupo_ordenado = grupo.sort_values(by='fecha_consulta', ascending=False)
            
            # Filtra para encontrar solo los exitosos
            registros_exitosos = grupo_ordenado[grupo_ordenado['estado_consulta'] == 'Exitoso']
            
            if not registros_exitosos.empty:
                # ¡Hay éxito! Devolver el MÁS RECIENTE de los exitosos
                # (que será el primero de esta lista, .iloc[0])
                return registros_exitosos.iloc[0]
            else:
                # No hay NINGÚN registro exitoso. Devolver el MÁS RECIENTE
                # del grupo completo (que será el 'Fallido' más reciente).
                return grupo_ordenado.iloc[0]

        # Agrupamos por número y aplicamos nuestra función para obtener la fila definitiva
        df_final = df_completo.groupby('numero_celular').apply(obtener_registro_definitivo)
        
        # Reseteamos el índice para que 'numero_celular' vuelva a ser una columna
        df_final = df_final.reset_index(drop=True)

        print(f"✅ Consolidación completa. Se generará un reporte con {len(df_final)} registros definitivos.")
        
        # 3. Exportar el DataFrame final y limpio
        nombre_archivo = f"Reporte_Saldos_Consolidado_{fecha_str}.xlsx"
        df_final.to_excel(nombre_archivo, index=False, sheet_name='Reporte Consolidado')
        
        print(f"¡Éxito! Los datos han sido guardados en: {nombre_archivo}")

        # 4. Aplicar el formato condicional al nuevo archivo
        aplicar_formato_condicional(nombre_archivo)

    except Exception as e:
        print(f"❌ Ocurrió un error durante la exportación: {e}")
    finally:
        db.close()

# --- EJECUCIÓN DEL SCRIPT ---
if __name__ == "__main__":
    # Para pruebas, puedes poner una fecha fija, o dejar el input
    # fecha_input = datetime.now().strftime('%Y-%m-%d') # Para usar la fecha de hoy
    fecha_input = input("Ingresa la fecha para el reporte (formato AAAA-MM-DD): ")
    exportar_consultas_a_excel(fecha_input)
