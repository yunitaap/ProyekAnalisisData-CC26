## 📊 Bike Sharing Dashboard ✨

Dashboard interaktif berbasis **Streamlit** untuk menganalisis dataset Bike Sharing.  
Dashboard ini menampilkan berbagai insight seperti tren penggunaan, distribusi waktu, dan pola perilaku pengguna.

---

### 🚀 Fitur
- Visualisasi tren penyewaan sepeda (harian & per jam)
- Analisis pola penggunaan berdasarkan waktu
- Dashboard interaktif menggunakan Streamlit

---

### 📁 Struktur Proyek
```
ProyekAnalisisData-CC26/
├── dashboard/
│   ├── dashboard.py
│   ├── data_day.csv
│   └── data_hour.csv
├── data/
│   ├── day.csv
│   └── hour.csv
├── notebook.ipynb
├── requirements.txt
└── README.md
```

---

### ⚙️ Setup Environment (VS Code / venv)

1. Buat virtual environment:
```
python -m venv .venv
```

2. Aktifkan environment:
- Windows:
```
.venv\Scripts\activate
```
- Mac/Linux:
```
source .venv/bin/activate
```

3. Install dependencies:
```
pip install -r requirements.txt
```

---

### ▶️ Menjalankan Aplikasi

Jalankan dari root folder project:

```
streamlit run dashboard/dashboard.py
```