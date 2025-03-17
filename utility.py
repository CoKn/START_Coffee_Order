import streamlit as st
from streamlit_current_location import current_position
from geopy.distance import geodesic



def find_value_with_key(data, key):
    if isinstance(data, dict):
        if key in data:
            return data[key]
        for k, v in data.items():
            result = find_value_with_key(v, key)
            if result is not None:
                return result
    elif isinstance(data, list):
        for item in data:
            result = find_value_with_key(item, key)
            if result is not None:
                return result
    return None


@st.cache_data
def parse_response(response):
    rows = []

    for page in response['results']:
        props = page.get("properties", {})

        # Use the "Name" property to extract the station.
        name_prop = props.get("Name", {})
        station = ""
        if "title" in name_prop and len(name_prop["title"]) > 0:
            station = name_prop["title"][0].get("plain_text", "")

        # Extract current and max quantities
        current_quant = props.get("Current Quant", {}).get("number", None)
        max_quant = props.get("Max Quant", {}).get("number", None)

        # Extract inventory from the "Inventory" property; join IDs if available
        inventory_prop = find_value_with_key(data=props, key="array")
        inventory_name = ""
        if inventory_prop:
            inventory_name = combine_inventory_names(inventory_prop)

        inventory_relation_prop = props.get("Inventory", {}).get("relation", [])
        inventory_relation_id = inventory_relation_prop[0].get("id") if inventory_relation_prop else None

        rows.append({
            "Station": station,
            "Current Quant": current_quant,
            "Max Quant": max_quant,
            "Inventory": inventory_name,
            "Inventory_Relation_ID": inventory_relation_id
        })

    return rows


def combine_inventory_names(inventory_prop):
    return ", ".join(
        item.get("title", [{}])[0].get("plain_text", "")
        for item in inventory_prop
    )


def create_dynamic_form(df, station, notion_adapter, database_id):
    st.header(f"Order Form for {station}")

    # Extract unique inventory items
    inventory_items = [item for item in df['Inventory'].dropna().unique() if item]
    with st.container(border=True):
        selected_items = st.multiselect("What do you want to order?", inventory_items)

        with st.form(key='order_form', border=False):
            # Dictionary to store order quantities for each selected item
            order_quantities = {}
            for item in selected_items:
                order_quantities[item] = st.number_input(f"Order Quantity for {item}", min_value=0, step=1,
                                                         key=f"order_quantity_{item}")

            # Submit button
            if len(order_quantities.keys()) == 0:
                return
            submit_button = st.form_submit_button(label='Submit Order')

            if submit_button:
                for item, quantity in order_quantities.items():
                    relation_id = df.loc[df['Inventory'] == item, 'Inventory_Relation_ID'].values[0]
                    properties = {
                        "Name": {
                            "title": [
                                {
                                    "text": {
                                        "content": f"Order for {station} - {item}"
                                    }
                                }
                            ]
                        },
                        "Inventory": {
                            "relation": [
                                {
                                    "id": relation_id
                                }
                            ]
                        },
                        "Update Quantity": {
                            "number": quantity
                        }
                    }
                    response = notion_adapter.create_page(database_id=database_id, properties=properties)
                    if "error" in response:
                        st.error(f"Failed to create page for {item}: {response['error']}")
                    else:
                        st.success(f"Order placed for {quantity} units of {item}")


def is_within_radius(radius, allowed_location):
    current_location = current_position()
    print("Allowed location:", allowed_location)
    print("Current location:", current_location)
    distance = geodesic((current_location["latitude"], current_location["longitude"]),
                        (allowed_location["latitude"],
                         allowed_location["longitude"])
                        ).kilometers
    print("Distance:", distance)
    return distance <= radius
