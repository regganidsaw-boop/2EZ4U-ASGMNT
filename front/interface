
import os
import sys
import time
import importlib.util
import importlib.machinery

import tkinter as tk
from tkinter import ttk, filedialog, messagebox

_LOKASI = os.path.dirname(os.path.abspath(__file__))
BATAS_TAMPIL = 200          


def _muat_m3():
    folder = (os.path.join(_LOKASI, "..", "back"),
              os.path.join(_LOKASI, "..", "backend"),
              os.path.join(_LOKASI, "back"),
              _LOKASI)
    for d in folder:
        if not os.path.isdir(d):
            continue
        for n in os.listdir(d):
            low = n.lower()
            if not low.startswith("m3"):
                continue
            if os.path.splitext(low)[1] not in ("", ".py"):
                continue
            p = os.path.join(d, n)
            if not os.path.isfile(p):
                continue
            if d not in sys.path:
                sys.path.insert(0, d)
            loader = importlib.machinery.SourceFileLoader("m3_sortsearch", p)
            spec = importlib.util.spec_from_loader("m3_sortsearch", loader)
            modul = importlib.util.module_from_spec(spec)
            loader.exec_module(modul)
            if hasattr(modul, "LayananM3"):
                return modul
    raise SystemExit("Berkas M3 tidak ditemukan. Taruh M1, M2, M3 di folder 'back' "
                     "(sejajar dengan folder 'front').")


_M3 = _muat_m3()
_M1 = _M3._M1
LayananM3 = _M3.LayananM3
format_ms = _M1.format_ms
format_rupiah = _M1.format_rupiah
format_jam = _M1.format_jam
VIP = _M1.VIP
PRIORITAS = _M1.PRIORITAS
REGULER = _M1.REGULER
NAMA_JENIS = _M1.NAMA_JENIS


def _angka(x):
    """12345 -> '12.345' (pemisah ribuan gaya Indonesia, tanpa format spec berkurung)."""
    s = str(int(x))
    neg = s.startswith("-")
    if neg:
        s = s[1:]
    out = ""
    k = 0
    i = len(s) - 1
    while i >= 0:
        if k == 3:
            out = "." + out
            k = 0
        out = s[i] + out
        k += 1
        i -= 1
    return ("-" if neg else "") + out


def _cari_csv():
    kandidat = (os.path.join(_LOKASI, "..", "data", "pesanan.csv"),
                os.path.join(_LOKASI, "data", "pesanan.csv"),
                os.path.join(_LOKASI, "pesanan.csv"),
                os.path.join(os.getcwd(), "data", "pesanan.csv"),
                os.path.join(os.getcwd(), "pesanan.csv"))
    for p in kandidat:
        if os.path.exists(p):
            return os.path.normpath(p)
    return ""



class Tampil:
    """Satu hasil yang siap digambar: ringkasan + tabel + keterangan perintah."""

    def __init__(self, perintah, modul, ms=0.0, ringkas=None, kolom=(), baris=None,
                 galat=False):
        self.perintah = perintah
        self.modul = modul
        self.ms = ms
        self.ringkas = ringkas if ringkas is not None else []
        self.kolom = kolom
        self.baris = baris if baris is not None else []
        self.galat = galat


KOLOM_PESANAN = ("#", "oid", "pelanggan", "resto", "menu", "harga",
                 "jenis", "masuk", "selesai", "status")


def _baris_pesanan(daftar, mulai=0):
    hasil = []
    n = len(daftar)
    if n > BATAS_TAMPIL:
        n = BATAS_TAMPIL
    for i in range(n):
        p = daftar[i]
        hasil.append((mulai + i, p.oid, p.pelanggan, p.resto, p.menu,
                      format_rupiah(p.harga), NAMA_JENIS[p.prioritas],
                      format_jam(p.t_masuk), format_jam(p.t_selesai), p.status))
    return hasil


def _detail_pesanan(p):
    hasil = []
    for k, v in p.baris():
        hasil.append((k, v))
    return hasil


def _ke_int(teks, nama, minimal=None, maksimal=None):
    t = str(teks).strip().replace(".", "").replace(",", "")
    if t == "":
        raise ValueError(nama + " tidak boleh kosong")
    try:
        x = int(t)
    except ValueError:
        raise ValueError(nama + " harus berupa angka bulat")
    if minimal is not None and x < minimal:
        raise ValueError(nama + " minimal " + _angka(minimal))
    if maksimal is not None and x > maksimal:
        raise ValueError(nama + " maksimal " + _angka(maksimal))
    return x


def _jenis_dari(teks):
    t = str(teks).strip().upper()
    if t.startswith("VIP"):
        return VIP
    if t.startswith("PRIO"):
        return PRIORITAS
    return REGULER


class Kontroler:
    """Jembatan UI -> M1/M2/M3. Satu pintu: jalankan(kode, nilai)."""

    def __init__(self):
        self.m3 = LayananM3()
        self.m1 = self.m3.m1
        self.m2 = self.m3.m2
        self.dimuat = False
        self.path = ""

    def _sinkron_oid(self):
        berikut = max(self.m1._oid_berikut, self.m2._oid_berikut)
        self.m1._oid_berikut = berikut
        self.m2._oid_berikut = berikut

    def status(self):
        if not self.dimuat:
            return "Data belum dimuat - pilih 'Muat pesanan.csv'"
        return ("M1 Array " + _angka(len(self.m1.array))
                + " | M1 LinkedList " + _angka(len(self.m1.linked))
                + " | Antrean M2 naif " + _angka(len(self.m2.naif))
                + " / circular " + _angka(len(self.m2.melingkar))
                + " | undo " + str(len(self.m2.undo))
                + " / redo " + str(len(self.m2.redo)))


    def jalankan(self, kode, v):
        """v = list isian (teks). Mengembalikan Tampil; kesalahan -> Tampil.galat."""
        t0 = time.perf_counter()
        try:
            if kode != "load" and not self.dimuat:
                return Tampil(kode, "UI", 0.0,
                              ["Data belum dimuat. Jalankan 'Muat pesanan.csv' dulu."],
                              galat=True)
            t = self._eksekusi(kode, v)
        except (ValueError, IndexError, OSError) as e:
            ms = (time.perf_counter() - t0) * 1000.0
            return Tampil(kode, "UI", ms, ["ERROR: " + str(e)], galat=True)
        return t

    def _eksekusi(self, kode, v):
        if kode == "load":
            return self._load(v[0])
        if kode == "m1_lihat":
            return self._m1_lihat(v[0], v[1])
        if kode == "m1_daftar":
            return self._m1_daftar(v[0], v[1], v[2])
        if kode == "m1_tambah_reguler":
            return self._m1_tambah(REGULER, v)
        if kode == "m1_tambah_prioritas":
            return self._m1_tambah(PRIORITAS, v)
        if kode == "m1_tambah_vip":
            return self._m1_tambah(VIP, v)
        if kode == "m1_hapus":
            return self._m1_hapus(v[0])
        if kode == "stack_postfix":
            return self._postfix(v[0])
        if kode == "stack_undo":
            return self._undo_redo(True)
        if kode == "stack_redo":
            return self._undo_redo(False)
        if kode == "stack_riwayat":
            return self._riwayat()
        if kode == "queue_enqueue":
            return self._enqueue(v)
        if kode == "queue_dequeue_naif":
            return self._dequeue(True, v[0])
        if kode == "queue_dequeue_circular":
            return self._dequeue(False, v[0])
        if kode == "queue_lihat":
            return self._queue_lihat(v[0], v[1])
        if kode == "sort_insertion":
            return self._sort_insertion(v)
        if kode == "sort_merge":
            return self._sort_merge(v)
        if kode == "sort_banding":
            return self._sort_banding(v)
        if kode == "sort_laporan":
            return self._sort_laporan(v[0])
        if kode == "sort_tabel":
            return self._sort_tabel(v[0])
        if kode == "search_linear":
            return self._search_linear(v[0], v[1])
        if kode == "search_binary":
            return self._search_binary(v[0])
        if kode == "search_banding":
            return self._search_banding(v[0])
        raise ValueError("aksi tidak dikenal: " + str(kode))

 
    def _load(self, path):
        path = str(path).strip().strip('"')
        if path == "":
            raise ValueError("path pesanan.csv tidak boleh kosong")
        if not os.path.exists(path):
            raise ValueError("berkas tidak ditemukan: " + path)
        h = self.m3.muat(path)
        self._sinkron_oid()
        self.dimuat = True
        self.path = path
        daftar = self.m1.daftar("array", 0, 100)
        return Tampil("LOAD " + os.path.basename(path), "M3 - load", h.ms,
                      [h.keterangan,
                       "menampilkan " + _angka(len(daftar)) + " pesanan pertama dari total "
                       + _angka(len(self.m1.array))],
                      KOLOM_PESANAN, _baris_pesanan(daftar, 0))


    def _m1_lihat(self, struktur, idx):
        i = _ke_int(idx, "indeks", 0)
        h = self.m1.lihat(struktur, i)
        return Tampil(struktur.upper() + ".lihat(" + str(i) + ")", h.modul, h.ms,
                      [h.keterangan], ("field", "isi"), _detail_pesanan(h.nilai))

    def _m1_daftar(self, struktur, mulai, jumlah):
        a = _ke_int(mulai, "mulai", 0)
        n = _ke_int(jumlah, "jumlah", 1, BATAS_TAMPIL)
        daftar = self.m1.daftar(struktur, a, n)
        return Tampil(struktur.upper() + ".daftar(" + str(a) + ", " + str(n) + ")",
                      "M1 - " + struktur, 0.0,
                      [str(len(daftar)) + " pesanan dari indeks " + _angka(a)
                       + " | total " + _angka(len(self.m1.array if struktur == "array"
                                                    else self.m1.linked))],
                      KOLOM_PESANAN, _baris_pesanan(daftar, a))

    def _m1_tambah(self, jenis, v):
        pelanggan = str(v[0]).strip()
        if pelanggan == "":
            raise ValueError("nama pelanggan tidak boleh kosong")
        resto = str(v[1]).strip() or "kafe-teknik"
        menu = str(v[2]).strip() or "roti-bakar"
        harga = _ke_int(v[3], "harga", 0)
        self._sinkron_oid()
        a, b = self.m1.tambah_keduanya(jenis, pelanggan, resto, menu, harga)
        self._sinkron_oid()
        baris = ((" ARRAY", _angka(a.langkah) + " elemen digeser", format_ms(a.ms), a.keterangan),
                 ("LINKED LIST", _angka(b.langkah) + " simpul ditelusuri", format_ms(b.ms),
                  b.keterangan))
        return Tampil("TAMBAH " + NAMA_JENIS[jenis] + " " + a.nilai.oid, "M1 - array + linked list",
                      a.ms + b.ms,
                      [a.nilai.oid + " (" + NAMA_JENIS[jenis] + ") masuk ke KEDUA struktur | "
                       "Array " + _angka(len(self.m1.array)) + " = LinkedList "
                       + _angka(len(self.m1.linked))],
                      ("struktur", "biaya", "waktu", "keterangan"), baris)

    def _m1_hapus(self, idx):
        i = _ke_int(idx, "indeks", 0)
        n = len(self.m1.array)
        if i >= n:
            raise ValueError("indeks " + str(i) + " di luar jangkauan (0.." + str(n - 1) + ")")
        a = self.m1.hapus("array", i)
        b = self.m1.hapus("linkedlist", i)
        baris = ((" ARRAY", _angka(a.langkah) + " elemen digeser", format_ms(a.ms), a.keterangan),
                 ("LINKED LIST", _angka(b.langkah) + " simpul ditelusuri", format_ms(b.ms),
                  b.keterangan))
        return Tampil("HAPUS indeks " + str(i), "M1 - array + linked list", a.ms + b.ms,
                      [a.nilai.oid + " dihapus dari KEDUA struktur | sisa "
                       + _angka(len(self.m1.array))],
                      ("struktur", "biaya", "waktu", "keterangan"), baris)

 
    def _postfix(self, ekspresi):
        h = self.m2.stack_postfix(ekspresi)
        if h.nilai is None:
            return Tampil("POSTFIX", h.modul, h.ms, [h.keterangan], galat=True)
        postfix_teks, total, baris = h.nilai
        return Tampil("POSTFIX " + str(ekspresi).strip(), h.modul, h.ms,
                      ["postfix: " + postfix_teks, "TOTAL : " + format_rupiah(total)],
                      ("langkah", "token", "tindakan", "stack", "keluaran"), baris)

    def _undo_redo(self, undo):
        h = self.m2.undo_last() if undo else self.m2.redo_last()
        return Tampil("UNDO" if undo else "REDO", h.modul, h.ms, [h.keterangan],
                      ("riwayat (terlama -> terbaru)",), self._baris_riwayat())

    def _baris_riwayat(self):
        hasil = []
        for t in self.m2.history():
            hasil.append((t,))
        return hasil

    def _riwayat(self):
        h = self._baris_riwayat()
        return Tampil("RIWAYAT", "M2 - stack", 0.0,
                      [str(len(h)) + " aksi di tumpukan undo | redo " + str(len(self.m2.redo))],
                      ("riwayat (terlama -> terbaru)",), h)


    def _enqueue(self, v):
        pelanggan = str(v[0]).strip()
        if pelanggan == "":
            raise ValueError("nama pelanggan tidak boleh kosong")
        resto = str(v[1]).strip() or "kafe-teknik"
        menu = str(v[2]).strip() or "roti-bakar"
        harga = _ke_int(v[3], "harga", 0)
        self._sinkron_oid()
        h = self.m2.queue_enqueue(pelanggan, resto, menu, harga, _jenis_dari(v[4]))
        self._sinkron_oid()
        return Tampil("ENQUEUE " + h.nilai.oid, h.modul, h.ms, [h.keterangan],
                      KOLOM_PESANAN, _baris_pesanan([h.nilai], len(self.m2.melingkar) - 1))

    def _dequeue(self, naif, k):
        n = _ke_int(k, "jumlah", 1)
        h = self.m2.queue_dequeue_naive(n) if naif else self.m2.queue_dequeue_circular(n)
        ket = [h.keterangan]
        if naif:
            ket.append("naif: tiap dequeue menggeser seluruh sisa antrean (O(n)); "
                       "coba circular untuk bandingkan")
        return Tampil("DEQUEUE " + ("naif" if naif else "circular") + " x" + str(n),
                      h.modul, h.ms, ket, KOLOM_PESANAN, _baris_pesanan(h.nilai))

    def _queue_lihat(self, jenis, jumlah):
        n = _ke_int(jumlah, "jumlah", 1, BATAS_TAMPIL)
        nama = "naif" if str(jenis).lower().startswith("naif") else "circular"
        daftar = self.m2.isi_antrean(nama, n)
        total = len(self.m2.naif) if nama == "naif" else len(self.m2.melingkar)
        return Tampil("ANTREAN " + nama, "M2 - queue " + nama, 0.0,
                      [str(len(daftar)) + " paling depan dari " + _angka(total) + " antrean"],
                      KOLOM_PESANAN, _baris_pesanan(daftar))


    @staticmethod
    def _sumber(teks):
        return "antrean" if str(teks).lower().startswith("antrean") else "semua"

    def _sort_insertion(self, v):
        n = _ke_int(v[0], "n", 1)
        h = self.m3.urutkan_insertion(n, str(v[1]).strip(), self._sumber(v[2]))
        return self._tampil_sort("INSERTION SORT n=" + _angka(n), h)

    def _sort_merge(self, v):
        t = str(v[0]).strip()
        n = None if t == "" else _ke_int(t, "n", 1)
        h = self.m3.urutkan_merge(n, str(v[1]).strip(), self._sumber(v[2]))
        return self._tampil_sort("MERGE SORT " + ("semua" if n is None else _angka(n)), h)

    def _tampil_sort(self, perintah, h):
        if h.nilai is None:
            return Tampil(perintah, h.modul, h.ms, [h.keterangan], galat=True)
        ket = [h.keterangan]
        if len(h.nilai) > BATAS_TAMPIL:
            ket.append("tabel hanya menampilkan " + str(BATAS_TAMPIL) + " baris pertama")
        return Tampil(perintah, h.modul, h.ms, ket, KOLOM_PESANAN, _baris_pesanan(h.nilai))

    def _sort_banding(self, v):
        n = _ke_int(v[0], "n", 1)
        h = self.m3.bandingkan_sort(n, str(v[1]).strip(), self._sumber(v[2]))
        if h.nilai is None:
            return Tampil("BANDING SORT", h.modul, h.ms, [h.keterangan], galat=True)
        a, b, identik = h.nilai
        baris = (("insertion sort", _angka(a.langkah), format_ms(a.ms), "O(n^2)"),
                 ("merge sort", _angka(b.langkah), format_ms(b.ms), "O(n log n)"))
        return Tampil("BANDING SORT n=" + _angka(n), h.modul, h.ms, [h.keterangan],
                      ("algoritma", "perbandingan", "waktu", "kompleksitas"), baris)

    def _sort_laporan(self, sumber):
        h = self.m3.laporan_harian(self._sumber(sumber))
        ket = [h.keterangan, "urut waktu selesai; pesanan yang belum selesai di bagian akhir"]
        return Tampil("LAPORAN HARIAN", h.modul, h.ms, ket, KOLOM_PESANAN,
                      _baris_pesanan(h.nilai))

    def _sort_tabel(self, kunci):
        k = str(kunci).strip()
        baris = []
        for n, ci, cm, mi, mm in self.m3.tabel_n_vs_banding((250, 500, 1000, 2000, 4000), k):
            rasio = "-"
            if cm > 0:
                rasio = str(round(ci / cm, 1)) + "x"
            baris.append((_angka(n), _angka(ci), _angka(cm), format_ms(mi), format_ms(mm), rasio))
        return Tampil("TABEL n vs PERBANDINGAN", "M3 - sort", 0.0,
                      ["n dilipatduakan: insertion ~4x lebih banyak, merge ~2x"],
                      ("n", "insertion", "merge", "ms insertion", "ms merge", "rasio"), baris)

    def _search_linear(self, oid, sumber):
        h = self.m3.cari_linear(oid, self._sumber(sumber))
        return self._tampil_cari("LINEAR " + str(oid).strip(), h)

    def _search_binary(self, oid):
        h = self.m3.cari_binary(oid)
        return self._tampil_cari("BINARY " + str(oid).strip(), h)

    def _tampil_cari(self, perintah, h):
        if h.nilai is None:
            return Tampil(perintah, h.modul, h.ms, [h.keterangan], galat=True)
        idx, p = h.nilai
        baris = [("indeks", _angka(idx))]
        for k, x in p.baris():
            baris.append((k, x))
        return Tampil(perintah, h.modul, h.ms, [h.keterangan], ("field", "isi"), baris)

    def _search_banding(self, oid):
        a = self.m3.cari_linear(oid, "semua")
        b = self.m3.cari_binary(oid)
        baris = (("linear search", _angka(a.langkah), format_ms(a.ms), "O(n)"),
                 ("binary search", _angka(b.langkah), format_ms(b.ms), "O(log n)"))
        ket = [a.keterangan, b.keterangan]
        return Tampil("BANDING SEARCH " + str(oid).strip(), "M3 - search", a.ms + b.ms, ket,
                      ("algoritma", "perbandingan", "waktu", "kompleksitas"), baris,
                      galat=(a.nilai is None))



class Isian:
    """Satu kolom isian. tipe: 'teks' | 'angka' | 'pilih'."""

    def __init__(self, label, awal="", tipe="teks", opsi=(), petunjuk=""):
        self.label = label
        self.awal = awal
        self.tipe = tipe
        self.opsi = opsi
        self.petunjuk = petunjuk


class Menu:
    def __init__(self, grup, label, aksi, judul, sub, isian=(), tombol="Jalankan",
                 catatan="", tetap=False):
        self.grup = grup
        self.label = label
        self.aksi = aksi
        self.judul = judul
        self.sub = sub
        self.isian = isian
        self.tombol = tombol
        self.catatan = catatan
        self.tetap = tetap


_JENIS = ("REGULER", "PRIORITAS", "VIP")
_KUNCI = ("harga", "oid", "selesai")
_SUMBER = ("semua (Array M1)", "antrean (circular M2)")
_PELANGGAN = Isian("Pelanggan", "Raina Firmansyah", "teks")
_RESTO = Isian("Resto", "kafe-teknik", "teks")
_MENUF = Isian("Menu", "roti-bakar", "teks")
_HARGA = Isian("Harga (Rp)", "12000", "angka")


def daftar_menu():
    m = []
    m.append(Menu("DATA", "Load", "load",
                  "Muat Data Pesanan",
                  "Satu pintu: CSV dimuat ke Array & Linked List (M1) dan antrean (M2) sekaligus.",
                  (Isian("Path CSV", _cari_csv(), "teks", (), "klik 'Cari...' untuk memilih"),),
                  "Muat Data",
                  "Setelah dimuat, M1, M2, dan M3 memakai data yang sama. Pesanan berstatus "
                  "ANTRE masuk ke dua antrean M2 (naif & circular)."))

    m.append(Menu("M1 - DATA PESANAN", "ARRAY - LIHAT PESANAN", "m1_lihat_array",
                  "Array - Lihat Pesanan",
                  "Akses langsung lewat indeks, 0 langkah penelusuran.",
                  (Isian("Indeks", "0", "angka"),), "Lihat",
                  "Array: akses indeks O(1) - tidak perlu menelusuri elemen lain."))
    m.append(Menu("M1 - DATA PESANAN", "ARRAY - DAFTAR PESANAN", "m1_daftar_array",
                  "Array - Daftar Pesanan", "Tampilkan sebagian isi Array.",
                  (Isian("Mulai", "0", "angka"), Isian("Jumlah", "20", "angka")), "Tampilkan",
                  "Tabel dibatasi " + str(BATAS_TAMPIL) + " baris agar tetap ringan."))

    m.append(Menu("M1 - DATA PESANAN", "LINKEDLIST - LIHAT PESANAN", "m1_lihat_linkedlist",
                  "Linked List - Lihat Pesanan",
                  "Harus menelusuri simpul dari head sampai indeks tujuan.",
                  (Isian("Indeks", "150000", "angka"),), "Lihat",
                  "Linked list: akses indeks O(n). Bandingkan jumlah simpul ditelusuri "
                  "dengan Array yang 0 langkah."))
    m.append(Menu("M1 - DATA PESANAN", "LINKEDLIST - DAFTAR PESANAN", "m1_daftar_linkedlist",
                  "Linked List - Daftar Pesanan", "Tampilkan sebagian isi Linked List.",
                  (Isian("Mulai", "0", "angka"), Isian("Jumlah", "20", "angka")), "Tampilkan",
                  "Isi Linked List selalu identik dengan Array."))

    kopi = "Pesanan baru masuk ke Array DAN Linked List sekaligus (isi tetap identik)."
    m.append(Menu("M1 - DATA PESANAN", "TAMBAH PESANAN REGULER", "m1_tambah_reguler",
                  "Tambah Pesanan REGULER", "Masuk paling belakang antrean.",
                  (_PELANGGAN, _RESTO, _MENUF, _HARGA), "Tambah",
                  kopi + " REGULER: di belakang - Array 0 geseran, Linked List lewat tail."))
    m.append(Menu("M1 - DATA PESANAN", "TAMBAH PESANAN PRIORITAS", "m1_tambah_prioritas",
                  "Tambah Pesanan PRIORITAS", "Masuk di tengah antrean (indeks n/2).",
                  (_PELANGGAN, _RESTO, _MENUF, _HARGA), "Tambah",
                  kopi + " PRIORITAS: di tengah - Array menggeser separuh elemen, "
                  "Linked List menelusuri separuh simpul."))
    m.append(Menu("M1 - DATA PESANAN", "TAMBAH PESANAN VIP", "m1_tambah_vip",
                  "Tambah Pesanan VIP", "Masuk paling depan antrean.",
                  (_PELANGGAN, _RESTO, _MENUF, _HARGA), "Tambah",
                  kopi + " VIP: di depan - Array menggeser SEMUA elemen, Linked List cukup "
                  "mengubah head."))
    m.append(Menu("M1 - DATA PESANAN", "HAPUS PESANAN", "m1_hapus",
                  "Hapus Pesanan", "Hapus pada indeks tertentu di Array dan Linked List.",
                  (Isian("Indeks", "0", "angka"),), "Hapus",
                  "Hapus dari kedua struktur supaya isinya tetap sama."))

    m.append(Menu("M2 - STACK DAN QUEUE", "STACK - POSTFIX (MESIN KASIR)", "stack_postfix",
                  "Stack - Hitung Struk Kasir",
                  "Ekspresi infix diubah ke postfix lalu dievaluasi dengan stack.",
                  (Isian("Ekspresi", "(12000*2)+(15000*1)+(9000*1)", "teks",
                         (), "operator + - * / dan kurung"),),
                  "Hitung",
                  "Tabel menunjukkan isi stack tiap langkah. Operan kanan di-pop lebih dulu."))
    m.append(Menu("M2 - STACK DAN QUEUE", "STACK - UNDO", "stack_undo", "Stack - Undo",
                  "Batalkan aksi terakhir (enqueue / dequeue).", (), "Undo",
                  "Aksi ditarik dari tumpukan undo dan dipindah ke tumpukan redo."))
    m.append(Menu("M2 - STACK DAN QUEUE", "STACK - REDO", "stack_redo", "Stack - Redo",
                  "Kerjakan ulang aksi yang baru dibatalkan.", (), "Redo",
                  "Aksi baru mengosongkan tumpukan redo."))
    m.append(Menu("M2 - STACK DAN QUEUE", "STACK - RIWAYAT AKSI", "stack_riwayat", "Stack - Riwayat",
                  "Isi tumpukan undo dari yang terlama sampai terbaru.", (), "Tampilkan",
                  "Riwayat berasal dari tumpukan undo yang sama dengan tombol Undo."))

    m.append(Menu("M2 - STACK DAN QUEUE", "QUEUE - ENQUEUE", "queue_enqueue",
                  "Queue - Enqueue", "Pesanan baru masuk ke belakang KEDUA antrean.",
                  (_PELANGGAN, _RESTO, _MENUF, _HARGA,
                   Isian("Jenis", "REGULER", "pilih", _JENIS)), "Enqueue",
                  "Enqueue O(1) di naif maupun circular. Aksinya masuk riwayat undo."))
    m.append(Menu("M2 - STACK DAN QUEUE", "QUEUE - DEQUEUE NAIF", "queue_dequeue_naive",
                  "Queue - Dequeue Naif",
                  "Cabut dari depan dengan menggeser seluruh sisa antrean.",
                  (Isian("Jumlah", "100", "angka"),), "Dequeue",
                  "Naif: tiap dequeue menggeser semua elemen (O(n)). Lihat jumlah geseran "
                  "yang sangat besar."))
    m.append(Menu("M2 - STACK DAN QUEUE", "QUEUE - DEQUEUE CIRCULAR", "queue_dequeue_circular",
                  "Queue - Dequeue Circular",
                  "Cabut dari depan dengan memajukan penunjuk front (modulo).",
                  (Isian("Jumlah", "100", "angka"),), "Dequeue",
                  "Circular: 0 geseran (O(1)). Hasil sama dengan naif, kerjanya jauh lebih ringan."))
    m.append(Menu("M2 - STACK DAN QUEUE", "QUEUE - ISI ANTREAN", "queue_lihat",
                  "Queue - Isi Antrean", "Pesanan paling depan di antrean.",
                  (Isian("Antrean", "circular", "pilih", ("circular", "naif")),
                   Isian("Jumlah", "20", "angka")), "Tampilkan",
                  "Kedua antrean berisi pesanan yang sama persis."))

    m.append(Menu("M3 - SORT DAN SEARCH", "SORT - INSERTION SORT", "sort_insertion",
                  "Sort - Insertion Sort", "Stabil, O(n^2), dibatasi 20.000 baris.",
                  (Isian("n (jumlah baris)", "2000", "angka"),
                   Isian("Kunci", "harga", "pilih", _KUNCI),
                   Isian("Sumber", _SUMBER[0], "pilih", _SUMBER)), "Urutkan",
                  "Pengurutan memakai salinan; data asli M1/M2 tidak berubah."))
    m.append(Menu("M3 - SORT DAN SEARCH", "SORT - MERGE SORT", "sort_merge",
                  "Sort - Merge Sort", "Stabil, O(n log n). Kosongkan n untuk semua data.",
                  (Isian("n (kosong = semua)", "", "angka"),
                   Isian("Kunci", "harga", "pilih", _KUNCI),
                   Isian("Sumber", _SUMBER[0], "pilih", _SUMBER)), "Urutkan",
                  "Untuk 200.000 baris butuh beberapa detik - tunggu sampai status selesai."))
    m.append(Menu("M3 - SORT DAN SEARCH", "SORT - BANDING ALGORITMA", "sort_banding",
                  "Sort - Banding", "Dua algoritma pada data yang sama.",
                  (Isian("n (jumlah baris)", "2000", "angka"),
                   Isian("Kunci", "harga", "pilih", _KUNCI),
                   Isian("Sumber", _SUMBER[0], "pilih", _SUMBER)), "Banding",
                  "Hasil kedua sort identik baris per baris karena keduanya stabil."))
    m.append(Menu("M3 - SORT DAN SEARCH", "SORT - LAPORAN HARIAN", "sort_laporan",
                  "Sort - Laporan Harian", "Semua pesanan urut waktu selesai (merge sort).",
                  (Isian("Sumber", _SUMBER[0], "pilih", _SUMBER),), "Buat Laporan",
                  "Pesanan yang belum selesai ditaruh di bagian akhir."))
    m.append(Menu("M3 - SORT DAN SEARCH", "SORT - TABEL N VS PERBANDINGAN", "sort_tabel",
                  "Sort - Tabel n vs Perbandingan",
                  "Pertumbuhan jumlah perbandingan saat n bertambah.",
                  (Isian("Kunci", "harga", "pilih", _KUNCI),), "Buat Tabel",
                  "Bukti empiris: n x2 -> insertion ~4x, merge ~2x."))

    m.append(Menu("M3 - SORT DAN SEARCH", "SEARCH - LINEAR SEARCH", "search_linear",
                  "Search - Linear Search", "Periksa satu per satu dari awal, O(n).",
                  (Isian("Order ID", "O-137442", "teks", (), "boleh angka saja: 137442"),
                   Isian("Sumber", _SUMBER[0], "pilih", _SUMBER)), "Cari",
                  "Linear search tidak butuh data terurut."))
    m.append(Menu("M3 - SORT DAN SEARCH", "SEARCH - BINARY SEARCH", "search_binary",
                  "Search - Binary Search", "Belah dua daftar terurut oid, O(log n).",
                  (Isian("Order ID", "O-137442", "teks", (), "boleh angka saja: 137442"),), "Cari",
                  "Daftar terurut dibangun SEKALI dengan merge sort lalu dipakai ulang."))
    m.append(Menu("M3 - SORT DAN SEARCH", "SEARCH - BANDING ALGORITMA", "search_banding",
                  "Search - Banding", "Dua metode mencari order yang sama.",
                  (Isian("Order ID", "O-137442", "teks", (), "boleh angka saja: 137442"),),
                  "Banding", "Binary ~17 perbandingan untuk 200.000 data."))
    return m

BIRU_LANGIT = "#4cb7ee"
BIRU = "#1f8fdc"
BIRU_TUA = "#0b4f8a"
AQUA = "#3fd0e6"
HIJAU = "#6fcf3a"
HIJAU_TUA = "#2f9a1f"
KUNING = "#ffe45e"
KUNING_TUA = "#f3b400"
KUNING_PUCAT = "#fff8d0"
PERAK_1 = "#fbfdff"
PERAK_2 = "#e4ebf1"
PERAK_3 = "#c2ccd5"
PERAK_GARIS = "#9fb0be"
TEKS = "#12344f"
TEKS_SOFT = "#4f6b82"
LANGIT_ATAS = "#d5eefc"
LANGIT_BAWAH = "#f1fae9"


def _rgb(h):
    return (int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16))


def _hex(r, g, b):
    return "#%02x%02x%02x" % (int(r), int(g), int(b))


def _campur(a, b, t):
    ra, ga, ba = _rgb(a)
    rb, gb, bb = _rgb(b)
    return _hex(ra + (rb - ra) * t, ga + (gb - ga) * t, ba + (bb - ba) * t)


def pilih_font(root, kandidat):
    import tkinter.font as tkfont
    ada = tkfont.families(root)
    for k in kandidat:
        if k in ada:
            return k
    return kandidat[len(kandidat) - 1]


def bikin_gambar_kaca(w, h, atas, bawah, garis, radius=8, kilap=0.42):
    """
    Gambar tombol 'kaca' khas Aero: gradasi vertikal, separuh atas lebih terang
    (kilap), tepi membulat, garis tepi tipis. Dibuat dari PhotoImage murni (tanpa PIL).
    """
    img = tk.PhotoImage(width=w, height=h)
    paruh = h // 2
    for y in range(h):
        if y < paruh:
            t = y / float(max(1, paruh))
            warna = _campur(_campur(atas, "#ffffff", kilap), _campur(atas, "#ffffff", kilap * 0.35), t)
        else:
            t = (y - paruh) / float(max(1, h - paruh - 1))
            warna = _campur(atas, bawah, 0.55 + 0.45 * t)
        # inset sudut membulat
        inset = 0
        if y < radius:
            dy = radius - y
            inset = radius - int((radius * radius - dy * dy) ** 0.5)
        elif y >= h - radius:
            dy = y - (h - radius - 1)
            inset = radius - int((radius * radius - dy * dy) ** 0.5)
        if inset > 0:
            for x in range(inset):
                img.transparency_set(x, y, True)
                img.transparency_set(w - 1 - x, y, True)
        x1 = inset
        x2 = w - inset
        if x2 > x1:
            img.put(warna, to=(x1, y, x2, y + 1))
            img.put(garis, to=(x1, y, x1 + 1, y + 1))
            img.put(garis, to=(x2 - 1, y, x2, y + 1))
            if y == 0 or y == h - 1 or inset > 0:
                img.put(garis, to=(x1, y, x2, y + 1))
    return img


class Kaca(tk.Canvas):
    """Tombol kaca berkilap (hover & tekan)."""

    def __init__(self, master, teks, perintah, lebar=150, tinggi=34, atas=BIRU_LANGIT,
                 bawah=BIRU, garis=BIRU_TUA, warna_teks="#ffffff", font=None,
                 rata="tengah", latar=None, radius=10):
        latar = latar if latar is not None else master.cget("bg")
        tk.Canvas.__init__(self, master, width=lebar, height=tinggi, bg=latar,
                           highlightthickness=0, bd=0, cursor="hand2")
        self._perintah = perintah
        self._aktif = True
        self._img_normal = bikin_gambar_kaca(lebar, tinggi, atas, bawah, garis, radius)
        self._img_hover = bikin_gambar_kaca(lebar, tinggi, _campur(atas, "#ffffff", 0.28),
                                            _campur(bawah, "#ffffff", 0.18), garis, radius)
        self._img_tekan = bikin_gambar_kaca(lebar, tinggi, _campur(atas, "#000000", 0.12),
                                            _campur(bawah, "#000000", 0.10), garis, radius, 0.1)
        self._gambar = self.create_image(0, 0, anchor="nw", image=self._img_normal)
        x = lebar // 2
        jangkar = "center"
        if rata == "kiri":
            x = 14
            jangkar = "w"
        self._bayang = self.create_text(x + 1, tinggi // 2 + 1, text=teks, fill=_campur(bawah, "#000000", 0.45),
                                        font=font, anchor=jangkar)
        self._teks = self.create_text(x, tinggi // 2, text=teks, fill=warna_teks, font=font,
                                      anchor=jangkar)
        self.bind("<Enter>", lambda e: self._set(self._img_hover))
        self.bind("<Leave>", lambda e: self._set(self._img_normal))
        self.bind("<ButtonPress-1>", lambda e: self._set(self._img_tekan))
        self.bind("<ButtonRelease-1>", self._lepas)

    def _set(self, img):
        if self._aktif:
            self.itemconfigure(self._gambar, image=img)

    def _lepas(self, e):
        self._set(self._img_hover)
        if self._aktif and 0 <= e.x <= int(self.cget("width")) and 0 <= e.y <= int(self.cget("height")):
            self._perintah()

    def ubah_teks(self, teks):
        self.itemconfigure(self._teks, text=teks)
        self.itemconfigure(self._bayang, text=teks)


class Gradasi(tk.Canvas):
    """Latar gradasi vertikal yang menyesuaikan ukuran."""

    def __init__(self, master, atas, bawah, tinggi=None, **kw):
        tk.Canvas.__init__(self, master, highlightthickness=0, bd=0, **kw)
        if tinggi is not None:
            self.configure(height=tinggi)
        self._atas = atas
        self._bawah = bawah
        self.bind("<Configure>", lambda e: self._gambar(e.width, e.height))

    def _gambar(self, w, h):
        self.delete("grad")
        n = max(1, h)
        langkah = 2
        for y in range(0, n, langkah):
            warna = _campur(self._atas, self._bawah, y / float(n))
            self.create_rectangle(0, y, w, y + langkah, outline=warna, fill=warna, tags="grad")
        self.tag_lower("grad")


class AplikasiUI:
    def __init__(self, root, kontroler):
        self.root = root
        self.k = kontroler
        self.menu = daftar_menu()
        self.aktif = None
        self.var = []
        self.tombol_menu = []
        self.counter = 0
        self.sibuk = False

        self.f_judul = pilih_font(root, ("Segoe UI Semibold", "Segoe UI", "Calibri", "DejaVu Sans"))
        self.f_isi = pilih_font(root, ("Segoe UI", "Calibri", "DejaVu Sans"))
        self.f_mono = pilih_font(root, ("Consolas", "Cascadia Mono", "DejaVu Sans Mono"))

        root.title("2EZ4U APP  -  Struktur Data & Analisa Algoritma")
        root.geometry("1280x780")
        root.minsize(1100, 680)
        root.configure(bg=LANGIT_ATAS)
        self._gaya()
        self._susun()
        self.pilih(0)
        self.root.after(250, self._muat_awal)

    
    def _gaya(self):
        s = ttk.Style(self.root)
        try:
            s.theme_use("clam")
        except tk.TclError:
            pass
        s.configure("Aero.Treeview", background="#ffffff", fieldbackground="#ffffff",
                    foreground=TEKS, rowheight=24, bordercolor=PERAK_GARIS,
                    font=(self.f_isi, 10), borderwidth=0)
        s.configure("Aero.Treeview.Heading", background=PERAK_2, foreground=BIRU_TUA,
                    font=(self.f_judul, 10, "bold"), relief="flat", padding=(6, 5),
                    bordercolor=PERAK_GARIS)
        s.map("Aero.Treeview", background=[("selected", AQUA)], foreground=[("selected", TEKS)])
        s.map("Aero.Treeview.Heading", background=[("active", "#d3e8f7")])
        s.configure("Aero.Vertical.TScrollbar", troughcolor=PERAK_2, background=PERAK_3,
                    bordercolor=PERAK_2, arrowcolor=BIRU_TUA, lightcolor=PERAK_1, darkcolor=PERAK_3)
        s.configure("Aero.Horizontal.TScrollbar", troughcolor=PERAK_2, background=PERAK_3,
                    bordercolor=PERAK_2, arrowcolor=BIRU_TUA, lightcolor=PERAK_1, darkcolor=PERAK_3)
        s.configure("Aero.TCombobox", fieldbackground="#ffffff", background=PERAK_2,
                    bordercolor=PERAK_GARIS, arrowcolor=BIRU_TUA, padding=3)
        s.configure("Aero.Horizontal.TProgressbar", troughcolor=PERAK_2, background=HIJAU,
                    bordercolor=PERAK_GARIS, lightcolor="#a6ec7a", darkcolor=HIJAU_TUA)

    
    def _susun(self):
        r = self.root
        # header bergradasi biru->aqua->hijau dengan gelembung
        self.header = Gradasi(r, "#1d86d6", "#5fd7c8", tinggi=84)
        self.header.pack(fill="x")
        self.header.bind("<Configure>", self._gambar_header)

        badan = tk.Frame(r, bg=LANGIT_ATAS)
        badan.pack(fill="both", expand=True, padx=14, pady=(10, 0))
        badan.columnconfigure(1, weight=1)
        badan.rowconfigure(0, weight=1)

        self._susun_menu(badan)
        self._susun_kanan(badan)

        # status bar perak
        bar = Gradasi(r, PERAK_1, PERAK_3, tinggi=40)
        bar.pack(fill="x", side="bottom", pady=(8, 0))
        self.status = tk.Label(bar, text="", bg=PERAK_2, fg=TEKS, anchor="w", font=(self.f_isi, 9))
        bar.create_window(14, 20, anchor="w", window=self.status)
        self.btn_tutup = Kaca(bar, "Tutup", self.root.destroy, lebar=96, tinggi=28,
                              atas="#ffe98a", bawah=KUNING_TUA, garis="#b98200",
                              warna_teks="#5a3c00", font=(self.f_judul, 10, "bold"),
                              latar=PERAK_2, radius=9)
        bar.bind("<Configure>", lambda e: self._tempatkan_bar(bar, e.width), add="+")
        self._bar = bar
        self._win_tutup = bar.create_window(1180, 20, anchor="e", window=self.btn_tutup)

    def _tempatkan_bar(self, bar, w):
        bar.coords(self._win_tutup, w - 14, 20)

    def _gambar_header(self, e):
        c = self.header
        Gradasi._gambar(c, e.width, e.height)
        c.delete("hias")
        w, h = e.width, e.height
        # gelembung (hanya garis tepi + kilau, tanpa transparansi)
        gel = ((70, 62, 38), (150, 20, 22), (250, 70, 30), (w - 330, 24, 40),
               (w - 210, 64, 24), (w - 110, 28, 34), (w // 2 + 40, 14, 14), (w // 2 - 160, 70, 16))
        for x, y, rr in gel:
            c.create_oval(x - rr, y - rr, x + rr, y + rr, outline="#e8fbff", width=2, tags="hias")
            c.create_oval(x - rr * 0.55, y - rr * 0.7, x - rr * 0.05, y - rr * 0.25,
                          outline="", fill="#f4fdff", tags="hias")
        # kilau kaca di separuh atas
        c.create_rectangle(0, 0, w, h // 2 - 4, outline="", fill=_campur("#1d86d6", "#ffffff", 0.18),
                           stipple="gray25", tags="hias")
        # judul
        c.create_text(30, 31, text="2EZ4U", anchor="w", fill=_campur("#0b4f8a", "#000000", 0.4),
                      font=(self.f_judul, 29, "bold"), tags="hias")
        c.create_text(28, 29, text="2EZ4U", anchor="w", fill="#ffffff",
                      font=(self.f_judul, 29, "bold"), tags="hias")
        c.create_text(32, 62, anchor="w", fill="#ecfbff", font=(self.f_isi, 11),
                      text="Rengganis Dewi Sekar Arum - 5024251044",
                      tags="hias")

    def _susun_menu(self, badan):
        kiri = tk.Frame(badan, bg=PERAK_GARIS, bd=0)
        kiri.grid(row=0, column=0, sticky="ns", padx=(0, 12), pady=(0, 6))
        dalam = tk.Frame(kiri, bg=PERAK_2)
        dalam.pack(fill="both", expand=True, padx=1, pady=1)
        self.kanvas_menu = tk.Canvas(dalam, bg=PERAK_2, width=262, highlightthickness=0, bd=0)
        sb = ttk.Scrollbar(dalam, orient="vertical", command=self.kanvas_menu.yview,
                           style="Aero.Vertical.TScrollbar")
        self.kanvas_menu.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.kanvas_menu.pack(side="left", fill="both", expand=True)
        isi = tk.Frame(self.kanvas_menu, bg=PERAK_2)
        self.kanvas_menu.create_window(0, 0, anchor="nw", window=isi)
        isi.bind("<Configure>", lambda e: self.kanvas_menu.configure(
            scrollregion=self.kanvas_menu.bbox("all")))
        self.kanvas_menu.bind("<Enter>", lambda e: self._roda(True))
        self.kanvas_menu.bind("<Leave>", lambda e: self._roda(False))

        grup_sekarang = ""
        for i in range(len(self.menu)):
            mi = self.menu[i]
            if mi.grup != grup_sekarang:
                grup_sekarang = mi.grup
                warna = HIJAU
                tua = HIJAU_TUA
                if grup_sekarang.startswith("M2"):
                    warna, tua = KUNING, KUNING_TUA
                elif grup_sekarang.startswith("M3"):
                    warna, tua = AQUA, "#1b9fb4"
                elif grup_sekarang.startswith("M1"):
                    warna, tua = BIRU_LANGIT, BIRU
                kepala = Kaca(isi, grup_sekarang, lambda: None, lebar=236, tinggi=26,
                              atas=warna, bawah=tua, garis=tua,
                              warna_teks="#ffffff" if not grup_sekarang.startswith("M2") else "#5a3c00",
                              font=(self.f_judul, 9, "bold"), rata="kiri", latar=PERAK_2, radius=7)
                kepala.configure(cursor="arrow")
                kepala.pack(padx=12, pady=(12, 4))
            b = Kaca(isi, mi.label, (lambda n=i: self.pilih(n)), lebar=236, tinggi=30,
                     atas="#ffffff", bawah="#d9e4ec", garis=PERAK_GARIS, warna_teks=TEKS,
                     font=(self.f_isi, 10), rata="kiri", latar=PERAK_2, radius=8)
            b.pack(padx=12, pady=2)
            self.tombol_menu.append(b)
        tk.Frame(isi, bg=PERAK_2, height=10).pack()

    def _roda(self, aktif):
        if aktif:
            self.root.bind_all("<MouseWheel>", self._gulir)
            self.root.bind_all("<Button-4>", self._gulir)
            self.root.bind_all("<Button-5>", self._gulir)
        else:
            self.root.unbind_all("<MouseWheel>")
            self.root.unbind_all("<Button-4>")
            self.root.unbind_all("<Button-5>")

    def _gulir(self, e):
        if getattr(e, "num", 0) == 4:
            self.kanvas_menu.yview_scroll(-2, "units")
        elif getattr(e, "num", 0) == 5:
            self.kanvas_menu.yview_scroll(2, "units")
        else:
            self.kanvas_menu.yview_scroll(int(-e.delta / 60), "units")

    def _susun_kanan(self, badan):
        kanan = tk.Frame(badan, bg=PERAK_GARIS)
        kanan.grid(row=0, column=1, sticky="nsew", pady=(0, 6))
        k = tk.Frame(kanan, bg="#f7fbfe")
        k.pack(fill="both", expand=True, padx=1, pady=1)
        k.columnconfigure(0, weight=1)
        k.rowconfigure(3, weight=3)
        k.rowconfigure(5, weight=1)

        # judul panel (gradasi perak)
        gj = Gradasi(k, PERAK_1, PERAK_2, tinggi=62)
        gj.grid(row=0, column=0, sticky="ew")
        self.l_judul = tk.Label(gj, text="", bg=PERAK_1, fg=BIRU_TUA, font=(self.f_judul, 15, "bold"),
                                anchor="w")
        self.l_sub = tk.Label(gj, text="", bg=PERAK_1, fg=TEKS_SOFT, font=(self.f_isi, 10), anchor="w")
        gj.create_window(18, 21, anchor="w", window=self.l_judul)
        gj.create_window(18, 44, anchor="w", window=self.l_sub)

        # form
        self.form = tk.Frame(k, bg="#f7fbfe")
        self.form.grid(row=1, column=0, sticky="ew", padx=16, pady=(10, 4))

        # ringkas (pil hijau)
        self.l_ringkas = tk.Label(k, text="", bg="#e6f7d8", fg="#1d5c10", anchor="w", justify="left",
                                  font=(self.f_isi, 10, "bold"), padx=12, pady=6, wraplength=900,
                                  highlightbackground="#a8dc86", highlightthickness=1)
        self.l_ringkas.grid(row=2, column=0, sticky="ew", padx=16, pady=(2, 8))

        # tabel hasil
        tabel = tk.Frame(k, bg=PERAK_GARIS)
        tabel.grid(row=3, column=0, sticky="nsew", padx=16)
        tabel.columnconfigure(0, weight=1)
        tabel.rowconfigure(0, weight=1)
        self.tree = ttk.Treeview(tabel, style="Aero.Treeview", show="headings")
        sy = ttk.Scrollbar(tabel, orient="vertical", command=self.tree.yview,
                           style="Aero.Vertical.TScrollbar")
        sx = ttk.Scrollbar(tabel, orient="horizontal", command=self.tree.xview,
                           style="Aero.Horizontal.TScrollbar")
        self.tree.configure(yscrollcommand=sy.set, xscrollcommand=sx.set)
        self.tree.grid(row=0, column=0, sticky="nsew", padx=1, pady=1)
        sy.grid(row=0, column=1, sticky="ns", pady=1)
        sx.grid(row=1, column=0, sticky="ew", padx=1)
        self.tree.tag_configure("ganjil", background="#f1f9ff")
        self.tree.tag_configure("genap", background="#ffffff")

        # COMMAND log
        tk.Label(k, text="COMMAND", bg="#f7fbfe", fg=BIRU_TUA, font=(self.f_judul, 9, "bold"),
                 anchor="w").grid(row=4, column=0, sticky="ew", padx=18, pady=(8, 0))
        lf = tk.Frame(k, bg=PERAK_GARIS)
        lf.grid(row=5, column=0, sticky="nsew", padx=16, pady=(2, 6))
        lf.columnconfigure(0, weight=1)
        lf.rowconfigure(0, weight=1)
        self.log = tk.Text(lf, height=4, bg="#fcfeff", fg=TEKS, font=(self.f_mono, 9),
                           relief="flat", wrap="none", state="disabled", padx=8, pady=4,
                           insertbackground=TEKS)
        ls = ttk.Scrollbar(lf, orient="vertical", command=self.log.yview, style="Aero.Vertical.TScrollbar")
        self.log.configure(yscrollcommand=ls.set)
        self.log.grid(row=0, column=0, sticky="nsew", padx=1, pady=1)
        ls.grid(row=0, column=1, sticky="ns", pady=1)
        self.log.tag_configure("baru", foreground=BIRU_TUA, font=(self.f_mono, 9, "bold"))
        self.log.tag_configure("galat", foreground="#c0392b", font=(self.f_mono, 9, "bold"))

        # catatan kuning
        self.catatan = tk.Label(k, text="", bg=KUNING_PUCAT, fg="#5d4a00", anchor="w", justify="left",
                                font=(self.f_isi, 10), padx=12, pady=7, wraplength=900,
                                highlightbackground="#efd56a", highlightthickness=1)
        self.catatan.grid(row=6, column=0, sticky="ew", padx=16, pady=(0, 12))
        k.bind("<Configure>", lambda e: self._atur_wrap(e.width))

    def _atur_wrap(self, w):
        lebar = max(300, w - 60)
        self.l_ringkas.configure(wraplength=lebar)
        self.catatan.configure(wraplength=lebar)

  
    def pilih(self, i):
        self.aktif = self.menu[i]
        m = self.aktif
        for j in range(len(self.tombol_menu)):
            b = self.tombol_menu[j]
            if j == i:
                b._img_normal = bikin_gambar_kaca(236, 30, HIJAU, HIJAU_TUA, HIJAU_TUA, 8)
                b.itemconfigure(b._gambar, image=b._img_normal)
                b.itemconfigure(b._teks, fill="#ffffff", font=(self.f_judul, 10, "bold"))
            else:
                b._img_normal = bikin_gambar_kaca(236, 30, "#ffffff", "#d9e4ec", PERAK_GARIS, 8)
                b.itemconfigure(b._gambar, image=b._img_normal)
                b.itemconfigure(b._teks, fill=TEKS, font=(self.f_isi, 10))
        self.l_judul.configure(text=m.judul)
        self.l_sub.configure(text=m.sub)
        self.catatan.configure(text="Catatan:  " + m.catatan)
        self._bangun_form(m)

    def _bangun_form(self, m):
        for w in self.form.winfo_children():
            w.destroy()
        self.var = []
        kolom = 0
        for isi in m.isian:
            kotak = tk.Frame(self.form, bg="#f7fbfe")
            kotak.grid(row=0, column=kolom, sticky="w", padx=(0, 12))
            tk.Label(kotak, text=isi.label, bg="#f7fbfe", fg=TEKS_SOFT,
                     font=(self.f_isi, 9)).pack(anchor="w")
            v = tk.StringVar(value=isi.awal)
            if isi.tipe == "pilih":
                w = ttk.Combobox(kotak, textvariable=v, values=list(isi.opsi), state="readonly",
                                 width=max(12, len(max(isi.opsi, key=len)) + 2),
                                 style="Aero.TCombobox", font=(self.f_isi, 10))
            else:
                lebar = 14
                if isi.label == "Ekspresi":
                    lebar = 46
                elif isi.label == "Path CSV":
                    lebar = 52
                elif isi.label in ("Pelanggan",):
                    lebar = 20
                w = tk.Entry(kotak, textvariable=v, width=lebar, font=(self.f_isi, 10),
                             relief="flat", bg="#ffffff", fg=TEKS, highlightthickness=1,
                             highlightbackground=PERAK_GARIS, highlightcolor=BIRU,
                             insertbackground=TEKS)
                w.bind("<Return>", lambda e: self.jalankan())
            w.pack(anchor="w", ipady=3)
            self.var.append(v)
            kolom += 1
        sisi = tk.Frame(self.form, bg="#f7fbfe")
        sisi.grid(row=0, column=kolom, sticky="sw")
        if m.aksi == "load":
            Kaca(sisi, "Cari...", self._cari_berkas, lebar=84, tinggi=30, atas="#ffffff",
                 bawah="#d9e4ec", garis=PERAK_GARIS, warna_teks=TEKS, font=(self.f_isi, 10),
                 latar="#f7fbfe", radius=8).pack(side="left", padx=(0, 8))
        Kaca(sisi, m.tombol, self.jalankan, lebar=130, tinggi=32, atas="#9be05f", bawah=HIJAU_TUA,
             garis="#25770f", warna_teks="#ffffff", font=(self.f_judul, 10, "bold"),
             latar="#f7fbfe", radius=10).pack(side="left")

    def _cari_berkas(self):
        p = filedialog.askopenfilename(title="Pilih pesanan.csv",
                                       filetypes=(("CSV", "*.csv"), ("Semua berkas", "*.*")))
        if p and len(self.var) > 0:
            self.var[0].set(p)

    
    def _muat_awal(self):
        p = _cari_csv()
        if p != "":
            self.aktif = self.menu[0]
            self.var = [tk.StringVar(value=p)]
            self._eksekusi("load", [p], "Memuat 200.000 pesanan ke M1, M2, M3 ...")
        self.pilih(0)
        self._perbarui_status()

    def jalankan(self):
        m = self.aktif
        kode = m.aksi
        nilai = []
        for v in self.var:
            nilai.append(v.get())
        # menu M1 lihat/daftar per-struktur: struktur disisipkan di depan
        if kode.startswith("m1_lihat_"):
            nilai = [kode[len("m1_lihat_"):]] + nilai
            kode = "m1_lihat"
        elif kode.startswith("m1_daftar_"):
            nilai = [kode[len("m1_daftar_"):]] + nilai
            kode = "m1_daftar"
        elif kode == "queue_dequeue_naive":
            kode = "queue_dequeue_naif"
        self._eksekusi(kode, nilai, "Memproses " + m.label + " ...")

    def _eksekusi(self, kode, nilai, pesan):
        if self.sibuk:
            return
        self.sibuk = True
        self.status.configure(text=pesan + "  (mohon tunggu)")
        self.root.configure(cursor="watch")
        self.root.update_idletasks()
        self.root.update()
        t0 = time.perf_counter()
        t = self.k.jalankan(kode, nilai)
        total = (time.perf_counter() - t0) * 1000.0
        self.root.configure(cursor="")
        self.sibuk = False
        self._tampilkan(t, total)

    def _tampilkan(self, t, total_ms):
        # ringkas
        teks = ""
        for i in range(len(t.ringkas)):
            teks += ("\n" if i > 0 else "") + t.ringkas[i]
        if t.galat:
            self.l_ringkas.configure(text=teks, bg="#fde8e4", fg="#9b2a1a", highlightbackground="#efb0a6")
        else:
            self.l_ringkas.configure(text=teks, bg="#e6f7d8", fg="#1d5c10", highlightbackground="#a8dc86")
        # tabel
        self.tree.delete(*self.tree.get_children())
        if len(t.kolom) > 0:
            self.tree.configure(columns=t.kolom)
            for c in t.kolom:
                self.tree.heading(c, text=c)
                self.tree.column(c, width=self._lebar(c), minwidth=50, anchor="w", stretch=True)
            n = len(t.baris)
            if n > BATAS_TAMPIL:
                n = BATAS_TAMPIL
            for i in range(n):
                self.tree.insert("", "end", values=t.baris[i],
                                 tags=("ganjil" if i % 2 else "genap",))
        # command log (terbaru di atas)
        self.counter += 1
        ms = format_ms(t.ms if t.ms > 0 else total_ms)
        baris = "#" + str(self.counter) + "  " + t.perintah + "  ->  " + t.modul + "   " + ms + "\n"
        self.log.configure(state="normal")
        self.log.insert("1.0", baris, ("galat" if t.galat else "baru",))
        self.log.configure(state="disabled")
        self._perbarui_status()

    @staticmethod
    def _lebar(c):
        if c in ("#", "langkah"):
            return 60
        if c in ("oid", "harga", "jenis", "status", "masuk", "selesai", "token", "stack"):
            return 90
        if c in ("pelanggan", "resto", "menu", "bagian", "ukuran", "struktur", "algoritma",
                 "biaya", "waktu", "field"):
            return 150
        if c in ("tindakan", "keterangan", "keluaran", "isi", "riwayat (terlama -> terbaru)"):
            return 320
        return 120

    def _perbarui_status(self):
        self.status.configure(text=self.k.status())


def main():
    root = tk.Tk()
    try:
        root.iconbitmap(default="")
    except tk.TclError:
        pass
    kontroler = Kontroler()
    AplikasiUI(root, kontroler)
    root.mainloop()


if __name__ == "__main__":
    main()