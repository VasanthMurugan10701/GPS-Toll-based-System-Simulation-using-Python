# defining locations for start and end points
locations_coords = {"CHENNAI": (28.9845, 77.7064), "BANGALORE": (27.4924, 77.6737), "SALEM": (28.4595, 77.0266), "KOVAI": (27.1767, 78.0081)}

# defining toll zones
from shapely.geometry import Polygon
toll_zones = {"Toll Zone 1": Polygon([(77.5, 28.9), (78.0, 28.9), (78.0, 28.7), (77.5, 28.7)]), "Toll Zone 2": Polygon([(77.05, 28.0), (77.55, 28.0), (77.55, 27.75), (77.05, 27.75)]), "Toll Zone 3": Polygon([(77.2, 28.1), (77.5, 28.1), (77.5, 28.4), (77.2, 28.4)]), "Toll Zone 4": Polygon([(77.65, 27.85), (78.05, 27.85), (78.05, 28.25), (77.65, 28.25)])}

# function to calculate distance between two coordinates using the haversine formula
def calculate_distance(coords1, coords2):
    lat1, lon1 = coords1
    lat2, lon2 = coords2
    radius = 6371  # radius of the earth in km
    import math
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = radius * c
    return distance

# simulate vehicle movement
def simulate_vehicle_movement(start_loc, end_loc):
    start_coords = locations_coords[start_loc]
    end_coords = locations_coords[end_loc]
    distance = calculate_distance(start_coords, end_coords)
    from shapely.geometry import LineString
    route = LineString([(start_coords[1], start_coords[0]), (end_coords[1], end_coords[0])])
    toll_zones_passed = []
    toll_zone_distances = []
    for zone, gdf in toll_zones.items():
        if route.intersects(gdf):
            intersection = route.intersection(gdf)
            toll_zones_passed.append(zone)
            toll_zone_distances.append(intersection.length * 111.32)  # conversion of degrees to km
    return distance, toll_zones_passed, toll_zone_distances

# function to calculate toll
def calculate_toll(vehicle_type, toll_zones_passed, toll_zone_distances, price_per_km):
    zone_details = []
    total_toll = 0
    for zone, dist in zip(toll_zones_passed, toll_zone_distances):
        if zone == "Toll Zone 1":
            dynamic_amount = price_per_km * dist * 1.55
            total_toll += dynamic_amount
            zone_details.append((zone, dist, dynamic_amount))
        elif zone == "Toll Zone 2":
            dynamic_amount = price_per_km * dist * 1.25
            total_toll += dynamic_amount
            zone_details.append((zone, dist, dynamic_amount))
        elif zone == "Toll Zone 3":
            dynamic_amount = price_per_km * dist * 1.35
            total_toll += dynamic_amount
            zone_details.append((zone, dist, dynamic_amount))
        else:
            dynamic_amount = price_per_km * dist * 1.45
            total_toll += dynamic_amount
            zone_details.append((zone, dist, dynamic_amount))
    return total_toll, zone_details

# initialize streamlit
import streamlit as st
st.title("GPS Toll based System simulation")

start_loc = st.selectbox("Select Start Location", list(locations_coords.keys()))
end_loc = st.selectbox("Select End Location", list(locations_coords.keys()))

vehicle_type_list = ["Car", "Truck", "SUV", "Ambulance"]
vehicle_type = st.selectbox("Select Vehicle Type", vehicle_type_list)

# dynamic pricing
st.subheader("Dynamic Pricing according to congestion levels by location")

# different congestion levels for different locations
import random
location_congestion_levels = {"Meerut": random.uniform(0, 1), "Mathura": random.uniform(0, 1), "Gurugram": random.uniform(0, 1), "Agra": random.uniform(0, 1)}

if start_loc == end_loc:
    congestion_level = 0
    vehicles_on_road = 0
    vehicle_speeds = {"Section 1": 0, "Section 2": 0, "Section 3": 0}
    vehicle_status = "None"
    total_toll = 0
    penalty_amount = 0
else:
    congestion_level = 10+location_congestion_levels[start_loc]
    vehicles_on_road = round((congestion_level-10) * 500, 0)
    vehicle_speeds = {"Section 1": random.uniform(50, 120), "Section 2": random.uniform(50, 120), "Section 3": random.uniform(50, 120)}

for loc, level in location_congestion_levels.items():
    st.write(f"{loc}: {level * 100:.2f}%")
if vehicle_type == "Car":
    price_per_km = congestion_level * 0.25
elif vehicle_type == "Truck":
    price_per_km = congestion_level * 0.50
elif vehicle_type == "SUV":
    price_per_km = congestion_level * 0.35
else:
    price_per_km = congestion_level * 0.00

st.write("Dynamic Pricing Factor according to congestion level in ", start_loc, f": {price_per_km:.2f} INR/km")
st.write("Number of vehicles on the road in ", start_loc, f"at the moment: {vehicles_on_road}")

st.subheader("Speed Limit Checks")

# speed limits for different sections based on vehicle type
speed_limits = {"Car": {"Section 1": 80, "Section 2": 100, "Section 3": 120}, "SUV": {"Section 1": 90, "Section 2": 110, "Section 3": 120}, "Truck": {"Section 1": 70, "Section 2": 80, "Section 3": 90}, "Ambulance": {"Section 1": float("inf"), "Section 2": float("inf"), "Section 3": float("inf")}}

sections = speed_limits.get(vehicle_type, {}) # displaying speed limits according to selected vehicle 
for section, speed_limit in sections.items():
    if vehicle_type == "Ambulance":
        st.write(f"{section}: No Speed Limit")
    else:
        st.write(f"{section}: {speed_limit} km/h")

st.subheader("Vehicle Speed")
for section, speed in vehicle_speeds.items():
    st.write(f"{section}: {speed:.2f} km/h") # displaying speeds of vehicle in different sections 

# check if the vehicle is over the speed limit and impose penalties
if start_loc != end_loc:
    penalty_amount = 0
    for section, speed_limit in sections.items():
        if vehicle_speeds[section] > speed_limit:
            st.warning(f"Speeding! Vehicle is over the speed limit in {section}")
            if vehicle_type != "Ambulance":
                penalty_amount += 500
        else:
            st.success(f"Vehicle is within the speed limit in {section}")
else:
    penalty_amount = 0

# display toll query information
st.subheader("Toll Query")
st.subheader(f"From {start_loc} to {end_loc}")

# calculate distance and simulate vehicle movement
distance, toll_zones_passed, toll_zone_distances = simulate_vehicle_movement(start_loc, end_loc)

if toll_zones_passed:
    total_toll, zone_details = calculate_toll(vehicle_type, toll_zones_passed, toll_zone_distances, price_per_km)
else:
    total_toll, zone_details = (0, [])

toll_waiver=0
if zone_details:
    for zone, dist, amount in zone_details:
        payment_vendors = ["Vendor A", "Vendor B", "Vendor C"]
        st.subheader(f"Payment Vendors for {zone}")
        selected_vendor = st.selectbox(f"Select Payment Vendor for {zone}", payment_vendors)
        st.write(f"{zone}: Distance Travelled: {dist:.2f} km and Amount Deducted: {amount:.2f} INR")

        # display vehicle status
        vehicle_status = random.choice(["Moving", "Stationary"])
        if vehicle_type == "Ambulance":
            vehicle_status = "Moving"
        st.write(f"Vehicle Status: {vehicle_status}")
        if vehicle_status == "Stationary":
            toll_waiver+=150

# calculation of final toll amount
st.subheader("Final Amount Deducted")
st.write(f"Total Distance: {distance:.2f} km")
st.write(f"Total Toll: {total_toll:.2f} INR")
st.write(f"Penalty for Speeding: {penalty_amount:.2f} INR")
st.write(f"Toll Waiver Fee: {toll_waiver:.2f} INR")
final_toll_amount = total_toll + penalty_amount - toll_waiver
if final_toll_amount>=0:
    st.write(f"Final Toll Amount including penalties: {final_toll_amount:.2f} INR")
else:
    final_toll_amount=final_toll_amount*(-1)
    st.write(f"Amount to be credited: {final_toll_amount:.2f} INR")

# display the map
start_coords = locations_coords[start_loc]
end_coords = locations_coords[end_loc]
import folium
m = folium.Map(location=[(start_coords[0] + end_coords[0]) / 2, (start_coords[1] + end_coords[1]) / 2], zoom_start=7)
folium.Marker(location=start_coords, popup=start_loc, icon=folium.Icon(color="green")).add_to(m)
folium.Marker(location=end_coords, popup=end_loc, icon=folium.Icon(color="red")).add_to(m)
folium.PolyLine(locations=[start_coords, end_coords], color="blue").add_to(m)

for zone, coords in toll_zones.items():
    folium.GeoJson(coords, name=zone).add_to(m)
    zone_center = [coords.bounds[1] + (coords.bounds[3] - coords.bounds[1]) / 2,coords.bounds[0] + (coords.bounds[2] - coords.bounds[0]) / 2]
    folium.Marker(location=zone_center, popup=zone, icon=folium.Icon()).add_to(m)

from folium.plugins import HeatMap
heatmap_data = [(coords[0], coords[1], location_congestion_levels[loc]) for loc, coords in locations_coords.items()]
HeatMap(heatmap_data).add_to(m)

from streamlit.components.v1 import html as st_html
st_html(m._repr_html_(), height=500)
