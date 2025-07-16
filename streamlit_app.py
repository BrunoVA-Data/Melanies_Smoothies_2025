# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests
import pandas as pd

# Write directly to the app
st.title(":cup_with_straw: Customize your Smoothie :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie:', name_on_order)

cnx = st.connection("snowflake")
# CORRECCIÓN: 'session' es un atributo de 'cnx', no un método.
# El error 'AttributeError: 'function' object has no attribute 'table'' se produce
# porque se intentaba llamar a 'session()' como una función, cuando es un objeto.
session = cnx.session 

my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))

#st.dataframe(data=my_dataframe, use_container_width=True)
#st.stop()

pd_df = my_dataframe.to_pandas()

#st.dataframe(pd_df)
#st.stop()

# Nota: La variable 'fruit_options' no está definida en este código,
# lo que probablemente causará un 'NameError' en la siguiente línea.
# Para solucionarlo, deberías definir 'fruit_options' a partir de 'pd_df' o 'my_dataframe'.
ingredients_list=st.multiselect('Choose up to 5 ingredients:', my_dataframe, max_selections=5)

if ingredients_list:
    #st.write(ingredients_list)
    #st.text(ingredients_list)
    ingredients_string =''
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

        search_on=pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        #st.write('The search value for ', fruit_chosen,' is ', search_on, '.')

        st.subheader(fruit_chosen + 'Nutrition Information')
        # Nota: La concatenación de URL aquí (fruit_chosen + search_on) es incorrecta para una URL de API.
        # Además, falta el manejo de errores para la respuesta de la API (status_code, JSONDecodeError).
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/" + fruit_chosen + search_on)
        sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)

    #st.write(ingredients_string)
    my_insert_stmt = """ insert into smoothies.public.orders(ingredients, name_on_order)
                values ('""" + ingredients_string + """','""" +name_on_order+ """')"""

    #st.write(my_insert_stmt)
    #st.stop()

    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success(f'Your Smoothie is ordered, {name_on_order}!', icon="✅")
