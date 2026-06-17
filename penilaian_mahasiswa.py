import math
import re

# ── Bobot Penilaian ───────────────────────────────────────────────────────────
BOBOT_TUGAS     = 0.10
BOBOT_KUIS      = 0.20
BOBOT_KEAKTIFAN = 0.05
BOBOT_KEHADIRAN = 0.05
BOBOT_UTS       = 0.30
BOBOT_UAS       = 0.30
 
assert abs((BOBOT_TUGAS + BOBOT_KUIS + BOBOT_KEAKTIFAN +
            BOBOT_KEHADIRAN + BOBOT_UTS + BOBOT_UAS) - 1.0) < 1e-9, \
    "Total bobot tidak sama dengan 1.0!"

# ── Tabel Grade ─────────────────────────────────────────────────
# (batas_bawah_inklusif, batas_atas_inklusif, grade, predikat, status, remedial)
GRADE_TABLE = [
    (87.50, 100.00, "A",  "Istimewa",             "Lulus",       "Tidak Perlu Remedial"),
    (75.00,  87.49, "AB", "Sangat Baik",           "Lulus",       "Tidak Perlu Remedial"),
    (62.50,  74.99, "B",  "Baik",                  "Lulus",       "Tidak Perlu Remedial"),
    (56.25,  62.49, "BC", "Cukup Baik",            "Lulus",       "Tidak Perlu Remedial"),
    (50.00,  56.24, "C",  "Cukup",                 "Lulus",       "Perlu Remedial"),
    (43.75,  49.99, "CD", "Kurang Cukup",           "Tidak Lulus", "Perlu Remedial"),
    (37.50,  43.74, "D",  "Kurang",                 "Tidak Lulus", "Perlu Remedial"),
    (18.75,  37.49, "DE", "Sangat Kurang",          "Tidak Lulus", "Perlu Remedial"),
    ( 0.00,  18.74, "E",  "Tidak Memenuhi Syarat",  "Tidak Lulus", "Perlu Remedial"),
]


def _validasi_nilai(nama: str, nilai) -> list:
    errors = []
    try:
        v = float(nilai)
    except (TypeError, ValueError):
        errors.append(f"Nilai {nama} harus berupa angka, diterima: '{nilai}'.")
        return errors
    if math.isnan(v) or math.isinf(v):
        errors.append(f"Nilai {nama} tidak boleh NaN atau Infinity.")
        return errors
    if v < 0:
        errors.append(f"Nilai {nama} tidak boleh negatif (diterima: {v}).")
    elif v > 100:
        errors.append(f"Nilai {nama} tidak boleh lebih dari 100 (diterima: {v}).")
    return errors


def validasi_semua_nilai(tugas, kuis, keaktifan, kehadiran, uts, uas) -> list:
    komponen = [
        ("Tugas", tugas), ("Kuis", kuis), ("Keaktifan", keaktifan),
        ("Kehadiran", kehadiran), ("UTS", uts), ("UAS", uas),
    ]
    errors = []
    for nama, nilai in komponen:
        errors.extend(_validasi_nilai(nama, nilai))
    return errors


def hitung_nilai_akhir(tugas: float, kuis: float, keaktifan: float,
                       kehadiran: float, uts: float, uas: float) -> float:
    errors = validasi_semua_nilai(tugas, kuis, keaktifan, kehadiran, uts, uas)
    if errors:
        raise ValueError(errors)
    na = (float(tugas)     * BOBOT_TUGAS
        + float(kuis)      * BOBOT_KUIS
        + float(keaktifan) * BOBOT_KEAKTIFAN
        + float(kehadiran) * BOBOT_KEHADIRAN
        + float(uts)       * BOBOT_UTS
        + float(uas)       * BOBOT_UAS)
    return round(max(0.0, min(100.0, na)), 2)


def tentukan_grade(nilai_akhir: float) -> str:
    if not (0.0 <= nilai_akhir <= 100.0):
        raise ValueError(f"nilai_akhir harus antara 0 dan 100, diterima: {nilai_akhir}")
    for bawah, atas, grade, *_ in GRADE_TABLE:
        if bawah <= nilai_akhir <= atas:
            return grade
    raise ValueError(f"Tidak dapat menentukan grade untuk nilai: {nilai_akhir}")


def tentukan_predikat(grade: str) -> str:
    for row in GRADE_TABLE:
        if row[2] == grade:
            return row[3]
    raise ValueError(f"Grade tidak dikenal: '{grade}'")


def tentukan_status_lulus(grade: str) -> str:
    for row in GRADE_TABLE:
        if row[2] == grade:
            return row[4]
    raise ValueError(f"Grade tidak dikenal: '{grade}'")


def tentukan_remedial(grade: str) -> str:
    for row in GRADE_TABLE:
        if row[2] == grade:
            return row[5]
    raise ValueError(f"Grade tidak dikenal: '{grade}'")


def proses_mahasiswa(data: dict) -> dict:
    KUNCI_WAJIB = ["nim", "nama", "tugas", "kuis", "keaktifan", "kehadiran", "uts", "uas"]
    missing = [k for k in KUNCI_WAJIB if k not in data]
    if missing:
        raise KeyError(f"Kunci wajib tidak ditemukan: {missing}")

    nim  = str(data["nim"]).strip()
    nama = str(data["nama"]).strip()
    
    # Kumpulkan error dalam list agar bisa memunculkan semua pesan sekaligus
    errors = []
    
    if not nim:  
        errors.append("NIM tidak boleh kosong.")
    elif not re.match(r"^\d+$", nim):
        errors.append("NIM hanya boleh berisi angka.")
        
    if not nama: 
        errors.append("Nama tidak boleh kosong.")
    elif not re.match(r"^[A-Za-z\s]+$", nama):
        errors.append("Nama hanya boleh berisi huruf dan spasi.")
        
    # Jika ada error pada nama atau nim, langsung lemparkan ValueError
    if errors:
        raise ValueError(errors)

    nilai_akhir = hitung_nilai_akhir(
        data["tugas"], data["kuis"], data["keaktifan"],
        data["kehadiran"], data["uts"], data["uas"]
    )
    grade    = tentukan_grade(nilai_akhir)
    status   = tentukan_status_lulus(grade)
    predikat = tentukan_predikat(grade)
    remedial = tentukan_remedial(grade)

    return {
        "nim":         nim,
        "nama":        nama,
        "tugas":       float(data["tugas"]),
        "kuis":        float(data["kuis"]),
        "keaktifan":   float(data["keaktifan"]),
        "kehadiran":   float(data["kehadiran"]),
        "uts":         float(data["uts"]),
        "uas":         float(data["uas"]),
        "nilai_akhir": nilai_akhir,
        "grade":       grade,
        "status":      status,
        "predikat":    predikat,
        "remedial":    remedial,
    }