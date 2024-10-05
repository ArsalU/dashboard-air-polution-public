import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.cm as cm

station_data = {
    "station": ["Wanshouxigong", "Gucheng", "Dongsi", "Nongzhanguan", "Wanliu", 
                "Tiantan", "Aotizhongxin", "Guanyuan", "Shunyi", "Changping", 
                "Huairou", "Dingling"],
    "latitude": [39.9026, 39.9155, 39.9390, 39.9174, 39.9785, 
                 39.8820, 39.8701, 39.9405, 40.1234, 40.2196, 
                 40.0636, 39.9380],
    "longitude": [116.3973, 116.3051, 116.4122, 116.2956, 116.2742, 
                  116.4340, 116.4280, 116.2975, 116.6708, 116.1360, 
                  116.4145, 116.3081]
}

df_stations = pd.DataFrame(station_data)

pollutant_data_file = 'C:/Users/Arsal Utama/Downloads/Bangkit/Course/4. Analisis Data Dengan Python/merged_cleaned_data.csv'
df_pollutants = pd.read_csv(pollutant_data_file, parse_dates=['date'])

df_pollutants['year'] = df_pollutants['date'].dt.year

st.set_page_config(page_title="Air Quality Dashboard", layout="wide")

st.markdown("<h1 style='text-align: center;'>Air Quality Monitoring Dashboard</h1>", unsafe_allow_html=True)

st.markdown("""
    <div style='text-align: center; padding: 10px 50px;'>
    This dashboard provides an interactive visualization of air quality data from various monitoring stations in Beijing. 
    It showcases PM2.5 and PM10 concentrations across different locations and over time, 
    offering insights into air pollution trends and spatial variations in the city.
    </div>
    """, unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

station_averages = df_pollutants.groupby('station')[['PM2.5', 'PM10']].mean().reset_index()

station_coordinates = {row['station']: (row['latitude'], row['longitude']) for _, row in df_stations.iterrows()}

station_averages['latitude'] = station_averages['station'].map(lambda x: station_coordinates[x][0])
station_averages['longitude'] = station_averages['station'].map(lambda x: station_coordinates[x][1])

st.subheader("Monitoring Stations Map")

map_container = st.container()
with map_container:
    map_height = 600

    m = folium.Map(location=[39.9042, 116.4074], zoom_start=10)

    pm25_values = station_averages['PM2.5'].values
    norm = mcolors.Normalize(vmin=min(pm25_values), vmax=max(pm25_values))

    colors = [cm.RdYlGn(1 - norm(value)) for value in pm25_values]

    for idx, row in station_averages.iterrows():
        color_hex = mcolors.to_hex(colors[idx][:3])
        folium.CircleMarker(
            location=(row['latitude'], row['longitude']),
            radius=8 + (row['PM2.5'] / 10),
            color='black',
            fill=True,
            fill_color=color_hex,
            fill_opacity=0.6,
            popup=f"{row['station']}: PM2.5 {row['PM2.5']:.2f} µg/m³"
        ).add_to(m)

    st.markdown(
        """
        <style>
        .fullScreenFrame > div {
            display: flex;
            justify-content: center;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    folium_static(m, width=1200, height=map_height)

analysis_option = st.selectbox(
    "Choose an analysis to display:",
    ("Perbandingan Kadar Polutan di Stasiun-stasiun", "Tren Tahunan Konsentrasi PM2.5 dan PM10", "Dampak Hujan pada Konsentrasi Polutan Udara")
)

if analysis_option == "Perbandingan Kadar Polutan di Stasiun-stasiun":
    st.subheader("Perbandingan Kadar Polutan di Stasiun-stasiun")
    
    pollutants = ['PM2.5', 'PM10', 'SO2', 'NO2', 'CO', 'O3']
    
    station_averages = df_pollutants.groupby('station')[pollutants].mean().reset_index()
    
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    axes = axes.flatten()
    
    for idx, pollutant in enumerate(pollutants):
        sns.barplot(x='station', y=pollutant, data=station_averages, ax=axes[idx])
        axes[idx].set_title(f'Average {pollutant} Levels by Station')
        axes[idx].set_xlabel('Station')
        axes[idx].set_ylabel(f'{pollutant} Concentration')
        axes[idx].tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    st.pyplot(fig)
    
    station_averages['AQI'] = station_averages[pollutants].mean(axis=1)
    worst_stations = station_averages.sort_values('AQI', ascending=False)
    
    st.subheader("Stations ranked by overall air quality (worst to best):")
    st.dataframe(worst_stations[['station', 'AQI']])
    
    st.subheader("Analysis:")
    st.write("""
    - Kualitas Udara yang Buruk di Stasiun Tertentu: Stasiun Wanshouxigong memiliki Indeks Kualitas Udara (AQI) tertinggi, 
      yaitu 283.33, menandakan kondisi polusi yang sangat buruk. Stasiun Gucheng dan Dongsi juga berada di urutan teratas 
      dengan AQI masing-masing 278.50 dan 276.43.
    
    - Fluktuasi Level Polutan: Level polutan PM2.5 dan PM10 dan polutan lainnya menunjukkan fluktuasi yang signifikan antar stasiun. 
      Hal ini mengindikasikan bahwa faktor lingkungan dan manusia dapat berkontribusi terhadap variasi konsentrasi polutan di udara. 
      Oleh karena itu, saya menambahkan analisis geospasial untuk memahami lebih dalam mengenai kondisi stasiun-stasiun ini.
    """)

elif analysis_option == "Tren Tahunan Konsentrasi PM2.5 dan PM10":
    st.subheader("Tren Tahunan Konsentrasi PM2.5 dan PM10")
    
    if 'year' not in df_pollutants.columns:
        df_pollutants['year'] = df_pollutants['date'].dt.year
    
    annual_pm = df_pollutants.groupby('year')[['PM2.5', 'PM10']].mean().reset_index()
    
    st.write("Annual average concentrations of PM2.5 and PM10:")
    st.dataframe(annual_pm)
    
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(annual_pm['year'], annual_pm['PM2.5'], label='PM2.5')
    ax.plot(annual_pm['year'], annual_pm['PM10'], label='PM10')
    ax.set_xlabel('Year')
    ax.set_ylabel('Concentration (μg/m³)')
    ax.set_title('Annual Trends of PM2.5 and PM10 Concentrations')
    ax.legend()
    ax.grid(True)
    
    st.pyplot(fig)
    
    st.subheader("Analysis:")
    st.write("""
    - Fluktuasi dan Tren Umum: Data menunjukkan fluktuasi signifikan dalam konsentrasi PM2.5 dan PM10 selama periode lima tahun, 
      dengan puncak tertinggi terjadi pada tahun 2014. Konsentrasi PM2.5 menurun menjadi terendah pada tahun 2016 (72.08 µg/m³), 
      tetapi kemudian meningkat kembali pada tahun 2017 (92.41 µg/m³).

    - Perbandingan dan Dampak Kesehatan: Secara konsisten, konsentrasi PM2.5 lebih tinggi dibandingkan dengan PM10, 
      menandakan bahwa partikel halus lebih dominan di lingkungan. Tingginya kadar PM2.5, yang berpotensi berdampak lebih besar 
      pada kesehatan, menunjukkan perlunya perhatian lebih dalam pemantauan dan pengendalian polusi udara untuk melindungi 
      kesehatan masyarakat.
    """)

elif analysis_option == "Dampak Hujan pada Konsentrasi Polutan Udara":
    st.subheader("Dampak Hujan pada Konsentrasi Polutan Udara")

    df_pollutants['is_rainy'] = df_pollutants['RAIN'] > 0
    pollutants = ['PM2.5', 'PM10', 'SO2', 'NO2', 'CO', 'O3']

    rain_impact = df_pollutants.groupby('is_rainy')[pollutants].mean()
    rain_impact['percent_change'] = (rain_impact.loc[True] - rain_impact.loc[False]) / rain_impact.loc[False] * 100

    st.write("Mean pollutant concentrations and percent change on rainy vs non-rainy days:")
    st.dataframe(rain_impact)

    fig, axes = plt.subplots(2, 3, figsize=(20, 15))
    for i, pollutant in enumerate(pollutants):
        row = i // 3
        col = i % 3
        sns.boxplot(x='is_rainy', y=pollutant, data=df_pollutants, ax=axes[row, col])
        axes[row, col].set_title(f'{pollutant} Concentration vs Rainfall')
        axes[row, col].set_xlabel('Rainy Day')
        axes[row, col].set_ylabel('Concentration')
    plt.tight_layout()
    st.pyplot(fig)

    correlation = df_pollutants[pollutants + ['RAIN']].corr()
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(correlation, annot=True, cmap='coolwarm', vmin=-1, vmax=1, center=0, ax=ax)
    plt.title('Correlation between Rainfall and Pollutants')
    st.pyplot(fig)

    st.subheader("Analysis:")
    st.write("""
    - Dari hasil boxplot, terlihat bahwa tingkat polutan saat terjadi hujan cenderung lebih rendah dibandingkan dengan saat tidak hujan. 
      Ini menunjukkan bahwa hujan dapat berperan sebagai mekanisme alamiah yang membantu mengurangi konsentrasi polutan udara.
    
    - Analisis korelasi menunjukkan bahwa terdapat hubungan negatif yang kuat antara curah hujan dan konsentrasi PM2.5 serta PM10, 
      dengan nilai korelasi masing-masing sebesar -0.027 dan -0.014. Hal ini menegaskan bahwa peningkatan curah hujan berhubungan 
      dengan penurunan kadar kedua jenis polutan tersebut di udara.
    """)

st.markdown("<hr>", unsafe_allow_html=True)
st.write("Data Source: Beijing Multi-Site Air-Quality Data")
st.write("By: Arsal Utama | Bangkit 2024 Batch 2 ML-23")

st.markdown("""
For a more detailed analysis, please check out our [full analysis notebook on Google Colab](https://colab.research.google.com/drive/1Iac3SkWlron3z1qGBrqhxy-MQOlZvEbT?usp=sharing).
""")