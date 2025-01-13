import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np  # For handling dynamic spacing in bar labels

# Title and description
st.title("Market Sizing Calculator with Custom and Predefined Inputs")
st.write("""
This interactive tool allows you to estimate the **Total Addressable Market (TAM)**, 
**Serviceable Available Market (SAM)**, and **Serviceable Obtainable Market (SOM)** 
using either predefined market assumptions or fully custom inputs. 
It also projects SOM growth over a specified number of years.
""")

# Choose assumption type
st.write("**Choose Market Assumption Type**")
col1, col2 = st.columns(2)

if "selected_type" not in st.session_state:
    st.session_state.selected_type = "predefined"

with col1:
    if st.button("Predefined Market Assumptions", key="predefined_button"):
        st.session_state.selected_type = "predefined"
with col2:
    if st.button("Custom Market Assumptions", key="custom_button"):
        st.session_state.selected_type = "custom"

use_predefined = st.session_state.selected_type == "predefined"
use_custom = st.session_state.selected_type == "custom"

# Population growth input
st.write("**Population Growth Assumptions**")
add_growth = st.checkbox("Project SOM with population growth?")
if add_growth:
    annual_growth_rate = st.number_input("Annual Growth Rate (%)", min_value=0.0, max_value=100.0, value=2.0, step=0.1)
    growth_years = st.number_input("Number of Years for Growth Projection", min_value=1, value=10, step=1)
else:
    annual_growth_rate = 0.0
    growth_years = 0

# Predefined Market Assumptions
if use_predefined:
    st.header("Predefined Market Assumptions")
    total_population = st.number_input("Total Population (e.g., total target audience size)", min_value=1, value=1000000, step=1000)
    adoption_rate = st.number_input("Adoption Rate (%)", min_value=0.0, max_value=100.0, value=20.0, step=0.1)
    serviceable_rate = st.number_input("Serviceable Market Rate (%)", min_value=0.0, max_value=100.0, value=50.0, step=0.1)
    conversion_rate = st.number_input("Conversion Rate (%)", min_value=0.0, max_value=100.0, value=10.0, step=0.1)
    arpu = st.number_input("Average Revenue Per User (ARPU) ($)", min_value=0.0, value=50.0, step=1.0)

    # Convert percentages to fractions
    adoption_rate /= 100
    serviceable_rate /= 100
    conversion_rate /= 100

    # Calculate TAM, SAM, SOM
    tam = total_population * arpu
    sam = tam * serviceable_rate
    som = sam * conversion_rate

    # Display results
    st.header("Market Size Results (Predefined Assumptions)")
    st.metric("Total Addressable Market (TAM)", f"${tam:,.2f}")
    st.metric("Serviceable Available Market (SAM)", f"${sam:,.2f}")
    st.metric("Serviceable Obtainable Market (SOM)", f"${som:,.2f}")

    # Prepare results for download
    predefined_results = pd.DataFrame({
        "Metric": ["TAM", "SAM", "SOM"],
        "Value ($)": [tam, sam, som]
    })
    predefined_csv = predefined_results.to_csv(index=False)

    # Download button for predefined results
    st.download_button(
        label="Download Predefined Results (CSV)",
        data=predefined_csv,
        file_name="predefined_market_size_results.csv",
        mime="text/csv",
    )

    # Apply population growth for projections
    if add_growth:
        som_projection = []
        for year in range(growth_years + 1):
            tam = total_population * arpu
            sam = tam * serviceable_rate
            som = sam * conversion_rate
            som_projection.append(som)

            # Update total population for the next year
            total_population *= (1 + annual_growth_rate / 100)

        # Plot SOM growth over time
        st.header("Projected SOM Growth Over Time (Predefined Assumptions)")
        fig, ax = plt.subplots()
        ax.plot(range(growth_years + 1), som_projection, marker="o", linestyle="--", color="#2ca02c")

        # Annotate each point with the SOM value
        for i, value in enumerate(som_projection):
            ax.annotate(f"${value:,.2f}", (i, value), textcoords="offset points", xytext=(0, 10), ha="center")

        ax.set_title("SOM Growth Over Time")
        ax.set_xlabel("Year")
        ax.set_ylabel("SOM ($)")
        ax.grid(visible=True, linestyle="--", alpha=0.5)
        st.pyplot(fig)

# Custom Market Assumptions
if use_custom:
    st.header("Create Your Own Market Assumptions")
    total_population = st.number_input("Total Population (Custom Assumptions)", min_value=1, value=1000000, step=1000)

    # Number of custom inputs (minimum 3)
    num_custom_inputs = st.number_input("Number of custom inputs to define", min_value=2, max_value=10, value=2, step=1)

    # Custom inputs section
    custom_inputs = []
    for i in range(num_custom_inputs):
        custom_title = st.text_input(f"Custom Input #{i + 1} Title", value=f"Input {i + 1}")
        custom_value = st.number_input(f"{custom_title} (%)", min_value=0.0, max_value=100.0, value=10.0, step=0.1)
        custom_inputs.append((custom_title, custom_value / 100))

    arpu = st.number_input("Average Revenue Per User (ARPU) (Custom Assumptions)", min_value=0.0, value=50.0, step=1.0)

    # Start with TAM
    tam = total_population * arpu
    adjusted_values = [tam]
    custom_labels = ["TAM"]

    # Apply custom inputs sequentially
    for title, percentage in custom_inputs:
        adjusted_values.append(adjusted_values[-1] * percentage)
        custom_labels.append(title)

    # Display results
    st.header("Market Size Results (Custom Assumptions)")
    for i, label in enumerate(custom_labels):
        st.metric(f"{label} Market Size", f"${adjusted_values[i]:,.2f}")

    # Prepare results for download
    custom_results = pd.DataFrame({
        "Metric": custom_labels,
        "Value ($)": adjusted_values
    })
    custom_csv = custom_results.to_csv(index=False)

    # Download button for custom results
    st.download_button(
        label="Download Custom Results (CSV)",
        data=custom_csv,
        file_name="custom_market_size_results.csv",
        mime="text/csv",
    )

    # Apply population growth to the final SOM
    if add_growth:
        som_projection = []
        for year in range(growth_years + 1):
            tam = total_population * arpu
            adjusted_values = [tam]
            for _, percentage in custom_inputs:
                adjusted_values.append(adjusted_values[-1] * percentage)
            som_projection.append(adjusted_values[-1])

            # Update total population for the next year
            total_population *= (1 + annual_growth_rate / 100)

        # Plot SOM growth over time
        st.header("Projected SOM Growth Over Time (Custom Assumptions)")
        fig, ax = plt.subplots()
        ax.plot(range(growth_years + 1), som_projection, marker="o", linestyle="--", color="#2ca02c")

        # Annotate each point with the SOM value
        for i, value in enumerate(som_projection):
            ax.annotate(f"${value:,.2f}", (i, value), textcoords="offset points", xytext=(0, 10), ha="center")

        ax.set_title("SOM Growth Over Time (Custom Assumptions)")
        ax.set_xlabel("Year")
        ax.set_ylabel("SOM ($)")
        ax.grid(visible=True, linestyle="--", alpha=0.5)
        st.pyplot(fig)

# Bar Chart for Market Size
st.header("Market Size Breakdown (Bar Chart)")
if use_predefined:
    sizes = [tam, sam, som]
    labels = ["TAM", "SAM", "SOM"]
else:
    sizes = adjusted_values
    labels = custom_labels

fig, ax = plt.subplots(figsize=(6, 6))  # Increased vertical height
bars = ax.bar(labels, sizes, color=["#4CAF50", "#FF9800", "#2196F3"])
ax.set_ylabel("Market Size ($)")
ax.set_title("Market Sizing Visualization")
ax.ticklabel_format(style="plain", axis="y")
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x:,.0f}"))
plt.xticks(rotation=45, ha="right")

# Add numbers on top of each bar dynamically
for bar in bars:
    height = bar.get_height()
    ax.annotate(f"${height:,.2f}",
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 5),
                textcoords="offset points",
                ha="center", va="bottom")

# Adjust y-axis limit to avoid text clipping
ax.set_ylim(0, max(sizes) * 1.3)  # Add 30% padding above the tallest bar
st.pyplot(fig)
