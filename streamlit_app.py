# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
from snowflake.snowpark import Session
import requests


# Write directly to the app
st.title(f":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write(
  """Choose the fruits you want in your custom Smoothie!
  """
)
# Set up the Snowflake session using secrets
connection_parameters = {
    "account": st.secrets["snowflake"]["account"],
    "user": st.secrets["snowflake"]["user"],
    "password": st.secrets["snowflake"]["password"],
    "role": st.secrets["snowflake"]["role"],
    "warehouse": st.secrets["snowflake"]["warehouse"],
    "database": st.secrets["snowflake"]["database"],
    "schema": st.secrets["snowflake"]["schema"]
}

session = Session.builder.configs(connection_parameters).create()

myname = st.text_input('Please provide your name below:')
st.write(f'"{myname}" will be displayed on your order')

my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'),col('SEARCH_ON'))
                                                                      
#st.dataframe(data=my_dataframe, use_container_width=True)
#st.stop()

#Converting DF to pandas DF

pd_df = my_dataframe.to_pandas()
#st.dataframe(pd_df)
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients: ',
    my_dataframe,max_selections= 5
)
if ingredients_list:
    
    ingredients_string = ''

    for i in ingredients_list:
        ingredients_string += i+' '

        search_on=pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write('The search value for ', i,' is ', search_on, '.')
        st.subheader(i+ ' Nutrition information')
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/" + i)
        st.df = st.dataframe(data=smoothiefroot_response.json(),use_container_width=True)
    #st.write(ingredients_string)

    my_insert_stmt = """ insert into smoothies.public.orders(ingredients,name_on_order)
            values ('""" + ingredients_string + """','"""+ myname +"""')"""
   
    

    time_to_insert = st.button('Submit Order')
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success(f'Your Smoothie is ordered, {myname}!', icon="✅")
