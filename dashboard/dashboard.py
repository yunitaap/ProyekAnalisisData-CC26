import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

sns.set(style='whitegrid')

st.markdown("""
<style>
    section[data-testid="stSidebar"] > div {
        overflow-y: auto;
        max-height: 100vh;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# Load data
# ============================================================
df_day  = pd.read_csv('dashboard/data_day.csv')
df_hour = pd.read_csv('dashboard/data_hour.csv')

df_day['dteday']  = pd.to_datetime(df_day['dteday'])
df_hour['dteday'] = pd.to_datetime(df_hour['dteday'])

# Urutan kategori
season_order     = ['Spring', 'Summer', 'Fall', 'Winter']
weekday_order    = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
weathersit_order = ['Clear', 'Mist/Cloudy', 'Light Rain/Snow', 'Heavy Rain/Snow']

for df in [df_day, df_hour]:
    df['season']     = pd.Categorical(df['season'],     categories=season_order,     ordered=True)
    df['weekday']    = pd.Categorical(df['weekday'],    categories=weekday_order,    ordered=True)
    df['weathersit'] = pd.Categorical(df['weathersit'], categories=weathersit_order, ordered=True)

min_date = df_day['dteday'].min()
max_date = df_day['dteday'].max()

# ============================================================
# Sidebar
# ============================================================
with st.sidebar:
    st.title('🚲 Bike Sharing')
    st.markdown('---')

    st.subheader('Filter Rentang Waktu')

    range_option = st.selectbox(
        'Pilih Periode',
        ['Semua Data', '1 Bulan Terakhir', '3 Bulan Terakhir',
         '6 Bulan Terakhir', 'Tahun 2011', 'Tahun 2012', 'Custom']
    )

    if range_option == 'Semua Data':
        start_date, end_date = min_date, max_date

    elif range_option == '1 Bulan Terakhir':
        start_date = max_date - pd.DateOffset(months=1)
        end_date   = max_date

    elif range_option == '3 Bulan Terakhir':
        start_date = max_date - pd.DateOffset(months=3)
        end_date   = max_date

    elif range_option == '6 Bulan Terakhir':
        start_date = max_date - pd.DateOffset(months=6)
        end_date   = max_date

    elif range_option == 'Tahun 2011':
        start_date = pd.Timestamp('2011-01-01')
        end_date   = pd.Timestamp('2011-12-31')

    elif range_option == 'Tahun 2012':
        start_date = pd.Timestamp('2012-01-01')
        end_date   = pd.Timestamp('2012-12-31')

    elif range_option == 'Custom':
        start_date = st.date_input('Tanggal Mulai', value=min_date,
                                    min_value=min_date, max_value=max_date)
        end_date   = st.date_input('Tanggal Selesai', value=max_date,
                                    min_value=min_date, max_value=max_date)
        start_date = pd.Timestamp(start_date)
        end_date   = pd.Timestamp(end_date)

        if start_date > end_date:
            st.error('Tanggal mulai tidak boleh lebih besar dari tanggal selesai.')
            st.stop()

    st.markdown('---')
    st.subheader('Filter Rentang Jam')
    jam_range = st.slider(
        'Pilih Rentang Jam',
        min_value=0,
        max_value=23,
        value=(0, 23),       # tuple = slider dengan dua handle
        format='%d:00'
    )
    jam_mulai, jam_selesai = jam_range

    st.markdown('---')
    st.caption(f'Periode : {start_date.strftime("%d %b %Y")} – {end_date.strftime("%d %b %Y")}')
    st.caption(f'Jam     : {jam_mulai}:00 – {jam_selesai}:00')

# ============================================================
# Filter dataframe
# ============================================================
day_filtered  = df_day[(df_day['dteday'] >= start_date) &
                        (df_day['dteday'] <= end_date)]
hour_filtered = df_hour[(df_hour['dteday'] >= start_date) &
                         (df_hour['dteday'] <= end_date) &
                         (df_hour['hr'] >= jam_mulai) &
                         (df_hour['hr'] <= jam_selesai)]

# ============================================================
# Header
# ============================================================
st.title('🚲 Bike Sharing Dashboard')
st.markdown(f'Menampilkan data **{start_date.strftime("%d %b %Y")}** hingga **{end_date.strftime("%d %b %Y")}**')
st.markdown('---')

# ============================================================
# Metrik Utama
# ============================================================
total_cnt        = day_filtered['cnt'].sum()
total_casual     = day_filtered['casual'].sum()
total_registered = day_filtered['registered'].sum()
avg_per_day      = day_filtered['cnt'].mean()

col1, col2, col3, col4 = st.columns(4)
col1.metric('Total Peminjaman',    f'{total_cnt:,}')
col2.metric('Pengguna Casual',     f'{total_casual:,}')
col3.metric('Pengguna Registered', f'{total_registered:,}')
col4.metric('Rata-rata/Hari',      f'{avg_per_day:,.0f}')

st.markdown('---')

# ============================================================
# Q1 — Tren Peminjaman
# ============================================================
st.subheader('📈 Tren Peminjaman Harian')

fig, ax = plt.subplots(figsize=(14, 4))
ax.plot(day_filtered['dteday'], day_filtered['cnt'],
        color='#2563EB', linewidth=1.5, alpha=0.8)
ax.fill_between(day_filtered['dteday'], day_filtered['cnt'],
                alpha=0.1, color='#2563EB')
ax.set_xlabel('Tanggal')
ax.set_ylabel('Jumlah Peminjaman')
ax.tick_params(axis='x', rotation=30)
st.pyplot(fig)

# Insight dinamis
bulan_tertinggi = day_filtered.groupby(day_filtered['dteday'].dt.month)['cnt'].mean().idxmax()
bulan_terendah  = day_filtered.groupby(day_filtered['dteday'].dt.month)['cnt'].mean().idxmin()
nama_bulan      = ['', 'Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni',
                   'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember']

st.info(f'📌 Pada periode ini, rata-rata peminjaman harian tertinggi terjadi di bulan '
        f'**{nama_bulan[bulan_tertinggi]}** dan terendah di bulan **{nama_bulan[bulan_terendah]}**. '
        f'Total peminjaman mencapai **{total_cnt:,}** dengan rata-rata **{avg_per_day:,.0f}** peminjaman per hari.')

st.markdown('---')

# ============================================================
# Q2 — Pola per Jam
# ============================================================
st.subheader('🕐 Pola Peminjaman per Jam')

hour_jam = hour_filtered[(hour_filtered['hr'] >= jam_mulai) &
                          (hour_filtered['hr'] <= jam_selesai)]

hourly_seg = hour_jam.groupby('hr', observed=True)[['casual', 'registered']].mean().reset_index()

fig, ax = plt.subplots(figsize=(12, 4))
ax.plot(hourly_seg['hr'], hourly_seg['casual'],
        marker='o', markersize=4, label='Casual',
        color='#F97316', linewidth=2)
ax.plot(hourly_seg['hr'], hourly_seg['registered'],
        marker='o', markersize=4, label='Registered',
        color='#2563EB', linewidth=2)
ax.set_xlabel('Jam')
ax.set_ylabel('Rata-rata Peminjaman')
ax.set_xticks(range(jam_mulai, jam_selesai + 1))
ax.legend()
st.pyplot(fig)

# Insight dinamis
jam_puncak_reg  = int(hourly_seg.loc[hourly_seg['registered'].idxmax(), 'hr'])
jam_puncak_cas  = int(hourly_seg.loc[hourly_seg['casual'].idxmax(), 'hr'])
avg_reg_periode = hourly_seg['registered'].mean()
avg_cas_periode = hourly_seg['casual'].mean()

st.info(f'📌 Pada rentang jam **{jam_mulai}:00 – {jam_selesai}:00**, '
        f'pengguna registered mencapai puncak di jam **{jam_puncak_reg}:00** '
        f'(rata-rata {avg_reg_periode:,.0f} peminjaman/jam) dan '
        f'pengguna casual paling aktif di jam **{jam_puncak_cas}:00** '
        f'(rata-rata {avg_cas_periode:,.0f} peminjaman/jam).')

st.markdown('---')

# ============================================================
# Q3 — Pengaruh Musim & Cuaca
# ============================================================
st.subheader('🌤️ Pengaruh Musim & Kondisi Cuaca')

col1, col2 = st.columns(2)

with col1:
    season_avg = day_filtered.groupby('season', observed=True)['cnt'].mean().reset_index()
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(season_avg['season'], season_avg['cnt'], color='#2563EB')
    ax.set_title('Rata-rata Peminjaman per Musim')
    ax.set_xlabel('Musim')
    ax.set_ylabel('Rata-rata Peminjaman/Hari')
    st.pyplot(fig)

with col2:
    weather_avg = day_filtered.groupby('weathersit', observed=True)['cnt'].mean().reset_index()
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(weather_avg['weathersit'], weather_avg['cnt'], color='#2563EB')
    ax.set_title('Rata-rata Peminjaman per Kondisi Cuaca')
    ax.set_xlabel('Kondisi Cuaca')
    ax.set_ylabel('Rata-rata Peminjaman/Hari')
    ax.tick_params(axis='x', rotation=15)
    st.pyplot(fig)

# Insight dinamis
musim_terbaik   = season_avg.loc[season_avg['cnt'].idxmax(), 'season']
cuaca_terbaik   = weather_avg.loc[weather_avg['cnt'].idxmax(), 'weathersit']

st.info(f'📌 Musim **{musim_terbaik}** mencatat rata-rata peminjaman tertinggi pada periode ini. '
        f'Kondisi cuaca **{cuaca_terbaik}** menghasilkan aktivitas peminjaman paling tinggi, '
        f'menunjukkan bahwa cuaca yang nyaman mendorong lebih banyak orang untuk bersepeda.')

# ============================================================
# Q4 — Hari Kerja vs Bukan
# ============================================================
st.subheader('📅 Pola Hari Kerja vs Akhir Pekan')

col1, col2 = st.columns(2)

with col1:
    hourly_wd = hour_filtered.groupby(['hr', 'workingday'], observed=True)['registered'].mean().reset_index()
    fig, ax = plt.subplots(figsize=(6, 4))
    for wd, color, label in zip(['No', 'Yes'], ['#F97316', '#2563EB'],
                                  ['Bukan Hari Kerja', 'Hari Kerja']):
        subset = hourly_wd[hourly_wd['workingday'] == wd]
        ax.plot(subset['hr'], subset['registered'], marker='o', markersize=3,
                label=label, color=color, linewidth=2)
    ax.set_title('Pola Jam — Registered')
    ax.set_xlabel('Jam')
    ax.set_ylabel('Rata-rata Peminjaman')
    ax.set_xticks(range(0, 24))
    ax.legend(fontsize=8)
    st.pyplot(fig)

with col2:
    hourly_cas = hour_filtered.groupby(['hr', 'workingday'], observed=True)['casual'].mean().reset_index()
    fig, ax = plt.subplots(figsize=(6, 4))
    for wd, color, label in zip(['No', 'Yes'], ['#F97316', '#2563EB'],
                                  ['Bukan Hari Kerja', 'Hari Kerja']):
        subset = hourly_cas[hourly_cas['workingday'] == wd]
        ax.plot(subset['hr'], subset['casual'], marker='o', markersize=3,
                label=label, color=color, linewidth=2)
    ax.set_title('Pola Jam — Casual')
    ax.set_xlabel('Jam')
    ax.set_ylabel('Rata-rata Peminjaman')
    ax.set_xticks(range(0, 24))
    ax.legend(fontsize=8)
    st.pyplot(fig)

avg_workday  = day_filtered[day_filtered['workingday'] == 'Yes']['cnt'].mean()
avg_weekend  = day_filtered[day_filtered['workingday'] == 'No']['cnt'].mean()

st.info(f'📌 Rata-rata peminjaman di hari kerja adalah **{avg_workday:,.0f}** dan di akhir pekan/libur '
        f'**{avg_weekend:,.0f}** per hari. Meski totalnya serupa, pola jamnya sangat berbeda dimana '
        f'pengguna registered cenderung beraktivitas di jam kerja, sementara casual lebih aktif di jam santai dan akhir pekan.')

st.markdown('---')

# ============================================================
# Q5 — Segmentasi Casual vs Registered
# ============================================================
st.subheader('👥 Segmentasi Pengguna: Casual vs Registered')

col1, col2 = st.columns(2)

with col1:
    total_casual     = day_filtered['casual'].sum()
    total_registered = day_filtered['registered'].sum()

    fig, ax = plt.subplots(figsize=(5, 5))
    ax.pie([total_casual, total_registered],
           labels=['Casual', 'Registered'],
           colors=['#F97316', '#2563EB'],
           autopct='%1.1f%%', startangle=90,
           wedgeprops={'edgecolor': 'white', 'linewidth': 2})
    ax.set_title('Proporsi Total Peminjaman')
    st.pyplot(fig)

with col2:
    seg_season = day_filtered.groupby('season', observed=True)[['casual', 'registered']].mean().reset_index()
    x = range(len(seg_season))
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.bar(x, seg_season['registered'], label='Registered', color='#2563EB')
    ax.bar(x, seg_season['casual'],     label='Casual',     color='#F97316',
           bottom=seg_season['registered'])
    ax.set_xticks(x)
    ax.set_xticklabels(seg_season['season'])
    ax.set_title('Casual vs Registered per Musim')
    ax.set_ylabel('Rata-rata Peminjaman/Hari')
    ax.legend()
    st.pyplot(fig)

pct_casual     = total_casual / (total_casual + total_registered) * 100
pct_registered = 100 - pct_casual

st.info(f'📌 Pada periode ini, pengguna registered berkontribusi **{pct_registered:.1f}%** '
        f'dan casual **{pct_casual:.1f}%** dari total peminjaman. '
        f'Registered adalah tulang punggung bisnis yang stabil di semua kondisi, '
        f'sementara casual lebih responsif terhadap musim dan cuaca.')

st.markdown('---')
st.caption('© 2025 Bike Sharing Analysis')