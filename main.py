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

    print("Allowed location:", allowed_location)
    if not is_within_radius(allowed_location=allowed_location, radius=2):
        st.warning("You are not authenticated to use this app.")
    else:
        # Get URL query parameters
        query_params = st.query_params.to_dict()
        # If the 'station' parameter is provided, use it to filter which station's form to show.
        selected_station = query_params.get('station', None)

        # st.write(selected_station)
        # http://localhost:8501/?station=Team%20Construction
        print(selected_station)

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

        df = pd.DataFrame(parse_response(res))
        print(df)
        if selected_station:
            # st.write(f"### Data for station: {selected_station}")
            # st.write(df)
            print("DB ID")
            print(os.getenv('Notion_DB_ID_REQUESTS'))
            create_dynamic_form(df, station=selected_station, notion_adapter=adapter, database_id=os.getenv('Notion_DB_ID_REQUESTS'))
        else:
            st.warning("You have to use a parameterised url")


#TODO: Send warning of how many things still be ordered
#TODO: Authenticate via location
#TODO: Add that people can order multiple items at the same time