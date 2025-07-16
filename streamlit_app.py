# 🐍 Importar paquetes necesarios
import streamlit as st
from snowflake.snowpark.functions import col, when_matched
 
# 🖥️ Título de la app
st.title(":cup_with_straw: Pending Smoothie Orders :cup_with_straw:")
st.write("Orders that need to be filled.")
 
# 🔗 Conectarse a la sesión activa de Snowflake
session = get_active_session()
 
# 📥 Traer pedidos no llenados
my_dataframe = session.table("smoothies.public.orders").filter(col("ORDER_FILLED") == 0)

cnx = st.connection("snowflake")
session = st. connection()

# ✅ Verificar si hay datos
if my_dataframe.count() > 0:
    # ✏️ Editor interactivo
    editable_df = st.data_editor(my_dataframe)
    submitted = st.button("Submit")
 
    if submitted:
        og_dataset = session.table("smoothies.public.orders")
        edited_dataset = session.create_dataframe(editable_df)
 
        try:
            # 🔁 MERGE para actualizar los pedidos
            og_dataset.merge(
                edited_dataset,
                og_dataset["ORDER_UID"] == edited_dataset["ORDER_UID"],
                [when_matched().update({"ORDER_FILLED": edited_dataset["ORDER_FILLED"]})]
            )
            # ✅ Mostrar mensaje solo si fue exitoso
            st.success("Order(s) updated! 👍", icon="✅")
        except:
            # ❌ Si falla, mostrar error
            st.error("Something went wrong while updating.", icon="⚠️")
 
else:
    # 💤 No hay pedidos pendientes
    st.success("There are no pending orders right now.", icon="👍")
