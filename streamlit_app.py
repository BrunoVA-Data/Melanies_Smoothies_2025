# 🐍 Importar paquetes de Python
import streamlit as st
import requests
#from snowflake.snowpark.functions import col
from snowflake.snowpark.exceptions import SnowparkClientException # Importación necesaria para el manejo de errores

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
# CAMBIO: Manejo robusto de la conexión a Snowflake.
# El código original de GitHub tenía 'session = cnx.session()', lo cual causaba el AttributeError.
# La forma correcta es acceder al atributo '.session' del objeto de conexión.
try:
    conn = st.connection("snowflake")
    session = conn.session # CORRECCIÓN CLAVE: Acceder a 'session' como un atributo, no como una función.
except SnowparkClientException as e:
    st.error(f"Error al conectar con Snowflake: {e}. Asegúrate de que tu configuración de conexión es correcta.")
    st.stop() # Detener la ejecución si no se puede conectar

# Seleccionar solo la columna con los nombres de frutas
my_dataframe = session.table("smoothies.public.fruit_options").select(col("FRUIT_NAME"))
fruit_options = my_dataframe.to_pandas()["FRUIT_NAME"].tolist()  # Convertir a lista de strings

# 🧃 Selección de ingredientes con límite de 5 frutas
# CAMBIO: Ajuste de 'max_selections' para limitar correctamente a 5.
# El código de GitHub tenía 'max_selections=6' que permitía 6 selecciones.
ingredients_list = st.multiselect(
    'Elige hasta 5 ingredientes:',
    fruit_options,
    max_selections=5  # CORRECCIÓN: Cambiado a 5 para limitar a 5 selecciones
)

# 🔁 Formatear ingredientes seleccionados como string y mostrar información nutricional
if ingredients_list:
    # CAMBIO: Uso de ', '.join() para una construcción de cadena más limpia y robusta.
    # El código de GitHub usaba concatenación en un bucle, que es menos eficiente y propenso a errores.
    ingredients_string = ', '.join(ingredients_list) 

    # --- Nueva sección para mostrar información nutricional de las frutas ---
    st.subheader("Información Nutricional de los Ingredientes:")
    for fruit_chosen in ingredients_list:
        st.write(f"**{fruit_chosen}**") # Muestra el nombre de la fruta

        # CAMBIO: Implementación de manejo robusto de llamadas a API.
        # El código de GitHub llamaba directamente a .json() sin verificar la respuesta,
        # lo que causaba el JSONDecodeError si la API no devolvía JSON válido o un error.
        # También se asegura el uso de la URL de SmoothieFroot.
        api_url = f"https://my.smoothiefroot.com/api/fruit/{fruit_chosen.lower()}" # Uso de .lower() para URLs amigables
        
        try:
            smoothiefroot_response = requests.get(api_url)
            
            # Verificación del código de estado HTTP (200 = OK)
            if smoothiefroot_response.status_code == 200:
                try:
                    # Intenta parsear la respuesta como JSON
                    nutrition_data = smoothiefroot_response.json()
                    st.dataframe(data=nutrition_data, use_container_width=True)
                except requests.exceptions.JSONDecodeError:
                    # Mensaje de advertencia si la respuesta no es JSON válido
                    st.warning(f"No se pudo decodificar la respuesta JSON para {fruit_chosen}. La API podría no estar devolviendo JSON válido.")
                    st.text(smoothiefroot_response.text) # Muestra la respuesta cruda para depuración
            else:
                # Mensaje de advertencia si la API devuelve un código de estado de error
                st.warning(f"Error al obtener datos nutricionales para {fruit_chosen}: Código de estado {smoothiefroot_response.status_code}. URL: {api_url}")
                st.text(smoothiefroot_response.text) # Muestra la respuesta cruda para depuración
        except requests.exceptions.RequestException as e:
            # Mensaje de error para problemas de conexión o de red
            st.error(f"Error de conexión al intentar obtener datos nutricionales para {fruit_chosen}: {e}. Verifica la URL de la API y tu conexión a internet.")
        st.markdown("---") # Separador para cada fruta
    # --- Fin de la nueva sección ---

    # 📤 Crear el statement SQL de inserción
    # CAMBIO: La creación de my_insert_stmt y el botón de envío se movieron fuera del bucle de ingredientes.
    # En el código de GitHub, estaban dentro del bucle, lo que los crearía múltiples veces.
    my_insert_stmt = f"""
        insert into smoothies.public.orders (ingredients, name_on_order)
        values ('{ingredients_string}', '{name_on_order}')
    """

    # ⏩ Botón para enviar pedido
    # CAMBIO: Texto del botón en español para consistencia.
    time_to_insert = st.button('Enviar Pedido') 

    if time_to_insert:
        try:
            session.sql(my_insert_stmt).collect()
            st.success("¡Tu Batido ha sido ordenado, " + name_on_order + "!")
        except Exception as e:
            st.error(f"Error al enviar el pedido: {e}. Por favor, inténtalo de nuevo.")
else:
    st.info("Por favor, selecciona al menos un ingrediente para tu batido.")

