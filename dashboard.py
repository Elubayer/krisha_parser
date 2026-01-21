import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

# ================== НАСТРОЙКИ СТРАНИЦЫ ==================
st.set_page_config(
    page_title="Krisha.kz — Аналитика квартир",
    layout="wide"
)

# ================== ЗАГРУЗКА И ОЧИСТКА ДАННЫХ ==================
@st.cache_data
def load_data():
    df = pd.read_csv("results.csv", sep=";", encoding="utf-8-sig")

    # ---- Цена ----
    df["price"] = (
        df["price"]
        .astype(str)
        .str.replace(" ", "")
        .str.replace(",", "")
    )
    df["price"] = pd.to_numeric(df["price"], errors="coerce")

    # ---- Площадь ----
    df["square_m2"] = (
        df["square_m2"]
        .astype(str)
        .str.replace(",", ".")
    )
    df["square_m2"] = pd.to_numeric(df["square_m2"], errors="coerce")

    # ---- Комнаты ----
    df["rooms"] = pd.to_numeric(df["rooms"], errors="coerce")

    # ---- Удаляем мусор ----
    df = df.dropna(subset=["price", "square_m2"])

    # ---- Цена за м² ----
    df["price_per_m2"] = df["price"] / df["square_m2"]

    return df


df = load_data()

# ================== ЗАГОЛОВОК ==================
st.title("🏠 Аналитика квартир Krisha.kz")
st.caption("Источник данных: собственный Python-парсер")

# ================== SIDEBAR ФИЛЬТРЫ ==================
st.sidebar.header("🔎 Фильтры")

rooms_options = sorted(df["rooms"].dropna().unique())
selected_rooms = st.sidebar.multiselect(
    "Количество комнат",
    options=rooms_options,
    default=rooms_options
)

df_filtered = df[df["rooms"].isin(selected_rooms)]

# ================== ОСНОВНЫЕ МЕТРИКИ ==================
st.subheader("📌 Ключевые показатели")

col1, col2, col3 = st.columns(3)

col1.metric(
    "Количество объявлений",
    f"{len(df_filtered)}"
)

col2.metric(
    "Средняя цена",
    f"{df_filtered['price'].mean():,.0f} ₸"
)

col3.metric(
    "Средняя цена за м²",
    f"{df_filtered['price_per_m2'].mean():,.0f} ₸"
)

# ================== ГРАФИК 1: РАСПРЕДЕЛЕНИЕ ЦЕНЫ ЗА М² ==================
st.subheader("📊 Распределение цены за м²")

fig1, ax1 = plt.subplots(figsize=(10, 4))
sns.histplot(
    df_filtered["price_per_m2"],
    bins=30,
    kde=True,
    ax=ax1
)
ax1.set_xlabel("Цена за м² (₸)")
ax1.set_ylabel("Количество объявлений")
st.pyplot(fig1)

# ================== ГРАФИК 2: ЦЕНА VS ПЛОЩАДЬ ==================
st.subheader("📐 Зависимость цены от площади")

fig2, ax2 = plt.subplots(figsize=(10, 5))
sns.scatterplot(
    data=df_filtered,
    x="square_m2",
    y="price",
    hue="rooms",
    palette="viridis",
    alpha=0.7,
    ax=ax2
)

ax2.set_xlabel("Площадь, м²")
ax2.set_ylabel("Цена, ₸")
ax2.legend(title="Комнат")
st.pyplot(fig2)

# ================== ТОП-10 САМЫХ ДОРОГИХ ЗА М² ==================
st.subheader("🚨 ТОП-10 самых дорогих квартир за м²")

top_expensive = (
    df_filtered
    .sort_values("price_per_m2", ascending=False)
    .head(10)
    [["title", "street", "rooms", "square_m2", "price", "price_per_m2"]]
)

st.dataframe(
    top_expensive,
    use_container_width=True
)

# ================== ТОП-10 УЛИЦ ПО ЦЕНЕ ЗА М² ==================
st.subheader("🏆 ТОП-10 улиц по средней цене за м²")

top_streets = (
    df_filtered
    .groupby("street")["price_per_m2"]
    .mean()
    .sort_values(ascending=False)
    .head(10)
    .reset_index()
)

fig3, ax3 = plt.subplots(figsize=(10, 4))
sns.barplot(
    data=top_streets,
    x="price_per_m2",
    y="street",
    ax=ax3
)

ax3.set_xlabel("Средняя цена за м² (₸)")
ax3.set_ylabel("")
st.pyplot(fig3)
