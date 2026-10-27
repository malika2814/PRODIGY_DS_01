
import pandas as pd
import matplotlib.pyplot as plt

# Load the sample population dataset
url = "https://raw.githubusercontent.com/kindo-tk/PRODIGY_DS_01/main/worldpopulationdata.csv"

df = pd.read_csv(url)

# Display dataset information
print("First 5 rows:")
print(df.head())

print("\nDataset columns:")
print(df.columns.tolist())

# Identify the country and population columns
country_col = next(
    c for c in df.columns
    if "country" in c.lower() or "entity" in c.lower()
)

population_col = next(

    (c for c in df.columns if "population" in c.lower()),
    None,
)
year_col = next(
    (c for c in df.columns if c.lower() in ["year", "time"]),
    None
)

if population_col is None:
    # Some population datasets store each year in a separate column.
    year_columns = [c for c in df.columns if str(c).strip().isdigit()]
    if not year_columns:
        raise ValueError(
            "Could not find a population column or year-based population columns."
        )

    series_col = next(
        (c for c in df.columns if c.lower() in ["series name", "indicator name"]),
        None,
    )
    if series_col:
        population_rows = df[series_col].astype(str).str.contains(
            "population", case=False, na=False
        )
        df = df[population_rows].copy()
        if df.empty:
            raise ValueError("No population records were found in the dataset.")

    population_col = max(year_columns, key=lambda column: int(str(column).strip()))
    df[population_col] = pd.to_numeric(df[population_col], errors="coerce")
    latest_df = df.dropna(subset=[country_col, population_col]).copy()
else:
    df[population_col] = pd.to_numeric(df[population_col], errors="coerce")
    df = df.dropna(subset=[country_col, population_col])
    if year_col:
        df[year_col] = pd.to_numeric(df[year_col], errors="coerce")
        latest_year = df[year_col].max()
        latest_df = df[df[year_col] == latest_year].copy()
    else:
        latest_df = df.copy()

# Exclude aggregate regions if present
latest_df = latest_df[
    ~latest_df[country_col].astype(str).str.lower().isin(
        ["world", "asia", "europe", "africa",
         "north america", "south america"]
    )
]

# Bar chart: top 10 countries by population
top10 = latest_df.nlargest(10, population_col).sort_values(
    population_col
)

plt.figure(figsize=(10, 6))
plt.barh(top10[country_col], top10[population_col])
plt.xlabel("Population")
plt.ylabel("Country")
plt.title("Top 10 Countries by Population")
plt.tight_layout()
plt.show()

# Histogram: distribution of population values
plt.figure(figsize=(10, 6))
plt.hist(latest_df[population_col], bins=15, edgecolor="black")
plt.xlabel("Population")
plt.ylabel("Number of Countries")
plt.title("Distribution of Country Populations")
plt.tight_layout()
plt.show()
