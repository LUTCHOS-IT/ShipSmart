import streamlit as st
import matplotlib.pyplot as plt

# Calculation Functions
def calculate_volume(length, width, height):
    """Calculate the volume of an item in liters based on dimensions in cm."""
    return length * width * height / 1000  # Convert cm³ to liters

def get_lvb_size_category(volume):
    """Determine the LVB size category based on volume in liters."""
    if volume <= 1:
        return "Small"
    elif volume <= 5:
        return "Medium"
    elif volume <= 10:
        return "Large"
    else:
        return None  # Item is too large for LVB

def get_lvb_cost(size_category, sales_price, destination, is_special, use_labeling):
    """Calculate LVB shipping costs (per article and per shipment) based on inputs."""
    base_costs = {
        "Small": {"NL": {"per_artikel": 1.0, "per_verzending": 3.0}, "BE": {"per_artikel": 1.0, "per_verzending": 4.0}},
        "Medium": {"NL": {"per_artikel": 1.5, "per_verzending": 4.0}, "BE": {"per_artikel": 1.5, "per_verzending": 5.0}},
        "Large": {"NL": {"per_artikel": 2.0, "per_verzending": 5.0}, "BE": {"per_artikel": 2.0, "per_verzending": 6.0}},
    }
    if size_category is None:
        return None, None
    costs = base_costs[size_category][destination]
    per_artikel = costs["per_artikel"]
    per_verzending = costs["per_verzending"]
    if is_special:
        per_artikel += 0.5  # Additional fee for special category
    if use_labeling:
        per_artikel += 0.2  # Additional fee for labeling
    return per_artikel, per_verzending

def calculate_vvb_cost(length, width, height, weight, destination):
    """Calculate VVB shipping cost based on dimensions, weight, and destination."""
    volume = calculate_volume(length, width, height)
    if destination == "NL":
        return 5.0 + 0.1 * volume + 0.5 * weight  # Base cost + volume and weight factors
    else:  # BE
        return 6.0 + 0.15 * volume + 0.6 * weight

# Streamlit App
st.title("Shipping Cost Calculator")
st.markdown("Enter your item details below to compare shipping costs between LVB (Logistics via Bol.com) and VVB (Own Shipping).")

# Number of Items
num_items = st.number_input("Number of Items", min_value=1, max_value=10, value=1, step=1)

# Item Inputs
items = []
for i in range(num_items):
    st.subheader(f"Item {i + 1}")
    length = st.number_input(f"Length (cm)", min_value=0.0, value=10.0, key=f"length_{i}")
    width = st.number_input(f"Width (cm)", min_value=0.0, value=10.0, key=f"width_{i}")
    height = st.number_input(f"Height (cm)", min_value=0.0, value=10.0, key=f"height_{i}")
    weight = st.number_input(f"Weight (kg)", min_value=0.0, value=1.0, key=f"weight_{i}")
    price = st.number_input(f"Sales Price (€)", min_value=0.0, value=20.0, key=f"price_{i}")
    special = st.checkbox(f"Special Category (e.g., fragile)", value=False, key=f"special_{i}")
    items.append({
        "length": length,
        "width": width,
        "height": height,
        "weight": weight,
        "price": price,
        "special": special
    })

# Destination Selection
destination = st.radio("Destination", ["NL", "BE"], index=0)

# Labeling Option
use_labeling = st.checkbox("Use Labeling", value=False)

# VVB Shipping Options (for multiple items)
if num_items > 1:
    vvb_option = st.radio("VVB Shipping Option", ["separate", "together"], index=0)
    if vvb_option == "together":
        st.subheader("Total Package Dimensions for VVB (Together)")
        total_length = st.number_input("Total Length (cm)", min_value=0.0, value=20.0)
        total_width = st.number_input("Total Width (cm)", min_value=0.0, value=20.0)
        total_height = st.number_input("Total Height (cm)", min_value=0.0, value=20.0)
        total_weight = st.number_input("Total Weight (kg)", min_value=0.0, value=2.0)
else:
    vvb_option = "together"  # Single item uses its own dimensions

# Calculate Button
if st.button("Calculate"):
    # LVB Cost Calculation
    total_per_artikel = 0
    max_per_verzending = 0
    for item in items:
        volume = calculate_volume(item["length"], item["width"], item["height"])
        size_category = get_lvb_size_category(volume)
        if size_category is None:
            st.error(f"Item {items.index(item) + 1} is too large for LVB shipping (volume > 10L).")
            st.stop()
        per_artikel, per_verzending = get_lvb_cost(size_category, item["price"], destination, item["special"], use_labeling)
        total_per_artikel += per_artikel
        max_per_verzending = max(max_per_verzending, per_verzending)
    lvb_cost = total_per_artikel + max_per_verzending

    # VVB Cost Calculation
    if num_items == 1:
        vvb_cost = calculate_vvb_cost(items[0]["length"], items[0]["width"], items[0]["height"], items[0]["weight"], destination)
        vvb_label = "VVB"
    elif vvb_option == "separate":
        vvb_cost = sum(calculate_vvb_cost(item["length"], item["width"], item["height"], item["weight"], destination) for item in items)
        vvb_label = "VVB (Separate)"
    else:  # vvb_option == "together"
        vvb_cost = calculate_vvb_cost(total_length, total_width, total_height, total_weight, destination)
        vvb_label = "VVB (Together)"

    # Determine Cheaper Option
    cheaper_option = "LVB" if lvb_cost < vvb_cost else vvb_label

    # Display Results
    st.markdown("### Shipping Cost Results")
    st.write(f"**LVB Total Cost:** €{lvb_cost:.2f}")
    st.write(f"**{vvb_label} Total Cost:** €{vvb_cost:.2f}")
    st.success(f"**Cheaper Option:** {cheaper_option}")

    # Cost Comparison Bar Chart
    fig, ax = plt.subplots()
    ax.bar(["LVB", vvb_label], [lvb_cost, vvb_cost], color=["blue", "green"])
    ax.set_ylabel("Cost (€)")
    ax.set_title("Shipping Cost Comparison")
    st.pyplot(fig)
