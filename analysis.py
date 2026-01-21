import pandas as pd
import matplotlib.pyplot as plt
import os

# ===== 1. Загрузка =====
df = pd.read_csv("results.csv", sep=";", encoding="utf-8-sig")

print("Исходные данные:")
print(df.head())
print("\nРазмер:", df.shape)

# ===== 2. Очистка =====

# price: "11 500 000" → 11500000
df["price"] = (
    df["price"]
    .astype(str)
    .str.replace(" ", "", regex=False)
    .astype(float)
)

# square_m2: строка → число
df["square_m2"] = (
    df["square_m2"]
    .astype(str)
    .str.replace(",", ".", regex=False)
    .astype(float)
)

# rooms → число
df["rooms"] = pd.to_numeric(df["rooms"], errors="coerce")

# floor пока НЕ трогаем (оставляем строкой)

# ===== 3. Новая метрика =====
df["price_per_m2"] = df["price"] / df["square_m2"]

# ===== 4. Проверка =====
print("\nПосле очистки:")
print(df[["price", "square_m2", "rooms", "price_per_m2"]].head())

print("\nПропуски:")
print(df.isna().sum())

# ===== 5. Визуализация =====

OUTPUT_FOLDER = "charts/"
if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

# 5.1 Распределение цены за м²
plt.figure(figsize=(10, 6))
plt.hist(df["price_per_m2"], bins=30, color="skyblue", edgecolor="black")
plt.title("Распределение цены за м²")
plt.xlabel("Цена за м² (₸)")
plt.ylabel("Количество объявлений")
plt.grid(True)
plt.savefig(os.path.join(OUTPUT_FOLDER, "price_per_m2_distribution.png"), dpi=150)
plt.close()

# 5.2 Сравнение по комнатам (boxplot)
plt.figure(figsize=(10, 6))
df.boxplot(column="price_per_m2", by="rooms")
plt.title("Цена за м² по количеству комнат")
plt.suptitle("")  # убираем автоматический заголовок
plt.xlabel("Количество комнат")
plt.ylabel("Цена за м² (₸)")
plt.grid(True)
plt.savefig(os.path.join(OUTPUT_FOLDER, "price_per_m2_by_rooms.png"), dpi=150)
plt.close()

# 5.3 ТОП-10 улиц / районов по цене за м²
top_streets = df.groupby("street")["price_per_m2"].mean().sort_values(ascending=False).head(10)

plt.figure(figsize=(10, 6))
top_streets.plot(kind="barh", color="lightgreen")
plt.title("ТОП-10 улиц по средней цене за м²")
plt.xlabel("Цена за м² (₸)")
plt.ylabel("Улица")
plt.gca().invert_yaxis()  # ТОП сверху
plt.grid(True)
plt.savefig(os.path.join(OUTPUT_FOLDER, "top10_streets_price_per_m2.png"), dpi=150)
plt.close()

print(f"\n✅ Все графики сохранены в папку '{OUTPUT_FOLDER}'")

