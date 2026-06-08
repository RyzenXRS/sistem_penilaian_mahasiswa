"""
app.py – Entry point aplikasi web Flask
Sistem Penilaian Mahasiswa Otomatis – Grade UNEJ
"""

import os
import ast
import json
import subprocess
import sys

from flask import Flask, render_template, request, jsonify
from penilaian_mahasiswa import proses_mahasiswa, validasi_semua_nilai
from database import init_db, simpan_penilaian, ambil_semua_penilaian, hapus_penilaian_by_id, hapus_semua_penilaian

app = Flask(__name__)
app.secret_key = "ippl-unej-2025-secret"

with app.app_context():
    try:
        init_db()
        print("Database siap.")
    except Exception as e:
        print(f"Gagal koneksi database: {e}")
        print("Pastikan Laragon/MySQL sudah berjalan.")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/nilai", methods=["POST"])
def hitung_nilai():
    try:
        nim  = request.form.get("nim",  "").strip()
        nama = request.form.get("nama", "").strip()
        errors = []
        if not nim:  errors.append("NIM tidak boleh kosong.")
        if not nama: errors.append("Nama tidak boleh kosong.")

        nilai_fields = {}
        for field in ["tugas", "kuis", "keaktifan", "kehadiran", "uts", "uas"]:
            raw = request.form.get(field, "")
            if raw == "" or raw is None:
                errors.append(f"Nilai {field.capitalize()} tidak boleh kosong.")
            else:
                try:
                    nilai_fields[field] = float(raw)
                except ValueError:
                    errors.append(f"Nilai {field.capitalize()} harus berupa angka, diterima: '{raw}'.")

        if not errors and len(nilai_fields) == 6:
            range_errors = validasi_semua_nilai(
                nilai_fields["tugas"], nilai_fields["kuis"],
                nilai_fields["keaktifan"], nilai_fields["kehadiran"],
                nilai_fields["uts"], nilai_fields["uas"]
            )
            errors.extend(range_errors)

        if errors:
            return jsonify({"errors": errors}), 400

        data = {"nim": nim, "nama": nama, **nilai_fields}
        hasil = proses_mahasiswa(data)
        new_id = simpan_penilaian(hasil)
        hasil["id"] = new_id
        return jsonify({"success": True, "hasil": hasil})

    except ValueError as e:
        err = e.args[0]
        if isinstance(err, list):
            return jsonify({"errors": err}), 400
        return jsonify({"errors": [str(err)]}), 400
    except Exception as e:
        return jsonify({"errors": [f"Terjadi kesalahan server: {str(e)}"]}), 500


@app.route("/aturan")
def aturan():
    return render_template("aturan.html")


@app.route("/rekap")
def rekap():
    try:
        daftar = ambil_semua_penilaian()
    except Exception:
        daftar = []
    return render_template("rekap.html", daftar=daftar)


@app.route("/testing")
def testing():
    return render_template("testing.html")


# ─── Helper: parse test file untuk ambil metadata tiap test ─────────────────
def _parse_test_metadata(test_file_path: str) -> dict:
    """
    Membaca file test dengan AST dan mengekstrak:
    - docstring class
    - nama method
    - docstring method (jika ada)
    - source code method (untuk deskripsi fallback)

    Returns:
        dict: { "ClassName::test_name": {"desc": str, "class_desc": str, "source": str} }
    """
    meta = {}
    try:
        with open(test_file_path, "r", encoding="utf-8") as f:
            source = f.read()
        tree = ast.parse(source)
        lines = source.splitlines()

        for node in ast.walk(tree):
            if not isinstance(node, ast.ClassDef):
                continue
            class_name = node.name
            class_doc  = ast.get_docstring(node) or ""

            for item in node.body:
                if not isinstance(item, ast.FunctionDef):
                    continue
                method_name = item.name
                if not method_name.startswith("test"):
                    continue

                method_doc = ast.get_docstring(item) or ""

                # Ambil baris source method (tanpa docstring)
                start = item.lineno - 1
                end   = item.end_lineno
                method_src = "\n".join(lines[start:end])

                key = f"{class_name}::{method_name}"
                meta[key] = {
                    "class_desc":  class_doc,
                    "method_doc":  method_doc,
                    "source":      method_src,
                }
    except Exception as e:
        print(f"[WARN] Gagal parse test metadata: {e}")
    return meta


def _infer_desc_from_source(method_name: str, source: str) -> str:
    """
    Inferensikan deskripsi singkat dari nama method & source kode.
    Dipakai jika tidak ada docstring.
    """
    # Bersihkan nama method jadi kalimat
    name = method_name.replace("test_", "").replace("_", " ")

    # Cari assert / raises untuk tahu what is tested
    lines = [l.strip() for l in source.splitlines()]
    assertions = [l for l in lines if l.startswith("assert ") or "pytest.raises" in l]

    if assertions:
        return f"{name.capitalize()} — {assertions[0][:80]}"
    return name.capitalize()


def _infer_input_expected(method_name: str, source: str) -> tuple:
    """
    Ekstrak input & expected dari source kode secara heuristik.
    Returns (input_str, expected_str)
    """
    lines = [l.strip() for l in source.splitlines()]

    # Cari assert lines
    asserts = [l for l in lines if l.startswith("assert ")]
    raises  = [l for l in lines if "pytest.raises" in l]

    input_hints = []
    expected_hints = []

    # Parametrize: nama test sudah mengandung nilai [val-grade]
    if "[" in method_name and "-" in method_name:
        bracket = method_name.split("[")[-1].rstrip("]")
        parts = bracket.split("-")
        if len(parts) >= 2:
            input_hints.append(parts[0])
            expected_hints.append(parts[-1])

    # Untuk test parametrize: sudah dapat input & expected dari bracket nama, skip source scan
    is_parametrize = "[" in method_name and len(input_hints) > 0

    if not is_parametrize:
        # Dari assert statements
        for a in asserts[:2]:
            if "==" in a:
                parts = a.split("==", 1)
                val = parts[1].strip().strip('"').strip("'")
                # Abaikan variabel (huruf kecil semua, tidak ada angka/titik)
                if not (val.isidentifier() and val.islower()):
                    expected_hints.append(val)
            elif "in h" in a:
                expected_hints.append(a.replace("assert ", "").strip()[:60])

        # Dari raises
        for r in raises[:1]:
            m = ""
            if "match=" in r:
                try:
                    m = r.split("match=")[1].split(")")[0].strip().strip('"').strip("'")
                    expected_hints.append(f"raises ValueError (match='{m}')")
                except Exception:
                    expected_hints.append("raises ValueError")
            else:
                expected_hints.append("raises ValueError")

        # Cari call args sebagai input hint
        for l in lines:
            l = l.strip()
            if any(fn in l for fn in ["hitung_nilai_akhir(", "tentukan_grade(", "tentukan_status_lulus(", "tentukan_predikat(", "tentukan_remedial("]):
                try:
                    start = l.index("(") + 1
                    end   = l.rindex(")")
                    args  = l[start:end][:60]
                    input_hints.append(args)
                except Exception:
                    pass
                break
            if "buat_input(" in l:
                try:
                    start = l.index("(") + 1
                    end   = l.rindex(")")
                    args  = l[start:end][:60] or "default"
                    input_hints.append(args)
                except Exception:
                    input_hints.append("buat_input()")
                break

    input_str    = ", ".join(dict.fromkeys(input_hints))[:80]  or "–"
    expected_str = ", ".join(dict.fromkeys(expected_hints))[:80] or "–"
    return input_str, expected_str


# ─── Endpoint: jalankan pytest secara programatik ───────────────────────────
@app.route("/testing/run", methods=["POST"])
def run_tests():
    try:
        base_dir    = os.path.dirname(os.path.abspath(__file__))
        test_file   = os.path.join(base_dir, "tests", "test_penilaian_mahasiswa.py")
        report_path = os.path.join(base_dir, "test_results.json")

        # Fallback: cari test file di root jika tidak ada di tests/
        if not os.path.exists(test_file):
            test_file = os.path.join(base_dir, "test_penilaian_mahasiswa.py")

        # Parse metadata sebelum run
        meta = _parse_test_metadata(test_file)

        # Pastikan pytest-json-report terinstall
        result = subprocess.run(
            [
                sys.executable, "-m", "pytest",
                test_file,
                "-v",
                "--tb=short",
                "--json-report",
                f"--json-report-file={report_path}",
                "--no-header",
            ],
            capture_output=True,
            text=True,
            cwd=base_dir,
        )

        terminal_output = result.stdout + result.stderr

        # Baca JSON report
        if not os.path.exists(report_path):
            return jsonify({
                "success": False,
                "error": (
                    "File test_results.json tidak ditemukan. "
                    "Pastikan pytest-json-report terinstall:\n"
                    "  pip install pytest-json-report\n\n"
                    f"Terminal output:\n{terminal_output}"
                )
            }), 500

        with open(report_path, "r", encoding="utf-8") as f:
            report = json.load(f)

        # Parsing tiap test dengan metadata lengkap
        tests = []
        for t in report.get("tests", []):
            nodeid = t["nodeid"]
            # nodeid = "tests/test_...py::ClassName::test_name"  atau
            #          "test_...py::ClassName::test_name"
            parts = nodeid.split("::")
            class_name = parts[-2] if len(parts) >= 3 else "–"
            test_name  = parts[-1] if len(parts) >= 2 else nodeid

            duration_ms = round(t.get("call", {}).get("duration", 0) * 1000, 2)
            outcome     = t["outcome"]  # "passed" | "failed" | "error"

            # Ambil pesan error jika ada
            error_msg = ""
            if outcome in ("failed", "error"):
                longrepr = t.get("call", {}).get("longrepr", "")
                error_msg = longrepr if isinstance(longrepr, str) else str(longrepr)

            # Ambil metadata dari parser
            meta_key  = f"{class_name}::{test_name}"
            test_meta = meta.get(meta_key, {})
            src       = test_meta.get("source", "")
            method_doc = test_meta.get("method_doc", "")
            class_doc  = test_meta.get("class_desc", "")

            # Deskripsi: docstring method > inferensi dari nama
            desc = method_doc or _infer_desc_from_source(test_name, src)

            # Input & Expected: inferensi dari source
            input_str, expected_str = _infer_input_expected(test_name, src)

            tests.append({
                "nodeid":      nodeid,
                "class_name":  class_name,
                "class_desc":  class_doc,
                "test_name":   test_name,
                "desc":        desc,
                "input":       input_str,
                "expected":    expected_str,
                "outcome":     outcome,
                "duration_ms": duration_ms,
                "error_msg":   error_msg,
            })

        summary        = report.get("summary", {})
        duration_total = round(report.get("duration", 0), 3)

        # Susun per class untuk frontend
        classes = {}
        for t in tests:
            cn = t["class_name"]
            if cn not in classes:
                classes[cn] = {
                    "class_name": cn,
                    "class_desc": t["class_desc"],
                    "tests": [],
                    "passed": 0,
                    "failed": 0,
                }
            classes[cn]["tests"].append(t)
            if t["outcome"] == "passed":
                classes[cn]["passed"] += 1
            else:
                classes[cn]["failed"] += 1

        return jsonify({
            "success":         True,
            "summary":         summary,
            "duration":        duration_total,
            "tests":           tests,
            "classes":         list(classes.values()),
            "terminal_output": terminal_output,
            "exit_code":       result.returncode,
        })

    except Exception as e:
        import traceback
        return jsonify({"success": False, "error": str(e) + "\n" + traceback.format_exc()}), 500


@app.route("/rekap/data")
def rekap_data():
    try:
        return jsonify(ambil_semua_penilaian())
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/rekap/hapus/<int:record_id>", methods=["POST"])
def hapus_satu(record_id):
    try:
        ok = hapus_penilaian_by_id(record_id)
        return jsonify({"success": ok})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/rekap/hapus-semua", methods=["POST"])
def hapus_semua():
    try:
        n = hapus_semua_penilaian()
        return jsonify({"success": True, "deleted": n})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)