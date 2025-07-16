# 🐍 Importar paquetes de Python
import streamlit as st
from snowflake.snowpark.functions import col # <-- Esta línea fue añadida
from snowflake.snowpark.exceptions import SnowparkClientException

# 🖥️ Mostrar título y subtítulo
st.title(":cup_with_straw: ¡Personaliza tu Batido! :cup_with_straw:")
st.write(
    """
    **¡Elige las frutas que quieres en tu Batido personalizado!**
    """
)

# 🧑‍💻 Entrada del nombre del cliente
name_on_order = st.text_input('Nombre en el Batido:')
st.write('El nombre en tu Batido será:', name_on_order)

# 📥 Conexión a Snowflake y carga de datos
# Corrección del problema de conexión:
# Usar st.connection() para obtener el objeto de conexión
# y luego .session para obtener la sesión de Snowpark.
try:
    conn = st.connection("snowflake")
    session = conn.session
except SnowparkClientException as e:
    st.error(f"Error al conectar con Snowflake: {e}. Asegúrate de que tu configuración de conexión es correcta.")
    st.stop() # Detener la ejecución si no se puede conectar

# Seleccionar solo la columna con los nombres de frutas
my_dataframe = session.table("smoothies.public.fruit_options").select(col("FRUIT_NAME"))
# Convertir a lista de strings
fruit_options = my_dataframe.to_pandas()["FRUIT_NAME"].tolist() 

# 🧃 Selección de ingredientes con límite de 5 frutas
ingredients_list = st.multiselect(
    'Elige hasta 5 ingredientes:',
    fruit_options,
    max_selections=5  # ✅ Restringir máximo 5 selecciones
)

# 🔁 Formatear ingredientes seleccionados como string
if ingredients_list:
    ingredients_string = ', '.join(ingredients_list) # Formato más limpio con join

    # 📤 Crear el statement SQL de inserción
    my_insert_stmt = f"""
        insert into smoothies.public.orders (ingredients, name_on_order)
        values ('{ingredients_string}', '{name_on_order}')
    """

    # ⏩ Botón para enviar pedido
    time_to_insert = st.button('Enviar Pedido')

    if time_to_insert:
        try:
            session.sql(my_insert_stmt).collect()
            st.success("¡Tu Batido ha sido ordenado, " + name_on_order + "!")
        except Exception as e:
            st.error(f"Error al enviar el pedido: {e}. Por favor, inténtalo de nuevo.")
else:
    st.info("Por favor, selecciona al menos un ingrediente para tu batido.")

