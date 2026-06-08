# """
# Sistem Penilaian Mahasiswa Otomatis
# Mata Kuliah: Implementasi dan Pengujian Perangkat Lunak
# Universitas Jember – 2025/2026

# Modul ini berisi logika bisnis inti yang dapat diuji secara independen
# menggunakan pytest, terpisah dari lapisan web (Flask).
# """

# import math

# # ─── Bobot Penilaian ───────────────────────────────────────────────────────
# BOBOT_TUGAS     = 0.10
# BOBOT_KUIS      = 0.20
# BOBOT_KEAKTIFAN = 0.05
# BOBOT_KEHADIRAN = 0.05
# BOBOT_UTS       = 0.30
# BOBOT_UAS       = 0.30

# # Total bobot harus = 1.0
# assert abs((BOBOT_TUGAS + BOBOT_KUIS + BOBOT_KEAKTIFAN +
#             BOBOT_KEHADIRAN + BOBOT_UTS + BOBOT_UAS) - 1.0) < 1e-9, \
#     "Total bobot tidak sama dengan 1.0!"


# # ─── Konstanta Grade ──────────────────────────────────────────────────────
# GRADE_RULES = [
#     # (batas_bawah_inklusif, batas_atas_inklusif, grade)
#     (80.0,  100.0, "A"),
#     (70.0,   79.99, "B"),
#     (60.0,   69.99, "C"),
#     (50.0,   59.99, "D"),
#     ( 0.0,   49.99, "E"),
# ]


# # ─── Helper: validasi satu nilai ──────────────────────────────────────────
# def _validasi_nilai(nama: str, nilai) -> list[str]:
#     """
#     Mengembalikan list pesan error untuk satu komponen nilai.
#     List kosong berarti nilai valid.
#     """
#     errors = []
#     # Cek tipe: harus bisa dikonversi ke float
#     try:
#         v = float(nilai)
#     except (TypeError, ValueError):
#         errors.append(f"Nilai {nama} harus berupa angka, diterima: '{nilai}'.")
#         return errors

#     # Cek NaN / Infinity
#     if math.isnan(v) or math.isinf(v):
#         errors.append(f"Nilai {nama} tidak boleh NaN atau Infinity.")
#         return errors

#     # Cek rentang [0, 100]
#     if v < 0:
#         errors.append(f"Nilai {nama} tidak boleh negatif (diterima: {v}).")
#     elif v > 100:
#         errors.append(f"Nilai {nama} tidak boleh lebih dari 100 (diterima: {v}).")

#     return errors


# # ─── Fungsi Inti ───────────────────────────────────────────────────────────

# def validasi_semua_nilai(tugas, kuis, keaktifan, kehadiran, uts, uas) -> list[str]:
#     """
#     Memvalidasi semua komponen nilai sekaligus dan mengembalikan
#     SELURUH pesan error yang ditemukan (bukan hanya yang pertama).

#     Returns:
#         list[str] – kosong jika semua valid.
#     """
#     komponen = [
#         ("Tugas",     tugas),
#         ("Kuis",      kuis),
#         ("Keaktifan", keaktifan),
#         ("Kehadiran", kehadiran),
#         ("UTS",       uts),
#         ("UAS",       uas),
#     ]
#     semua_error = []
#     for nama, nilai in komponen:
#         semua_error.extend(_validasi_nilai(nama, nilai))
#     return semua_error


# def hitung_nilai_akhir(tugas: float, kuis: float, keaktifan: float,
#                        kehadiran: float, uts: float, uas: float) -> float:
#     """
#     Menghitung nilai akhir berbobot dari enam komponen nilai.

#     Raises:
#         ValueError: Jika ada komponen yang tidak valid (semua error dilampirkan).
#     """
#     errors = validasi_semua_nilai(tugas, kuis, keaktifan, kehadiran, uts, uas)
#     if errors:
#         raise ValueError(errors)   # kirim sebagai list agar front-end bisa tampilkan semua

#     na = (float(tugas)     * BOBOT_TUGAS
#         + float(kuis)      * BOBOT_KUIS
#         + float(keaktifan) * BOBOT_KEAKTIFAN
#         + float(kehadiran) * BOBOT_KEHADIRAN
#         + float(uts)       * BOBOT_UTS
#         + float(uas)       * BOBOT_UAS)

#     # Clamp untuk menghindari floating-point overshoot (mis. 100.000000001)
#     na = max(0.0, min(100.0, na))
#     return round(na, 2)


# def tentukan_grade(nilai_akhir: float) -> str:
#     """
#     Menentukan grade huruf berdasarkan Decision Table R1–R5.

#     Rentang (inklusif kedua sisi):
#         A : 80.00 – 100.00
#         B : 70.00 –  79.99
#         C : 60.00 –  69.99
#         D : 50.00 –  59.99
#         E :  0.00 –  49.99

#     Raises:
#         ValueError: Jika nilai_akhir di luar [0, 100].
#     """
#     if not (0.0 <= nilai_akhir <= 100.0):
#         raise ValueError(
#             f"nilai_akhir harus antara 0 dan 100, diterima: {nilai_akhir}"
#         )

#     # Iterasi tabel – gunakan perbandingan eksplisit agar tidak ada gap/overlap
#     if 80.0 <= nilai_akhir <= 100.0:
#         return "A"
#     elif 70.0 <= nilai_akhir < 80.0:
#         return "B"
#     elif 60.0 <= nilai_akhir < 70.0:
#         return "C"
#     elif 50.0 <= nilai_akhir < 60.0:
#         return "D"
#     elif 0.0 <= nilai_akhir < 50.0:
#         return "E"
#     else:
#         # Fallback – seharusnya tidak pernah tercapai setelah validasi di atas
#         raise ValueError(f"Tidak dapat menentukan grade untuk nilai: {nilai_akhir}")


# def tentukan_status_lulus(grade: str) -> str:
#     """Menentukan status kelulusan berdasarkan grade."""
#     GRADE_VALID = {"A", "B", "C", "D", "E"}
#     if grade not in GRADE_VALID:
#         raise ValueError(f"Grade tidak dikenal: '{grade}'")
#     return "Lulus" if grade in {"A", "B", "C"} else "Tidak Lulus"


# def tentukan_predikat(grade: str) -> str:
#     """Menentukan predikat berdasarkan grade."""
#     predikat_map = {
#         "A": "Sangat Memuaskan",
#         "B": "Memuaskan",
#         "C": "Cukup Baik",
#         "D": "Kurang",
#         "E": "Tidak Memenuhi Syarat",
#     }
#     if grade not in predikat_map:
#         raise ValueError(f"Grade tidak dikenal: '{grade}'")
#     return predikat_map[grade]


# def tentukan_remedial(grade: str) -> str:
#     """Menentukan rekomendasi remedial berdasarkan grade."""
#     GRADE_VALID = {"A", "B", "C", "D", "E"}
#     if grade not in GRADE_VALID:
#         raise ValueError(f"Grade tidak dikenal: '{grade}'")
#     return "Perlu Remedial" if grade in {"D", "E"} else "Tidak Perlu Remedial"


# def proses_mahasiswa(data: dict) -> dict:
#     """
#     Memproses satu record mahasiswa dan mengembalikan hasil lengkap.

#     Args:
#         data: dict berisi nim, nama, tugas, kuis, keaktifan, kehadiran, uts, uas

#     Returns:
#         dict hasil penilaian lengkap.

#     Raises:
#         ValueError: Jika data tidak valid (list error atau string).
#         KeyError: Jika kunci wajib tidak ditemukan di data.
#     """
#     KUNCI_WAJIB = ["nim", "nama", "tugas", "kuis", "keaktifan", "kehadiran", "uts", "uas"]
#     missing = [k for k in KUNCI_WAJIB if k not in data]
#     if missing:
#         raise KeyError(f"Kunci wajib tidak ditemukan: {missing}")

#     nim  = str(data["nim"]).strip()
#     nama = str(data["nama"]).strip()

#     if not nim:
#         raise ValueError(["NIM tidak boleh kosong."])
#     if not nama:
#         raise ValueError(["Nama tidak boleh kosong."])

#     nilai_akhir = hitung_nilai_akhir(
#         data["tugas"], data["kuis"], data["keaktifan"],
#         data["kehadiran"], data["uts"], data["uas"]
#     )
#     grade    = tentukan_grade(nilai_akhir)
#     status   = tentukan_status_lulus(grade)
#     predikat = tentukan_predikat(grade)
#     remedial = tentukan_remedial(grade)

#     return {
#         "nim":         nim,
#         "nama":        nama,
#         "tugas":       float(data["tugas"]),
#         "kuis":        float(data["kuis"]),
#         "keaktifan":   float(data["keaktifan"]),
#         "kehadiran":   float(data["kehadiran"]),
#         "uts":         float(data["uts"]),
#         "uas":         float(data["uas"]),
#         "nilai_akhir": nilai_akhir,
#         "grade":       grade,
#         "status":      status,
#         "predikat":    predikat,
#         "remedial":    remedial,
#     }


"""
penilaian_mahasiswa.py
Sistem Penilaian Mahasiswa Otomatis
Mata Kuliah: Implementasi dan Pengujian Perangkat Lunak
Universitas Jember – 2025/2026

Grade mengacu pada sistem UNEJ: A, AB, B, BC, C, CD, D, DE, E
"""

import math

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

# ── Tabel Grade UNEJ ──────────────────────────────────────────────────────────
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
    if not nim:  raise ValueError(["NIM tidak boleh kosong."])
    if not nama: raise ValueError(["Nama tidak boleh kosong."])

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