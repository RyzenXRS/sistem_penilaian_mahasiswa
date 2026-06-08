import mysql.connector
from mysql.connector import Error

# ─── Konfigurasi Database ──────────────────────────────────────────────
DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "",           # Laragon default
    "database": "nilai_mahasiswa",
    "charset": "utf8mb4",
}


# ─── Koneksi ───────────────────────────────────────────────────────────
def get_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        if conn.is_connected():
            return conn
        raise Exception("Gagal terhubung ke database.")
    except Error as e:
        raise Exception(f"Error koneksi database: {e}")


# ─── Inisialisasi Database & Tabel ─────────────────────────────────────
def init_db():
    try:
        cfg_no_db = {k: v for k, v in DB_CONFIG.items() if k != "database"}
        conn = mysql.connector.connect(**cfg_no_db)
        cursor = conn.cursor()

        cursor.execute(
            f"""
            CREATE DATABASE IF NOT EXISTS `{DB_CONFIG['database']}`
            CHARACTER SET utf8mb4
            COLLATE utf8mb4_unicode_ci
            """
        )
        conn.commit()
        cursor.close()
        conn.close()

        conn = get_connection()
        cursor = conn.cursor()

        # grade VARCHAR(2) agar mendukung: A, AB, B, BC, C, CD, D, DE, E
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS penilaian (
                id INT AUTO_INCREMENT PRIMARY KEY,

                nim VARCHAR(20) NOT NULL,
                nama VARCHAR(100) NOT NULL,

                tugas DECIMAL(5,2) NOT NULL,
                kuis DECIMAL(5,2) NOT NULL,
                keaktifan DECIMAL(5,2) NOT NULL,
                kehadiran DECIMAL(5,2) NOT NULL,
                uts DECIMAL(5,2) NOT NULL,
                uas DECIMAL(5,2) NOT NULL,

                nilai_akhir DECIMAL(5,2) NOT NULL,
                grade VARCHAR(2) NOT NULL,
                status VARCHAR(20) NOT NULL,
                predikat VARCHAR(30) NOT NULL,
                remedial VARCHAR(30) NOT NULL,

                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)

        conn.commit()
        cursor.close()
        conn.close()

        print("Database dan tabel berhasil dibuat.")

    except Error as e:
        print(f"Gagal inisialisasi database: {e}")
        raise


# ─── Insert Data ───────────────────────────────────────────────────────
def simpan_penilaian(hasil: dict) -> int:
    conn = get_connection()
    cursor = conn.cursor()

    try:
        sql = """
            INSERT INTO penilaian
            (nim, nama, tugas, kuis, keaktifan, kehadiran, uts, uas,
             nilai_akhir, grade, status, predikat, remedial)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (
            hasil["nim"], hasil["nama"],
            hasil["tugas"], hasil["kuis"], hasil["keaktifan"], hasil["kehadiran"],
            hasil["uts"], hasil["uas"],
            hasil["nilai_akhir"], hasil["grade"], hasil["status"],
            hasil["predikat"], hasil["remedial"]
        )
        cursor.execute(sql, values)
        conn.commit()
        return cursor.lastrowid
    finally:
        cursor.close()
        conn.close()


# ─── Ambil Semua Data ──────────────────────────────────────────────────
def ambil_semua_penilaian() -> list:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM penilaian ORDER BY created_at DESC")
        rows = cursor.fetchall()
        for row in rows:
            for key in ("tugas","kuis","keaktifan","kehadiran","uts","uas","nilai_akhir"):
                row[key] = float(row[key])
            if row["created_at"]:
                row["created_at"] = row["created_at"].strftime("%d/%m/%Y %H:%M")
        return rows
    finally:
        cursor.close()
        conn.close()


# ─── Hapus Berdasarkan ID ──────────────────────────────────────────────
def hapus_penilaian_by_id(record_id: int) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM penilaian WHERE id = %s", (record_id,))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        cursor.close()
        conn.close()


# ─── Hapus Semua Data ──────────────────────────────────────────────────
def hapus_semua_penilaian() -> int:
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM penilaian")
        conn.commit()
        return cursor.rowcount
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    init_db()
    print("Database siap digunakan.")