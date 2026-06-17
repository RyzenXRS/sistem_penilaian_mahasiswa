/**
 * main.js – Logika antarmuka halaman input penilaian
 * Grade UNEJ: A, AB, B, BC, C, CD, D, DE, E
 */

const form        = document.getElementById("formNilai");
const errorBanner = document.getElementById("errorMsg");
const resultPanel = document.getElementById("resultPanel");
const btnHitung   = document.getElementById("btnHitung");

// Warna per grade UNEJ
const GRADE_COLORS = {
  A:  "#014BAA",
  AB: "#1260AA",
  B:  "#1A7A4A",
  BC: "#7A6A00",
  C:  "#B07400",
  CD: "#A03A00",
  D:  "#C04A00",
  DE: "#880A0A",
  E:  "#B01010",
};

const NILAI_FIELDS = ["tugas", "kuis", "keaktifan", "kehadiran", "uts", "uas"];

document.querySelectorAll('input[type="number"]').forEach(function(input) {
  input.addEventListener('keydown', function(e) {
    // 1. Blokir tombol e, E, plus (+), minus (-), dan koma (,)
    if (['e', 'E', '+', '-', ','].includes(e.key)) {
      e.preventDefault();
    }
    
    // 2. Blokir titik HANYA jika form masih kosong (mencegah titik doang di awal)
    // Jika sudah ada angka (misal "9"), maka titik akan diizinkan (menjadi "9.")
    if (e.key === '.' && this.value === '') {
      e.preventDefault();
    }
  });
  
  // Event 'input' (this.value = ...) dihapus total agar tidak bentrok 
  // dengan bawaan type="number" yang menyebabkan kursor error.
});
// =========================================================================

function validasiKlien() {
  const errors = [];
  const highlights = [];
  const nim  = document.getElementById("nim").value.trim();
  const nama = document.getElementById("nama").value.trim();
  if (!nim)  { errors.push("NIM tidak boleh kosong.");  highlights.push("nim"); }
  if (!nama) { errors.push("Nama tidak boleh kosong."); highlights.push("nama"); }

  for (const field of NILAI_FIELDS) {
    const el  = document.getElementById(field);
    const raw = el.value.trim();
    const label = el.closest(".field-group").querySelector("label")
                   ?.firstChild?.textContent?.trim() || field;
    if (raw === "") {
      errors.push(`${label} tidak boleh kosong.`);
      highlights.push(field);
      continue;
    }
    const v = parseFloat(raw);
    if (isNaN(v)) {
      errors.push(`${label} harus berupa angka.`);
      highlights.push(field);
    } else if (v < 0) {
      errors.push(`${label} tidak boleh negatif (dimasukkan: ${v}).`);
      highlights.push(field);
    } else if (v > 100) {
      errors.push(`${label} tidak boleh lebih dari 100 (dimasukkan: ${v}).`);
      highlights.push(field);
    }
  }
  return { errors, highlights };
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  sembunyikanError();
  bersihkanHighlight();
  const { errors: clientErrors, highlights } = validasiKlien();
  if (clientErrors.length > 0) {
    tampilError(clientErrors, highlights);
    return;
  }
  setLoading(true);
  try {
    const formData = new FormData(form);
    const resp = await fetch("/nilai", { method: "POST", body: formData });
    const json = await resp.json();
    if (!resp.ok || json.errors) {
      const serverErrors = json.errors || [json.error || "Terjadi kesalahan server."];
      tampilError(serverErrors);
      return;
    }
    tampilHasil(json.hasil);
  } catch (err) {
    tampilError(["Tidak dapat terhubung ke server. Periksa koneksi dan coba lagi."]);
  } finally {
    setLoading(false);
  }
});

function tampilHasil(h) {
  document.getElementById("r-nim").textContent      = h.nim;
  document.getElementById("r-nama").textContent     = h.nama;
  document.getElementById("r-na").textContent       = h.nilai_akhir.toFixed(2);
  document.getElementById("r-grade").textContent    = h.grade;
  document.getElementById("r-predikat").textContent = h.predikat;
  document.getElementById("r-status").textContent   = h.status;
  document.getElementById("r-remedial").textContent = h.remedial;

  const color = GRADE_COLORS[h.grade] || "#014BAA";
  const pct   = h.nilai_akhir;
  const circle = document.getElementById("scoreCircle");
  circle.style.setProperty("--pct", pct);
  circle.style.background = `conic-gradient(${color} calc(${pct} * 1%), #EFE9E4 0%)`;

  const gradeBox = document.getElementById("gradeBox");
  gradeBox.style.borderLeftColor = color;
  document.getElementById("r-grade").style.color = color;

  const statusChip = document.getElementById("statusChip");
  if (h.status === "Lulus") {
    statusChip.style.background = "rgba(26,122,74,.12)";
    statusChip.style.color = "#1A7A4A";
  } else {
    statusChip.style.background = "rgba(176,16,16,.10)";
    statusChip.style.color = "#B01010";
  }

  const remChip = document.getElementById("remedialChip");
  if (h.remedial === "Tidak Perlu Remedial") {
    remChip.style.background = "rgba(26,122,74,.10)";
    remChip.style.color = "#1A7A4A";
  } else {
    remChip.style.background = "rgba(192,74,0,.10)";
    remChip.style.color = "#C04A00";
  }

  const komponen = [
    { lbl: "Tugas",   val: h.tugas,     bobot: 0.10 },
    { lbl: "Kuis",    val: h.kuis,      bobot: 0.20 },
    { lbl: "Aktif",   val: h.keaktifan, bobot: 0.05 },
    { lbl: "Hadir",   val: h.kehadiran, bobot: 0.05 },
    { lbl: "UTS",     val: h.uts,       bobot: 0.30 },
    { lbl: "UAS",     val: h.uas,       bobot: 0.30 },
  ];

  const container = document.getElementById("breakdownBars");
  container.innerHTML = komponen.map(k => `
    <div class="bar-row">
      <span class="bar-lbl">${k.lbl}</span>
      <div class="bar-track">
        <div class="bar-fill" style="width:${k.val}%; background:${color};"></div>
      </div>
      <span class="bar-val">${k.val.toFixed(0)}</span>
    </div>
  `).join("");

  resultPanel.style.display = "block";
  resultPanel.scrollIntoView({ behavior: "smooth", block: "start" });
}

function tutupHasil() {
  resultPanel.style.display = "none";
  form.reset();
  sembunyikanError();
  bersihkanHighlight();
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function tampilError(errors, highlights = []) {
  if (errors.length === 1) {
    errorBanner.innerHTML = `<div class="error-title">⚠ Terdapat kesalahan input</div>${escapeHtml(errors[0])}`;
  } else {
    const items = errors.map(e => `<li>${escapeHtml(e)}</li>`).join("");
    errorBanner.innerHTML = `<div class="error-title">⚠ Terdapat ${errors.length} kesalahan input</div><ul>${items}</ul>`;
  }
  errorBanner.style.display = "block";
  highlights.forEach(id => {
    const el = document.getElementById(id);
    if (el) el.classList.add("input-error");
  });
  errorBanner.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

function sembunyikanError() {
  errorBanner.style.display = "none";
  errorBanner.innerHTML = "";
}

function bersihkanHighlight() {
  document.querySelectorAll(".input-error").forEach(el => el.classList.remove("input-error"));
}

function setLoading(state) {
  btnHitung.disabled = state;
  document.querySelector(".btn-text").style.display   = state ? "none" : "inline";
  document.querySelector(".btn-loader").style.display = state ? "inline" : "none";
}

function escapeHtml(str) {
  return str.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;");
}

[...NILAI_FIELDS, "nim", "nama"].forEach(id => {
  const el = document.getElementById(id);
  if (el) {
    el.addEventListener("input", () => {
      el.classList.remove("input-error");
      if (!document.querySelector(".input-error")) sembunyikanError();
    });
  }
});