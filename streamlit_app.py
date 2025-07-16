# 🐍 Importar paquetes de Python
import streamlit as st
import requests
import pandas as pd # Asegúrate de que pandas esté importado
from snowflake.snowpark.functions import col
from snowflake.snowpark.exceptions import SnowparkClientException # Necesario para el manejo de errores de conexión

# 🖥️ Mostrar título y subtítulo
st.title(":cup_with_straw: ¡Personaliza tu Batido! :cup_with_straw:") # Traducido al español
st.write(
    """
    **¡Elige las frutas que quieres en tu Batido personalizado!** # Traducido al español
    """
)

# 🧑‍💻 Entrada del nombre del cliente
name_on_order = st.text_input('Nombre en el Batido:') # Traducido al español
st.write('El nombre en tu Batido será:', name_on_order) # Traducido al español

# 📥 Conexión a Snowflake y carga de datos
try:
    cnx = st.connection("snowflake")
    session = cnx.session # CORRECCIÓN: Acceder a 'session' como atributo, no como método.
except SnowparkClientException as e:
    st.error(f"Error al conectar con Snowflake: {e}. Asegúrate de que tu configuración de conexión es correcta.")
    st.stop() # Detener la ejecución si no se puede conectar

# Seleccionar las columnas FRUIT_NAME y SEARCH_ON
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))

# Convertir el Snowpark DataFrame a un Pandas DataFrame para usar .loc
pd_df = my_dataframe.to_pandas()

# CORRECCIÓN: Descomentar y definir 'fruit_options' aquí.
# 'fruit_options' se usa en st.multiselect, por lo que debe estar definida antes.
fruit_options = pd_df["FRUIT_NAME"].tolist()

# 🧃 Selección de ingredientes con límite de 5 frutas
ingredients_list = st.multiselect(
    'Elige hasta 5 ingredientes:', # Traducido al español
    fruit_options,
    max_selections=5  # CORRECCIÓN: Cambiado a 5 para limitar a 5 selecciones.
)

# 🔁 Formatear ingredientes seleccionados como string y mostrar información nutricional
if ingredients_list:
    # CORRECCIÓN: Construir ingredients_string con ', '.join() fuera del bucle de visualización.
    # Esto asegura que la cadena se construya una sola vez y correctamente para la inserción.
    ingredients_string = ', '.join(ingredients_list)

    # --- Sección para mostrar información nutricional de las frutas ---
    st.subheader("Información Nutricional de los Ingredientes:") # Traducido al español
    for fruit_chosen in ingredients_list:
        st.write(f"**{fruit_chosen}**") # Muestra el nombre de la fruta

        # Obtener el valor de SEARCH_ON para la fruta elegida
        # Asegúrate de que 'pd_df' contenga la columna 'SEARCH_ON' y 'FRUIT_NAME'.
        try:
            search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        except IndexError:
            st.warning(f"No se encontró el valor SEARCH_ON para '{fruit_chosen}'.")
            search_on = fruit_chosen.lower() # Fallback a fruit_chosen en minúsculas

        # CORRECCIÓN: Usar la URL base correcta (my.smoothiefroot.com) y el valor 'search_on'.
        # Se añadió manejo de errores para la llamada a la API.
        api_url = f"https://my.smoothiefroot.com/api/fruit/{search_on}"
        
        try:
            smoothiefroot_response = requests.get(api_url)
            
            if smoothiefroot_response.status_code == 200:
                try:
                    nutrition_data = smoothiefroot_response.json()
                    st.dataframe(data=nutrition_data, use_container_width=True)
                except requests.exceptions.JSONDecodeError:
                    st.warning(f"No se pudo decodificar la respuesta JSON para {fruit_chosen}. La API podría no estar devolviendo JSON válido.")
                    st.text(smoothiefroot_response.text) # Muestra la respuesta cruda para depuración
            else:
                st.warning(f"Error al obtener datos nutricionales para {fruit_chosen}: Código de estado {smoothiefroot_response.status_code}. URL: {api_url}")
                st.text(smoothiefroot_response.text) # Muestra la respuesta cruda para depuración
        except requests.exceptions.RequestException as e:
            st.error(f"Error de conexión al intentar obtener datos nutricionales para {fruit_chosen}: {e}. Verifica la URL de la API y tu conexión a internet.")
        st.markdown("---") # Separador para cada fruta
    # --- Fin de la sección de información nutricional ---

    # 📤 Crear el statement SQL de inserción
    # CORRECCIÓN: Movido fuera del bucle de visualización de ingredientes.
    # Esto asegura que la sentencia SQL se cree una sola vez con todos los ingredientes.
    my_insert_stmt = f"""
        insert into smoothies.public.orders (ingredients, name_on_order)
        values ('{ingredients_string}', '{name_on_order}')
    """

    # ⏩ Botón para enviar pedido
    time_to_insert = st.button('Enviar Pedido') # Traducido al español

    if time_to_insert:
        try:
            session.sql(my_insert_stmt).collect()
            st.success("¡Tu Batido ha sido ordenado, " + name_on_order + "!") # Traducido al español
        except Exception as e:
            st.error(f"Error al enviar el pedido: {e}. Por favor, inténtalo de nuevo.") # Traducido al español
else:
    st.info("Por favor, selecciona al menos un ingrediente para tu batido.") # Traducido al español

