# Sistem Penilaian Mahasiswa Otomatis
**Mata Kuliah:** Implementasi dan Pengujian Perangkat Lunak  
**Kelompok 4** · Universitas Jember 2025/2026

---

## Struktur Folder

```
sistem_penilaian/
│
├── penilaian_mahasiswa.py   ← Logika bisnis inti
├── app.py                   ← Aplikasi Flask
├── database.py              ← Koneksi & operasi MySQL
├── requirements.txt
├── pytest.ini
│
├── templates/
│   ├── index.html
│   └── rekap.html
│
├── static/
│   ├── css/style.css
│   └── js/main.js
│
└── tests/
    └── test_penilaian_mahasiswa.py
```

---

## Cara Setup dengan Laragon

### 1. Pastikan Laragon sudah berjalan
- Buka Laragon → klik **Start All**
- Pastikan MySQL sudah **Running** (port 3306)

### 2. (Opsional) Cek/ubah password MySQL
Default Laragon: user = `root`, password = `""` (kosong)  
Jika berbeda, buka `database.py` dan ubah bagian ini:
```python
DB_CONFIG = {
    "host":     "localhost",
    "port":     3306,
    "user":     "root",
    "password": "",        # ← ganti jika punya password
    "database": "ippl_penilaian",
}
```

### 3. Buat virtual environment & install
Buka terminal di folder `sistem_penilaian/`:
```bash
python -m venv venv

# Aktifkan:
venv\Scripts\activate          # Windows
source venv/bin/activate       # Mac/Linux

pip install -r requirements.txt
```

### 4. Jalankan Flask
```bash
python app.py
```
Saat pertama jalan, **database dan tabel dibuat otomatis**.  
Buka browser → **http://127.0.0.1:5000**

---

## Cara Jalankan Testing

```bash
pytest                  # semua test
pytest -v               # verbose
pytest --cov=penilaian_mahasiswa --cov-report=term-missing
```

---

## Tabel Database

**Database:** `ippl_penilaian`  
**Tabel:** `penilaian`

| Kolom       | Tipe          | Keterangan          |
|-------------|---------------|---------------------|
| id          | INT PK AUTO   | ID otomatis         |
| nim         | VARCHAR(20)   |                     |
| nama        | VARCHAR(100)  |                     |
| tugas       | DECIMAL(5,2)  |                     |
| kuis        | DECIMAL(5,2)  |                     |
| keaktifan   | DECIMAL(5,2)  |                     |
| kehadiran   | DECIMAL(5,2)  |                     |
| uts         | DECIMAL(5,2)  |                     |
| uas         | DECIMAL(5,2)  |                     |
| nilai_akhir | DECIMAL(5,2)  |                     |
| grade       | CHAR(1)       | A/B/C/D/E           |
| status      | VARCHAR(20)   | Lulus / Tidak Lulus |
| predikat    | VARCHAR(30)   |                     |
| remedial    | VARCHAR(30)   |                     |
| created_at  | DATETIME      | Waktu input         |
