# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests

# Write directly to the app
st.title("My Parents New Healthy Diner")
st.write(
    """
    Breakfast menu
    """
)
#option = st.selectbox('How can we contact you?',('E-mail','Landline','Mobile'))
#st.write('Contact method:',option)

#Get the name
name_on_order = st.text_input('Name on the Smoothie:')
st.write('This smoothie is for ', name_on_order)

cnx = st.connection("snowflake")
session = cnx.session()
#session = get_active_session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'),col('SEARCH_ON'))

#st.dataframe(data=my_dataframe, use_container_width=True)
#st.stop

#Panda time
panda_df = my_dataframe.to_pandas()
#st.dataframe(data=panda_df, use_container_width=True)
#st.stop

ingredients_list = st.multiselect('Select up to 5 ingredients',my_dataframe, max_selections=5)

if ingredients_list:
    #st.write(ingredients_list)
    #st.text(ingredients_list)

    ingredients_string=''

    for fruit_chosen in ingredients_list:
        ingredients_string+=fruit_chosen+","

        search_on=panda_df.loc[panda_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write('The search value for ', fruit_chosen,' is ', search_on, '.')

        st.subheader(fruit_chosen +' - Nutrition information')
        fruityvice_response = requests.get("https://fruityvice.com/api/fruit/"+search_on)
        fv_df=st.dataframe(data=fruityvice_response.json(),use_container_width=True)

    
    st.write(ingredients_string)

    my_insert_stmt = """ insert into smoothies.public.orders(ingredients, name_on_order)
                        values ('""" + ingredients_string + """'
                                ,'"""+name_on_order+"""'
                                )
                    """
    st.write(my_insert_stmt)
    #st.stop

    
    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!', icon="✅")


