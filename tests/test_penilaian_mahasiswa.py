import pytest
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from penilaian_mahasiswa import (
    hitung_nilai_akhir,
    tentukan_grade,
    tentukan_status_lulus,
    tentukan_predikat,
    tentukan_remedial,
    proses_mahasiswa,
)


def buat_input(tugas=80, kuis=80, keaktifan=80,
               kehadiran=80, uts=80, uas=80) -> dict:
    return dict(nim="000000000", nama="Test",
                tugas=tugas, kuis=kuis, keaktifan=keaktifan,
                kehadiran=kehadiran, uts=uts, uas=uas)


# ─── 1. TestHitungNilaiAkhir ─────────────────────────────────────────────────

class TestHitungNilaiAkhir:
    # Menguji formula hitung_nilai_akhir dan validasi input

    def test_semua_nilai_100(self):
        assert hitung_nilai_akhir(100, 100, 100, 100, 100, 100) == 100.0

    def test_semua_nilai_0(self):
        assert hitung_nilai_akhir(0, 0, 0, 0, 0, 0) == 0.0

    def test_bobot_uts_dominan(self):
        assert hitung_nilai_akhir(0, 0, 0, 0, 100, 0) == 30.0

    def test_bobot_uas_dominan(self):
        assert hitung_nilai_akhir(0, 0, 0, 0, 0, 100) == 30.0

    def test_bobot_kuis_dominan(self):
        assert hitung_nilai_akhir(0, 100, 0, 0, 0, 0) == 20.0

    def test_bobot_tugas_dominan(self):
        assert hitung_nilai_akhir(100, 0, 0, 0, 0, 0) == 10.0

    def test_bobot_keaktifan_dominan(self):
        assert hitung_nilai_akhir(0, 0, 100, 0, 0, 0) == 5.0

    def test_bobot_kehadiran_dominan(self):
        assert hitung_nilai_akhir(0, 0, 0, 100, 0, 0) == 5.0

    def test_nilai_campuran(self):
        expected = round(70*0.10 + 80*0.20 + 60*0.05 + 90*0.05 + 75*0.30 + 85*0.30, 2)
        assert hitung_nilai_akhir(70, 80, 60, 90, 75, 85) == expected

    def test_nilai_negatif_raise_error(self):
        with pytest.raises(ValueError, match="Tugas"):
            hitung_nilai_akhir(-1, 80, 80, 80, 80, 80)

    def test_nilai_lebih_100_raise_error(self):
        with pytest.raises(ValueError, match="UAS"):
            hitung_nilai_akhir(80, 80, 80, 80, 80, 101)

    def test_nilai_kuis_negatif_raise_error(self):
        with pytest.raises(ValueError, match="Kuis"):
            hitung_nilai_akhir(80, -5, 80, 80, 80, 80)

    def test_nilai_uts_negatif_raise_error(self):
        with pytest.raises(ValueError, match="UTS"):
            hitung_nilai_akhir(80, 80, 80, 80, -10, 80)


# ─── 2. TestTentukanGrade ────────────────────────────────────────────────────

class TestTentukanGrade:
    # R1 – Grade A
    def test_R1_grade_A_tepat_87_50(self):
        assert tentukan_grade(87.50) == "A"

    def test_R1_grade_A_nilai_95(self):
        assert tentukan_grade(95) == "A"

    def test_R1_grade_A_nilai_100(self):
        assert tentukan_grade(100) == "A"

    # R2 – Grade AB
    def test_R2_grade_AB_tepat_75(self):
        assert tentukan_grade(75.00) == "AB"

    def test_R2_grade_AB_nilai_80(self):
        assert tentukan_grade(80) == "AB"

    def test_R2_grade_AB_tepat_87_49(self):
        assert tentukan_grade(87.49) == "AB"

    # R3 – Grade B
    def test_R3_grade_B_tepat_62_50(self):
        assert tentukan_grade(62.50) == "B"

    def test_R3_grade_B_nilai_70(self):
        assert tentukan_grade(70) == "B"

    def test_R3_grade_B_tepat_74_99(self):
        assert tentukan_grade(74.99) == "B"

    # R4 – Grade BC
    def test_R4_grade_BC_tepat_56_25(self):
        assert tentukan_grade(56.25) == "BC"

    def test_R4_grade_BC_nilai_60(self):
        assert tentukan_grade(60) == "BC"

    def test_R4_grade_BC_tepat_62_49(self):
        assert tentukan_grade(62.49) == "BC"

    # R5 – Grade C
    def test_R5_grade_C_tepat_50(self):
        assert tentukan_grade(50.00) == "C"

    def test_R5_grade_C_nilai_53(self):
        assert tentukan_grade(53) == "C"

    def test_R5_grade_C_tepat_56_24(self):
        assert tentukan_grade(56.24) == "C"

    # R6 – Grade CD
    def test_R6_grade_CD_tepat_43_75(self):
        assert tentukan_grade(43.75) == "CD"

    def test_R6_grade_CD_nilai_47(self):
        assert tentukan_grade(47) == "CD"

    def test_R6_grade_CD_tepat_49_99(self):
        assert tentukan_grade(49.99) == "CD"

    # R7 – Grade D
    def test_R7_grade_D_tepat_37_50(self):
        assert tentukan_grade(37.50) == "D"

    def test_R7_grade_D_nilai_40(self):
        assert tentukan_grade(40) == "D"

    def test_R7_grade_D_tepat_43_74(self):
        assert tentukan_grade(43.74) == "D"

    # R8 – Grade DE
    def test_R8_grade_DE_tepat_18_75(self):
        assert tentukan_grade(18.75) == "DE"

    def test_R8_grade_DE_nilai_30(self):
        assert tentukan_grade(30) == "DE"

    def test_R8_grade_DE_tepat_37_49(self):
        assert tentukan_grade(37.49) == "DE"

    # R9 – Grade E
    def test_R9_grade_E_nilai_0(self):
        assert tentukan_grade(0) == "E"

    def test_R9_grade_E_nilai_10(self):
        assert tentukan_grade(10) == "E"

    def test_R9_grade_E_tepat_18_74(self):
        assert tentukan_grade(18.74) == "E"

    # Transisi batas
    def test_batas_A_ke_AB(self):
        assert tentukan_grade(87.49) == "AB"
        assert tentukan_grade(87.50) == "A"

    def test_batas_AB_ke_B(self):
        assert tentukan_grade(74.99) == "B"
        assert tentukan_grade(75.00) == "AB"

    def test_batas_B_ke_BC(self):
        assert tentukan_grade(62.49) == "BC"
        assert tentukan_grade(62.50) == "B"

    def test_batas_BC_ke_C(self):
        assert tentukan_grade(56.24) == "C"
        assert tentukan_grade(56.25) == "BC"

    def test_batas_C_ke_CD(self):
        assert tentukan_grade(49.99) == "CD"
        assert tentukan_grade(50.00) == "C"

    def test_batas_CD_ke_D(self):
        assert tentukan_grade(43.74) == "D"
        assert tentukan_grade(43.75) == "CD"

    def test_batas_D_ke_DE(self):
        assert tentukan_grade(37.49) == "DE"
        assert tentukan_grade(37.50) == "D"

    def test_batas_DE_ke_E(self):
        assert tentukan_grade(18.74) == "E"
        assert tentukan_grade(18.75) == "DE"


# ─── 3. TestStatusLulus ──────────────────────────────────────────────────────

class TestStatusLulus:
    def test_grade_A_lulus(self):
        assert tentukan_status_lulus("A") == "Lulus"

    def test_grade_AB_lulus(self):
        assert tentukan_status_lulus("AB") == "Lulus"

    def test_grade_B_lulus(self):
        assert tentukan_status_lulus("B") == "Lulus"

    def test_grade_BC_lulus(self):
        assert tentukan_status_lulus("BC") == "Lulus"

    def test_grade_C_lulus(self):
        assert tentukan_status_lulus("C") == "Lulus"

    def test_grade_CD_tidak_lulus(self):
        assert tentukan_status_lulus("CD") == "Tidak Lulus"

    def test_grade_D_tidak_lulus(self):
        assert tentukan_status_lulus("D") == "Tidak Lulus"

    def test_grade_DE_tidak_lulus(self):
        assert tentukan_status_lulus("DE") == "Tidak Lulus"

    def test_grade_E_tidak_lulus(self):
        assert tentukan_status_lulus("E") == "Tidak Lulus"


# ─── 4. TestPredikat ─────────────────────────────────────────────────────────

class TestPredikat:
    def test_grade_A_istimewa(self):
        assert tentukan_predikat("A") == "Istimewa"

    def test_grade_AB_sangat_baik(self):
        assert tentukan_predikat("AB") == "Sangat Baik"

    def test_grade_B_baik(self):
        assert tentukan_predikat("B") == "Baik"

    def test_grade_BC_cukup_baik(self):
        assert tentukan_predikat("BC") == "Cukup Baik"

    def test_grade_C_cukup(self):
        assert tentukan_predikat("C") == "Cukup"

    def test_grade_CD_kurang_cukup(self):
        assert tentukan_predikat("CD") == "Kurang Cukup"

    def test_grade_D_kurang(self):
        assert tentukan_predikat("D") == "Kurang"

    def test_grade_DE_sangat_kurang(self):
        assert tentukan_predikat("DE") == "Sangat Kurang"

    def test_grade_E_tidak_memenuhi(self):
        assert tentukan_predikat("E") == "Tidak Memenuhi Syarat"


# ─── 5. TestRemedial ─────────────────────────────────────────────────────────

class TestRemedial:
    def test_grade_A_tidak_remedial(self):
        assert tentukan_remedial("A") == "Tidak Perlu Remedial"

    def test_grade_AB_tidak_remedial(self):
        assert tentukan_remedial("AB") == "Tidak Perlu Remedial"

    def test_grade_B_tidak_remedial(self):
        assert tentukan_remedial("B") == "Tidak Perlu Remedial"

    def test_grade_BC_tidak_remedial(self):
        assert tentukan_remedial("BC") == "Tidak Perlu Remedial"

    def test_grade_C_perlu_remedial(self):
        assert tentukan_remedial("C") == "Perlu Remedial"

    def test_grade_CD_perlu_remedial(self):
        assert tentukan_remedial("CD") == "Perlu Remedial"

    def test_grade_D_perlu_remedial(self):
        assert tentukan_remedial("D") == "Perlu Remedial"

    def test_grade_DE_perlu_remedial(self):
        assert tentukan_remedial("DE") == "Perlu Remedial"

    def test_grade_E_perlu_remedial(self):
        assert tentukan_remedial("E") == "Perlu Remedial"


# ─── 6. TestProsesMahasiswa (end-to-end) ─────────────────────────────────────

class TestProsesMahasiswa:
    def test_R1_grade_A(self):
        data = buat_input(90, 90, 90, 90, 90, 90)
        data["nim"] = "231001"; data["nama"] = "Mahasiswa A"
        h = proses_mahasiswa(data)
        assert h["grade"] == "A"
        assert h["status"] == "Lulus"
        assert h["predikat"] == "Istimewa"
        assert h["remedial"] == "Tidak Perlu Remedial"

    def test_R2_grade_AB(self):
        # NA ~= 80 → AB
        data = buat_input(80, 80, 80, 80, 80, 80)
        data["nim"] = "231002"; data["nama"] = "Mahasiswa AB"
        h = proses_mahasiswa(data)
        assert h["grade"] == "AB"
        assert h["status"] == "Lulus"
        assert h["predikat"] == "Sangat Baik"
        assert h["remedial"] == "Tidak Perlu Remedial"

    def test_R3_grade_B(self):
        # NA ~= 70 → B
        data = buat_input(70, 70, 70, 70, 70, 70)
        data["nim"] = "231003"; data["nama"] = "Mahasiswa B"
        h = proses_mahasiswa(data)
        assert h["grade"] == "B"
        assert h["status"] == "Lulus"
        assert h["predikat"] == "Baik"
        assert h["remedial"] == "Tidak Perlu Remedial"

    def test_R4_grade_BC(self):
        # NA ~= 60 → BC
        data = buat_input(60, 60, 60, 60, 60, 60)
        data["nim"] = "231004"; data["nama"] = "Mahasiswa BC"
        h = proses_mahasiswa(data)
        assert h["grade"] == "BC"
        assert h["status"] == "Lulus"
        assert h["predikat"] == "Cukup Baik"
        assert h["remedial"] == "Tidak Perlu Remedial"

    def test_R5_grade_C(self):
        # NA ~= 53 → C
        data = buat_input(53, 53, 53, 53, 53, 53)
        data["nim"] = "231005"; data["nama"] = "Mahasiswa C"
        h = proses_mahasiswa(data)
        assert h["grade"] == "C"
        assert h["status"] == "Lulus"
        assert h["predikat"] == "Cukup"
        assert h["remedial"] == "Perlu Remedial"

    def test_R6_grade_CD(self):
        # NA ~= 47 → CD
        data = buat_input(47, 47, 47, 47, 47, 47)
        data["nim"] = "231006"; data["nama"] = "Mahasiswa CD"
        h = proses_mahasiswa(data)
        assert h["grade"] == "CD"
        assert h["status"] == "Tidak Lulus"
        assert h["predikat"] == "Kurang Cukup"
        assert h["remedial"] == "Perlu Remedial"

    def test_R7_grade_D(self):
        # NA ~= 40 → D
        data = buat_input(40, 40, 40, 40, 40, 40)
        data["nim"] = "231007"; data["nama"] = "Mahasiswa D"
        h = proses_mahasiswa(data)
        assert h["grade"] == "D"
        assert h["status"] == "Tidak Lulus"
        assert h["predikat"] == "Kurang"
        assert h["remedial"] == "Perlu Remedial"

    def test_R8_grade_DE(self):
        # NA ~= 30 → DE
        data = buat_input(30, 30, 30, 30, 30, 30)
        data["nim"] = "231008"; data["nama"] = "Mahasiswa DE"
        h = proses_mahasiswa(data)
        assert h["grade"] == "DE"
        assert h["status"] == "Tidak Lulus"
        assert h["predikat"] == "Sangat Kurang"
        assert h["remedial"] == "Perlu Remedial"

    def test_R9_grade_E(self):
        # NA ~= 10 → E
        data = buat_input(10, 10, 10, 10, 10, 10)
        data["nim"] = "231009"; data["nama"] = "Mahasiswa E"
        h = proses_mahasiswa(data)
        assert h["grade"] == "E"
        assert h["status"] == "Tidak Lulus"
        assert h["predikat"] == "Tidak Memenuhi Syarat"
        assert h["remedial"] == "Perlu Remedial"

    def test_nim_dan_nama_tersimpan(self):
        data = buat_input()
        data["nim"] = "231910101099"; data["nama"] = "Fulan bin Fulan"
        h = proses_mahasiswa(data)
        assert h["nim"] == "231910101099"
        assert h["nama"] == "Fulan bin Fulan"

    def test_output_mengandung_semua_key(self):
        data = buat_input()
        data["nim"] = "000"; data["nama"] = "Test"
        h = proses_mahasiswa(data)
        for key in ("nim","nama","tugas","kuis","keaktifan","kehadiran",
                    "uts","uas","nilai_akhir","grade","status","predikat","remedial"):
            assert key in h

    def test_input_invalid_raise_error(self):
        data = buat_input(uas=105)
        data["nim"] = "000"; data["nama"] = "Error"
        with pytest.raises(ValueError):
            proses_mahasiswa(data)

    def test_nim_kosong_raise_error(self):
        data = buat_input()
        data["nim"] = "  "; data["nama"] = "Test"
        with pytest.raises(ValueError):
            proses_mahasiswa(data)

    def test_nama_kosong_raise_error(self):
        data = buat_input()
        data["nim"] = "123"; data["nama"] = "  "
        with pytest.raises(ValueError):
            proses_mahasiswa(data)


# ─── 7. TestBoundaryValue ────────────────────────────────────────────────────

class TestBoundaryValue:
    # Boundary Value Analysis pada setiap batas transisi grade
    @pytest.mark.parametrize("na,expected_grade", [
        (100.00, "A"),
        (87.50,  "A"),
        (87.49,  "AB"),
        (75.00,  "AB"),
        (74.99,  "B"),
        (62.50,  "B"),
        (62.49,  "BC"),
        (56.25,  "BC"),
        (56.24,  "C"),
        (50.00,  "C"),
        (49.99,  "CD"),
        (43.75,  "CD"),
        (43.74,  "D"),
        (37.50,  "D"),
        (37.49,  "DE"),
        (18.75,  "DE"),
        (18.74,  "E"),
        (0.00,   "E"),
    ])
    def test_boundary_grade(self, na, expected_grade):
        assert tentukan_grade(na) == expected_grade, (
            f"NA={na} seharusnya Grade {expected_grade}"
        )