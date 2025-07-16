# 🐍 Importar paquetes de Python
import streamlit as st
import requests
import pandas as pd
from snowflake.snowpark.functions import col

# 🖥️ Mostrar título y subtítulo
@@ -20,9 +21,16 @@
session = cnx.session()

# Seleccionar solo la columna con los nombres de frutas
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'),col('SEARCH_ON'))
#st.dataframe(data=my_dataframe, use_container_width=True)
#st.stop()
#fruit_options = my_dataframe.to_pandas()["FRUIT_NAME"].tolist()  # Convertir a lista de strings

# Convert the Snowpark Dataframe to a Pandas Dataframe so we can use the LOC function
pd_df=my_dataframe.to_pandas()
#st.dataframe(pd_df)
#st.stop()

# 🧃 Selección de ingredientes con límite de 5 frutas
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    ingredients_string = ''
    
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

        search_on=pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        #st.write('The search value for ', fruit_chosen, ' is ', search_on, '.')

        st.subheader(fruit_chosen + ' Nutrition Information')
        smoothiefroot_response = requests.get("https://fruityvice.com/api/fruit/" + fruit_chosen + search_on)
        sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
