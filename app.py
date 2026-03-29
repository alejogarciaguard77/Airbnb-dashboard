import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")

st.title("AIRBNB HOMEWORK - ALEJO GARCÍA GUARDIOLA 2E8")

df = pd.read_csv("airbnb.csv")

# ── SIDEBAR FILTERS ──────────────────────────────────────────────────────────
st.sidebar.header("Filters")

neighbourhoods = st.sidebar.multiselect(
    "Neighbourhood",
    options=df["neighbourhood_group"].dropna().unique(),
    default=df["neighbourhood_group"].dropna().unique()
)

room_types = st.sidebar.multiselect(
    "Room type",
    options=df["room_type"].dropna().unique(),
    default=df["room_type"].dropna().unique()
)

price_range = st.sidebar.slider(
    "Price range (€/night)",
    min_value=int(df["price"].dropna().min()),
    max_value=int(df["price"].dropna().quantile(0.99)),
    value=(int(df["price"].dropna().min()), int(df["price"].dropna().quantile(0.99)))
)


# ── APPLY FILTERS ────────────────────────────────────────────────────────────
filtered_df = df[
    (df["neighbourhood_group"].isin(neighbourhoods)) &
    (df["room_type"].isin(room_types)) &
    (df["price"] >= price_range[0]) &
    (df["price"] <= price_range[1])
]

# ── TABS ─────────────────────────────────────────────────────────────────────
tab1, tab2 = st.tabs(["Listings and Prices", "Reviews"])

# ── TAB 1 ────────────────────────────────────────────────────────────────────
with tab1:

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Room type vs minimum nights")
        fig1 = px.bar(
            filtered_df.groupby("room_type")["minimum_nights"].median().reset_index(),
            x="room_type",
            y="minimum_nights",
            labels={"room_type": "Room type", "minimum_nights": "Median minimum nights"}
        )
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        st.subheader("Price by room type")
        fig2 = px.box(
            filtered_df,
            x="room_type",
            y="price",
            labels={"room_type": "Room type", "price": "Price (€/night)"}
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Average price per neighbourhood")
    fig3 = px.bar(
        filtered_df.groupby("neighbourhood_group")["price"].mean().reset_index().sort_values("price", ascending=False),
        x="neighbourhood_group",
        y="price",
        labels={"neighbourhood_group": "Neighbourhood", "price": "Avg price (€/night)"}
    )
    st.plotly_chart(fig3, use_container_width=True)

# ── TAB 2 ────────────────────────────────────────────────────────────────────
with tab2:

    col3, col4 = st.columns(2)

    with col3:
        st.subheader("Top 15 listings by reviews per month")
        top = (
            filtered_df[["name", "reviews_per_month", "neighbourhood_group"]]
            .dropna()
            .sort_values("reviews_per_month", ascending=False)
            .head(15)
        )
        fig4 = px.bar(
            top,
            x="reviews_per_month",
            y="name",
            color="neighbourhood_group",
            orientation="h",
            labels={"reviews_per_month": "Reviews per month", "name": "Listing", "neighbourhood_group": "Neighbourhood"}
        )
        st.plotly_chart(fig4, use_container_width=True)

    with col4:
        st.subheader("Price vs number of reviews")
        fig5 = px.scatter(
            filtered_df.dropna(subset=["price", "number_of_reviews"]),
            x="number_of_reviews",
            y="price",
            color="room_type",
            labels={"number_of_reviews": "Number of reviews", "price": "Price (€/night)", "room_type": "Room type"}
        )
        st.plotly_chart(fig5, use_container_width=True)

    st.subheader("Average reviews per month by neighbourhood")
    fig6 = px.bar(
        filtered_df.groupby("neighbourhood_group")["reviews_per_month"].mean().reset_index().sort_values("reviews_per_month", ascending=False),
        x="neighbourhood_group",
        y="reviews_per_month",
        labels={"neighbourhood_group": "Neighbourhood", "reviews_per_month": "Avg reviews/month"}
    )
    st.plotly_chart(fig6, use_container_width=True)

# ── PRICE SIMULATOR ──────────────────────────────────────────────────────────
st.subheader("Price simulator")

sim_col1, sim_col2 = st.columns(2)

with sim_col1:
    sim_neighbourhood = st.selectbox("Neighbourhood", options=sorted(df["neighbourhood_group"].dropna().unique()))
    sim_room_type = st.selectbox("Room type", options=sorted(df["room_type"].dropna().unique()))

if st.button("Get price recommendation"):
    similar = df[
        (df["neighbourhood_group"] == sim_neighbourhood) &
        (df["room_type"] == sim_room_type)
    ]["price"].dropna()

    if len(similar) == 0:
        st.warning("No data found for this combination.")
    else:
        r1, r2, r3 = st.columns(3)
        r1.metric("Budget (25th percentile)", f"€{similar.quantile(0.25):.0f}/night")
        r2.metric("Recommended (median)",     f"€{similar.median():.0f}/night")
        r3.metric("Premium (75th percentile)",f"€{similar.quantile(0.75):.0f}/night")
