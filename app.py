import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from data import get_bess_data

# Page Configuration
st.set_page_config(
    page_title="BESS Technology Dashboard",
    page_icon="🔋",
    layout="wide"
)

# Title and Introduction
st.title("🔋 BESS Technology Dashboard: Performance & Finance Outlook")
st.markdown("""
This dashboard provides a comparative analysis of Battery Energy Storage System (BESS) technologies.
It explores the current landscape and projects future trends over 3, 5, and 10-year horizons.
""")

# Load Data
@st.cache_data
def load_data():
    return get_bess_data()

try:
    df = load_data()

    # Sidebar Filters
    st.sidebar.header("Filters")

    # Technology filter
    all_technologies = df['Technology'].unique().tolist()
    selected_technologies = st.sidebar.multiselect(
        "Select Technologies",
        options=all_technologies,
        default=all_technologies
    )

    # Category filter
    all_categories = df['Category'].unique().tolist()
    selected_categories = st.sidebar.multiselect(
        "Select Categories",
        options=all_categories,
        default=all_categories
    )

    # Timeframe filter
    all_years = sorted(df['Year'].unique().tolist())
    selected_years = st.sidebar.multiselect(
        "Select Years",
        options=all_years,
        default=all_years
    )

    # Apply filters
    filtered_df = df[
        (df['Technology'].isin(selected_technologies)) &
        (df['Category'].isin(selected_categories)) &
        (df['Year'].isin(selected_years))
    ]

    if filtered_df.empty:
        st.warning("No data matches your filter selection. Please adjust filters.")
    else:
        # Key Metrics Summary (Current Year)
        st.header("📊 Current Technology Snapshot (2025)")
        current_df = filtered_df[filtered_df['Year'] == 2025]

        if not current_df.empty:
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                lowest_capex = current_df.loc[current_df['CAPEX ($/kWh)'].idxmin()]
                st.metric(
                    label="Lowest CAPEX",
                    value=f"${lowest_capex['CAPEX ($/kWh)']:.0f}/kWh",
                    delta=lowest_capex['Technology']
                )

            with col2:
                highest_eff = current_df.loc[current_df['Efficiency (%)'].idxmax()]
                st.metric(
                    label="Highest Efficiency",
                    value=f"{highest_eff['Efficiency (%)']:.1f}%",
                    delta=highest_eff['Technology']
                )

            with col3:
                longest_cycle = current_df.loc[current_df['Cycle Life'].idxmax()]
                st.metric(
                    label="Longest Cycle Life",
                    value=f"{longest_cycle['Cycle Life']:,}",
                    delta=longest_cycle['Technology']
                )

            with col4:
                lowest_lcos = current_df.loc[current_df['LCOS ($/MWh)'].idxmin()]
                st.metric(
                    label="Lowest LCOS",
                    value=f"${lowest_lcos['LCOS ($/MWh)']:.0f}/MWh",
                    delta=lowest_lcos['Technology']
                )

        st.divider()

        # CAPEX Comparison Chart
        st.header("💰 CAPEX Trends Over Time")

        fig_capex = px.line(
            filtered_df,
            x='Year',
            y='CAPEX ($/kWh)',
            color='Technology',
            markers=True,
            title="CAPEX Projection by Technology ($/kWh)"
        )
        fig_capex.update_layout(
            xaxis_title="Year",
            yaxis_title="CAPEX ($/kWh)",
            legend_title="Technology",
            hovermode="x unified"
        )
        st.plotly_chart(fig_capex, use_container_width=True)

        # Two column layout for Efficiency and Cycle Life
        col_left, col_right = st.columns(2)

        with col_left:
            st.header("⚡ Efficiency Comparison")
            fig_eff = px.bar(
                filtered_df,
                x='Technology',
                y='Efficiency (%)',
                color='Year',
                barmode='group',
                title="Round-Trip Efficiency by Technology (%)"
            )
            fig_eff.update_layout(
                xaxis_title="Technology",
                yaxis_title="Efficiency (%)",
                xaxis_tickangle=-45
            )
            st.plotly_chart(fig_eff, use_container_width=True)

        with col_right:
            st.header("🔄 Cycle Life Comparison")
            fig_cycles = px.bar(
                filtered_df,
                x='Technology',
                y='Cycle Life',
                color='Year',
                barmode='group',
                title="Cycle Life by Technology"
            )
            fig_cycles.update_layout(
                xaxis_title="Technology",
                yaxis_title="Cycle Life (cycles)",
                xaxis_tickangle=-45
            )
            st.plotly_chart(fig_cycles, use_container_width=True)

        st.divider()

        # LCOS Analysis
        st.header("📈 Levelized Cost of Storage (LCOS)")

        fig_lcos = px.line(
            filtered_df,
            x='Year',
            y='LCOS ($/MWh)',
            color='Technology',
            markers=True,
            title="LCOS Projection by Technology ($/MWh)"
        )
        fig_lcos.update_layout(
            xaxis_title="Year",
            yaxis_title="LCOS ($/MWh)",
            legend_title="Technology",
            hovermode="x unified"
        )
        st.plotly_chart(fig_lcos, use_container_width=True)

        # Energy Density Comparison
        st.header("🔋 Energy Density Comparison")

        current_year_data = filtered_df[filtered_df['Year'] == 2025]
        future_year_data = filtered_df[filtered_df['Year'] == 2035]

        if not current_year_data.empty:
            fig_density = go.Figure()

            fig_density.add_trace(go.Bar(
                name='2025',
                x=current_year_data['Technology'],
                y=current_year_data['Energy Density (Wh/L)'],
                marker_color='steelblue'
            ))

            if not future_year_data.empty:
                fig_density.add_trace(go.Bar(
                    name='2035',
                    x=future_year_data['Technology'],
                    y=future_year_data['Energy Density (Wh/L)'],
                    marker_color='coral'
                ))

            fig_density.update_layout(
                title="Energy Density Comparison: Current vs 10-Year Projection",
                xaxis_title="Technology",
                yaxis_title="Energy Density (Wh/L)",
                barmode='group',
                xaxis_tickangle=-45
            )
            st.plotly_chart(fig_density, use_container_width=True)

        st.divider()

        # Technology Radar/Spider Chart for Current Year
        st.header("🎯 Technology Profile Comparison (2025)")

        if not current_df.empty:
            # Normalize metrics for radar chart
            radar_df = current_df.copy()

            # Invert CAPEX and LCOS (lower is better)
            radar_df['CAPEX Score'] = 1 - (radar_df['CAPEX ($/kWh)'] - radar_df['CAPEX ($/kWh)'].min()) / (radar_df['CAPEX ($/kWh)'].max() - radar_df['CAPEX ($/kWh)'].min() + 0.01)
            radar_df['LCOS Score'] = 1 - (radar_df['LCOS ($/MWh)'] - radar_df['LCOS ($/MWh)'].min()) / (radar_df['LCOS ($/MWh)'].max() - radar_df['LCOS ($/MWh)'].min() + 0.01)
            radar_df['Efficiency Score'] = (radar_df['Efficiency (%)'] - radar_df['Efficiency (%)'].min()) / (radar_df['Efficiency (%)'].max() - radar_df['Efficiency (%)'].min() + 0.01)
            radar_df['Cycle Score'] = (radar_df['Cycle Life'] - radar_df['Cycle Life'].min()) / (radar_df['Cycle Life'].max() - radar_df['Cycle Life'].min() + 0.01)
            radar_df['Density Score'] = (radar_df['Energy Density (Wh/L)'] - radar_df['Energy Density (Wh/L)'].min()) / (radar_df['Energy Density (Wh/L)'].max() - radar_df['Energy Density (Wh/L)'].min() + 0.01)

            categories = ['CAPEX Score', 'Efficiency Score', 'Cycle Score', 'Density Score', 'LCOS Score']

            fig_radar = go.Figure()

            for _, row in radar_df.iterrows():
                fig_radar.add_trace(go.Scatterpolar(
                    r=[row['CAPEX Score'], row['Efficiency Score'], row['Cycle Score'], row['Density Score'], row['LCOS Score']],
                    theta=['Cost', 'Efficiency', 'Cycle Life', 'Energy Density', 'LCOS'],
                    fill='toself',
                    name=row['Technology']
                ))

            fig_radar.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True, range=[0, 1])
                ),
                showlegend=True,
                title="Normalized Technology Comparison (Higher = Better)"
            )
            st.plotly_chart(fig_radar, use_container_width=True)

        # Raw Data Preview
        with st.expander("📋 View Raw Data"):
            st.dataframe(filtered_df, use_container_width=True)

            # Download button
            csv = filtered_df.to_csv(index=False)
            st.download_button(
                label="Download as CSV",
                data=csv,
                file_name="bess_technology_data.csv",
                mime="text/csv"
            )

except Exception as e:
    st.error(f"Error loading data: {e}")
    st.exception(e)

# Footer
st.sidebar.divider()
st.sidebar.markdown("---")
st.sidebar.caption("Data based on industry trends (NREL, BNEF) - For demonstration purposes")
