# 🐍 Importar paquetes de Python
import streamlit as st
import requests
from snowflake.snowpark.functions import col

# 🖥️ Mostrar título y subtítulo
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write(
    """
    **Choose the fruits you want in your custom Smoothie!**
    """
)
 
# 🧑‍💻 Entrada del nombre del cliente
name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be:', name_on_order)
 
# 📥 Conexión a Snowflake y carga de datos
cnx = st.connection("snowflake")
session = cnx.session()
 
# Seleccionar solo la columna con los nombres de frutas
my_dataframe = session.table("smoothies.public.fruit_options").select(col("FRUIT_NAME"))
fruit_options = my_dataframe.to_pandas()["FRUIT_NAME"].tolist()  # Convertir a lista de strings
 
# 🧃 Selección de ingredientes con límite de 5 frutas
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    fruit_options,
    max_selections=6  # ⛔️ Restringir máximo 5 selecciones
)
 
# 🔁 Formatear ingredientes seleccionados como string
if ingredients_list:
    ingredients_string = ''
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
        st.subheader(fruit_chosen + ' Nutrition Information')
        smoothiefroot_response = requests.get("https://my.fruityvice.com/api/fruit/" + fruit_chosen)
        sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)


 
    # 📤 Crear el statement SQL de inserción
    my_insert_stmt = """
        insert into smoothies.public.orders (ingredients, name_on_order)
        values ('""" + ingredients_string.strip() + """','""" + name_on_order + """')
    """
 
    # ⏩ Botón para enviar pedido
    time_to_insert = st.button('Submit Order')
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success("Your Smoothie is ordered, " + name_on_order + "!")

