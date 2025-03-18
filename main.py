import streamlit as st
import os
import pandas as pd
from notion import NotionAdapter
from utility import parse_response, create_dynamic_form, is_within_radius
from dotenv import load_dotenv


if __name__ == "__main__":
    load_dotenv()

    allowed_location = {"latitude": float(os.getenv("ALLOWED_LOCATION_LAT")),
                        "longitude": float(os.getenv("ALLOWED_LOCATION_LONG"))}

    query_params = st.query_params.to_dict()

    selected_station = query_params.get('station', None)
    location = {"latitude": query_params.get('lat', None), "longitude": query_params.get('log', None)}

    if not location["latitude"] or not location["longitude"]:
        st.warning("You are not authenticated to use this app.")

    if not is_within_radius(allowed_location=allowed_location, current_location=location, radius=2):
        st.warning("You are not authenticated to use this app.")

    else:
        if selected_station:
            filter_ = {
                "filter": {
                    "property": "Name",
                    "title": {
                        "equals": selected_station
                    }
                }
            }
        else:
            filter_ = {}

        adapter = NotionAdapter()
        res = adapter.query(database_id=os.getenv('Notion_DB_ID_STATIONS'), filter=filter_)

        print(res)

        df = pd.DataFrame(parse_response(res))
        print(df)
        if selected_station:
            create_dynamic_form(df, station=selected_station, notion_adapter=adapter, database_id=os.getenv('Notion_DB_ID_REQUESTS'))
        else:
            st.warning("You have to use a parameterised url")


#TODO: Send warning of how many things still be ordered
#TODO: Send Event Station relation with Request