import os
import sys
import time
import importlib.util
import importlib.machinery

_LOKASI = os.path.dirname(os.path.abspath(__file__))

def _impor(awalan, nama_modul, atribut):
    folder = (_LOKASI, os.path.join(_LOKASI, "..", "backend"),
              os.path.join(_LOKASI, "..", "back"))
    for d in folder:
        if not os.path.isdir(d):
            continue
        for nama in os.listdir(d):
            low = nama.lower()
            if low.startswith(awalan) and os.path.splitext(low)[1] in ("", ".py"):
                path = os.path.join(d, nama)
                if not os.path.isfile(path):
                    continue
                loader = importlib.machinery.SourceFileLoader(nama_modul, path)
                spec = importlib.util.spec_from_loader(nama_modul, loader)
                modul = importlib.util.module_from_spec(spec)
                loader.exec_module(modul)
                if hasattr(modul, atribut):
                    return modul
    raise SystemExit("Berkas " + awalan.upper() + " tidak ditemukan. Taruh di folder "
                     "yang sama dengan berkas ini.")

_M1 = _impor("m1", "m1_pesanan", "LayananM1")
_M2 = _impor("m2", "m2_antrean", "LayananM2")
LayananM1, LayananM2 = _M1.LayananM1, _M2.LayananM2
Pesanan, Hasil = _M1.Pesanan, _M1.Hasil
format_ms, format_jam = _M1.format_ms, _M1.format_jam
format_rupiah = _M1.format_rupiah
REGULER, PRIORITAS, VIP = _M1.REGULER, _M1.PRIORITAS, _M1.VIP

KUNCI_VALID = ("oid", "harga", "selesai")
BATAS_INSERTION = 20000
BELUM_SELESAI = 10 ** 9
_DETAIL = "--detail" in sys.argv
_LULUS = [0]

def fmt(n):
    return ("-" if n < 0 else "") + format_rupiah(abs(n))

class Pencacah:
    __slots__ = ("banding", "pindah")

    def __init__(self):
        self.banding = self.pindah = 0

    def reset(self):
        self.banding = self.pindah = 0

def ekstrak_kunci(A, kunci):
    if kunci not in KUNCI_VALID:
        raise ValueError("kunci harus salah satu dari: oid, harga, selesai")
    if kunci == "oid":
        return [p.oid for p in A]
    if kunci == "harga":
        return [p.harga for p in A]
    return [BELUM_SELESAI if p.t_selesai is None else p.t_selesai for p in A]

def insertion_sort(A, kunci, pencacah=None):
    c = pencacah if pencacah is not None else Pencacah()
    K, banding, pindah = ekstrak_kunci(A, kunci), 0, 0
    for i in range(1, len(A)):
        kk, pp, j = K[i], A[i], i - 1
        while j >= 0:
            banding += 1
            if K[j] <= kk:
                break
            K[j + 1], A[j + 1] = K[j], A[j]
            pindah += 1
            j -= 1
        if j + 1 != i:
            K[j + 1], A[j + 1] = kk, pp
            pindah += 1
    c.banding += banding
    c.pindah += pindah
    return A

def _gabung(K, B, ak, ab, lo, mid, hi, c):
    for i in range(lo, hi):
        ak[i], ab[i] = K[i], B[i]
    i, j, k, banding = lo, mid, lo, 0
    while i < mid and j < hi:
        banding += 1
        if ak[i] <= ak[j]:
            K[k], B[k] = ak[i], ab[i]
            i += 1
        else:
            K[k], B[k] = ak[j], ab[j]
            j += 1
        k += 1
    while i < mid:
        K[k], B[k] = ak[i], ab[i]
        i += 1
        k += 1
    while j < hi:
        K[k], B[k] = ak[j], ab[j]
        j += 1
        k += 1
    c.banding += banding
    c.pindah += hi - lo

def _urut(K, B, ak, ab, lo, hi, c):
    if hi - lo > 1:
        mid = (lo + hi) // 2
        _urut(K, B, ak, ab, lo, mid, c)
        _urut(K, B, ak, ab, mid, hi, c)
        _gabung(K, B, ak, ab, lo, mid, hi, c)

def merge_sort(A, kunci, pencacah=None):
    c = pencacah if pencacah is not None else Pencacah()
    K, B = ekstrak_kunci(A, kunci), list(A)
    n = len(A)
    _urut(K, B, [None] * n, [None] * n, 0, n, c)
    return B

def linear_search(A, target, pencacah=None):
    c = pencacah if pencacah is not None else Pencacah()
    for i, p in enumerate(A):
        c.banding += 1
        if p.oid == target:
            return i
    return -1

def binary_search(A, target, pencacah=None):
    c = pencacah if pencacah is not None else Pencacah()
    lo, hi = 0, len(A) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        c.banding += 1
        if A[mid].oid == target:
            return mid
        if A[mid].oid < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1

def normal_oid(teks):
    t = teks.strip()
    if t and t[0] in "oO":
        t = "O" + t[1:]
    angka = t[2:] if t.startswith("O-") else t
    if angka and all("0" <= ch <= "9" for ch in angka):
        return "O-" + ("0" * (6 - len(angka))) + angka
    return t

class LayananM3:
    def __init__(self, m1=None, m2=None):
        self.m1 = m1 if m1 is not None else LayananM1()
        self.m2 = m2 if m2 is not None else LayananM2()
        self._indeks = self._versi = None
        self.ms_bangun_indeks = 0.0

    def muat(self, path):
        h1, h2 = self.m1.muat(path), self.m2.muat(path)
        self._indeks = self._versi = None
        ket = (fmt(h1.nilai) + " pesanan masuk Array M1 | " + fmt(h2.nilai)
               + " pesanan ANTRE masuk antrean M2")
        return Hasil("M3 - load", h1.nilai, h1.ms + h2.ms, 0, ket)

    def _ambil(self, sumber, n):
        return (self.m2.melingkar if sumber == "antrean" else self.m1.array).ke_list(0, n)

    @staticmethod
    def _nama_sumber(sumber):
        return "antrean M2" if sumber == "antrean" else "data M1"

    def urutkan_insertion(self, n=10, kunci="harga", sumber="semua"):
        if kunci not in KUNCI_VALID:
            return Hasil("M3 - insertion sort", None, 0.0, 0,
                         "kunci tidak valid (pilih: oid, harga, selesai)")
        if n > BATAS_INSERTION:
            return Hasil("M3 - insertion sort", None, 0.0, 0,
                         "DITOLAK: batasnya " + fmt(BATAS_INSERTION)
                         + " baris, pakai merge sort untuk data penuh")
        data, c = self._ambil(sumber, n), Pencacah()
        t0 = time.perf_counter()
        insertion_sort(data, kunci, c)
        ms = (time.perf_counter() - t0) * 1000
        ket = (fmt(len(data)) + " pesanan terurut menurut " + kunci + " ("
               + self._nama_sumber(sumber) + ") | " + fmt(c.banding)
               + " perbandingan, " + fmt(c.pindah) + " pemindahan")
        return Hasil("M3 - insertion sort", data, ms, c.banding, ket)

    def urutkan_merge(self, n=None, kunci="harga", sumber="semua"):
        if kunci not in KUNCI_VALID:
            return Hasil("M3 - merge sort", None, 0.0, 0,
                         "kunci tidak valid (pilih: oid, harga, selesai)")
        data, c = self._ambil(sumber, n), Pencacah()
        t0 = time.perf_counter()
        hasil = merge_sort(data, kunci, c)
        ms = (time.perf_counter() - t0) * 1000
        ket = (fmt(len(hasil)) + " pesanan terurut menurut " + kunci + " ("
               + self._nama_sumber(sumber) + ") | " + fmt(c.banding)
               + " perbandingan, " + fmt(c.pindah) + " pemindahan")
        return Hasil("M3 - merge sort", hasil, ms, c.banding, ket)

    def bandingkan_sort(self, n=2000, kunci="harga", sumber="semua"):
        a, b = self.urutkan_insertion(n, kunci, sumber), self.urutkan_merge(n, kunci, sumber)
        if a.nilai is None:
            return a
        identik = len(a.nilai) == len(b.nilai) and all(x is y for x, y in zip(a.nilai, b.nilai))
        ket = ("insertion " + fmt(a.langkah) + " perbandingan (" + format_ms(a.ms)
               + ") vs merge " + fmt(b.langkah) + " perbandingan (" + format_ms(b.ms)
               + ") | hasil identik baris per baris: " + ("YA" if identik else "TIDAK"))
        return Hasil("M3 - banding sort", (a, b, identik), a.ms + b.ms, 0, ket)

    def laporan_harian(self, sumber="semua"):
        h = self.urutkan_merge(None, "selesai", sumber)
        return Hasil("M3 - laporan", h.nilai, h.ms, h.langkah, "laporan harian: " + h.keterangan)

    def tabel_n_vs_banding(self, daftar_n=(250, 500, 1000, 2000, 4000), kunci="harga"):
        hasil = []
        for n in daftar_n:
            a, b = self.urutkan_insertion(n, kunci), self.urutkan_merge(n, kunci)
            hasil.append((n, a.langkah, b.langkah, a.ms, b.ms))
        return hasil

    def cari_linear(self, oid, sumber="semua"):
        target, data, c = normal_oid(oid), self._ambil(sumber, None), Pencacah()
        t0 = time.perf_counter()
        idx = linear_search(data, target, c)
        ms = (time.perf_counter() - t0) * 1000
        if idx < 0:
            ket = (target + " tidak ditemukan | " + fmt(c.banding)
                   + " perbandingan (menyentuh seluruh " + self._nama_sumber(sumber) + ")")
            return Hasil("M3 - linear", None, ms, c.banding, ket)
        return Hasil("M3 - linear", (idx, data[idx]), ms, c.banding,
                     "ditemukan di indeks " + fmt(idx) + " | " + fmt(c.banding) + " perbandingan")

    def _versi_data(self):
        a, n = self.m1.array, len(self.m1.array)
        if not n:
            return (0, "", "", "")
        return (n, a.get(0).oid, a.get(n // 2).oid, a.get(n - 1).oid)

    def bangun_indeks_oid(self, paksa=False):
        versi = self._versi_data()
        if not paksa and self._indeks is not None and self._versi == versi:
            return Hasil("M3 - indeks", len(self._indeks), 0.0, 0,
                         "indeks oid sudah ada (dibangun sebelumnya), dipakai ulang")
        c, data = Pencacah(), self._ambil("semua", None)
        t0 = time.perf_counter()
        self._indeks = merge_sort(data, "oid", c)
        ms = (time.perf_counter() - t0) * 1000
        self._versi, self.ms_bangun_indeks = versi, ms
        ket = ("daftar terurut oid dibangun sekali (merge sort) " + format_ms(ms)
               + " | " + fmt(c.banding) + " perbandingan")
        return Hasil("M3 - indeks", len(self._indeks), ms, c.banding, ket)

    def cari_binary(self, oid):
        target = normal_oid(oid)
        hb, c = self.bangun_indeks_oid(), Pencacah()
        t0 = time.perf_counter()
        idx = binary_search(self._indeks, target, c)
        ms = (time.perf_counter() - t0) * 1000
        if idx < 0:
            ket = target + " tidak ditemukan | " + fmt(c.banding) + " perbandingan | " + hb.keterangan
            return Hasil("M3 - binary", None, ms, c.banding, ket)
        ket = ("ditemukan di baris ke-" + fmt(idx + 1) + " dari " + fmt(len(self._indeks))
               + " | " + fmt(c.banding) + " perbandingan | " + hb.keterangan)
        return Hasil("M3 - binary", (idx, self._indeks[idx]), ms, c.banding, ket)

    def stats(self):
        return (("baris_m1", len(self.m1.array)), ("antrean_m2", len(self.m2.melingkar)),
                ("indeks_oid_ada", int(self._indeks is not None)),
                ("batas_insertion", BATAS_INSERTION))

def _cek(kondisi, pesan):
    if not kondisi:
        raise AssertionError("GAGAL: " + pesan)
    _LULUS[0] += 1
    if _DETAIL:
        print("  OK  " + pesan)

def _p(serial, harga, selesai=None):
    return Pesanan("T-" + ("0" * (4 - len(str(serial)))) + str(serial),
                   "x", "r", "m", harga, 3, 0, selesai, "DONE")

def _acak(n, mod, benih):
    hasil, x = [], benih
    for i in range(n):
        x = (x * 1103515245 + 12345) % 2147483648
        hasil.append(_p(i, (x // 65536) % mod))
    return hasil

def _salin(A):
    return list(A)

def _terurut(A, kunci):
    K = ekstrak_kunci(A, kunci)
    return all(K[i - 1] <= K[i] for i in range(1, len(K)))

def _stabil(A, kunci):
    K = ekstrak_kunci(A, kunci)
    return all(K[i - 1] != K[i] or A[i - 1].oid <= A[i].oid for i in range(1, len(K)))

def _sama_persis(A, B):
    return len(A) == len(B) and all(x is y for x, y in zip(A, B))

def uji_mandiri():
    if _DETAIL:
        print("\n" + "=" * 78 + "\n0. UJI MANDIRI (kebenaran logika)\n" + "=" * 78)
    kasus = (
        ("acak+duplikat", _acak(300, 20, 7)),
        ("sudah terurut", [_p(i, i) for i in range(300)]),
        ("terbalik", [_p(i, 300 - i) for i in range(300)]),
        ("semua duplikat", [_p(i, 5) for i in range(300)]),
    )
    for nama, data in kasus:
        a, b = insertion_sort(_salin(data), "harga"), merge_sort(data, "harga")
        _cek(_terurut(a, "harga") and _terurut(b, "harga"), "kedua sort benar pada data " + nama)
        _cek(_stabil(a, "harga") and _stabil(b, "harga"), "kedua sort STABIL pada data " + nama)
        _cek(_sama_persis(a, b), "hasil identik baris per baris pada data " + nama)
    _cek(merge_sort([], "harga") == [] and insertion_sort([], "harga") == [], "larik kosong aman")
    satu = [_p(1, 9)]
    _cek(merge_sort(satu, "harga")[0] is satu[0], "satu elemen aman")
    ganjil = _acak(1001, 1000, 3)
    rg = merge_sort(ganjil, "harga")
    _cek(len(rg) == 1001 and _terurut(rg, "harga"), "merge sort n ganjil tidak kehilangan data di ujung")
    campur = [_p(0, 1, 500), _p(1, 1), _p(2, 1, 100), _p(3, 1), _p(4, 1, 300)]
    r = merge_sort(campur, "selesai")
    _cek(r[0].oid == "T-0002" and r[2].oid == "T-0000" and r[3].oid == "T-0001"
         and r[4].oid == "T-0003", "kunci selesai: yang kosong di akhir, urutan relatif terjaga")
    c1, c2, c3, c4 = Pencacah(), Pencacah(), Pencacah(), Pencacah()
    d1, d2 = _acak(1000, 100000, 11), _acak(2000, 100000, 11)
    insertion_sort(_salin(d1), "harga", c1)
    insertion_sort(_salin(d2), "harga", c2)
    merge_sort(d1, "harga", c3)
    merge_sort(d2, "harga", c4)
    r_ins, r_mrg = c2.banding / c1.banding, c4.banding / c3.banding
    _cek(3.5 < r_ins < 4.5, "n x2 -> perbandingan insertion sort ~4x (terukur " + str(round(r_ins, 2)) + "x)")
    _cek(2.0 <= r_mrg < 2.3, "n x2 -> perbandingan merge sort ~2x (terukur " + str(round(r_mrg, 2)) + "x)")
    A = [Pesanan("O-" + ("0" * (6 - len(str(i)))) + str(i), "x", "r", "m", 1, 3, 0, None, "DONE")
         for i in range(1, 100)]
    _cek(binary_search(A, "O-000050") == 49, "binary search: elemen tengah")
    _cek(binary_search(A, "O-000001") == 0, "binary search: elemen paling kiri")
    _cek(binary_search(A, "O-000099") == 98, "binary search: elemen paling kanan")
    _cek(binary_search(A, "O-999999") == -1 and binary_search(A, "O-000000") == -1,
         "binary search: tidak ada")
    _cek(binary_search([], "O-000001") == -1, "binary search: larik kosong")
    _cek(linear_search(A, "O-000077") == 76 and linear_search(A, "O-123456") == -1,
         "linear search: ada & tidak ada")
    _cek(normal_oid("137442") == "O-137442" and normal_oid("o-42") == "O-000042",
         "normalisasi input oid")
    cb = Pencacah()
    besar = [Pesanan("O-" + ("0" * (6 - len(str(i)))) + str(i), "x", "r", "m", 1, 3, 0, None, "DONE")
             for i in range(1, 1001)]
    binary_search(besar, "O-000001", cb)
    _cek(cb.banding <= 10, "binary search: <= 10 perbandingan untuk 1.000 data")
    if _DETAIL:
        print("  Semua uji mandiri lulus")
    return _LULUS[0]

def _cari_csv():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if args:
        return args[0]
    kandidat = (os.path.join(_LOKASI, "..", "data", "pesanan.csv"),
                os.path.join(_LOKASI, "data", "pesanan.csv"),
                os.path.join(_LOKASI, "pesanan.csv"),
                os.path.join(os.getcwd(), "data", "pesanan.csv"),
                os.path.join(os.getcwd(), "pesanan.csv"))
    for p in kandidat:
        if os.path.exists(p):
            return p
    raise SystemExit("pesanan.csv tidak ditemukan. Taruh di folder data/ "
                     "atau beri path sebagai argumen.")

def _sel(banding, ms):
    return fmt(banding).rjust(12) + " | " + format_ms(ms).rjust(10)

def _garis(judul):
    print("\n" + "=" * 78 + "\n" + judul + "\n" + "=" * 78)

def main():
    n_cek = uji_mandiri()
    svc = LayananM3()
    muat = svc.muat(_cari_csv())
    n_m1, n_m2 = len(svc.m1.array), len(svc.m2.melingkar)
    baris = svc.tabel_n_vs_banding((250, 500, 1000, 2000, 4000), "harga")
    banding = svc.bandingkan_sort(2000, "harga")
    penuh = svc.urutkan_merge(None, "harga")
    svc.urutkan_insertion(200000, "harga")
    lap = svc.laporan_harian()
    data, belum = lap.nilai, 0
    while data[len(data) - 1 - belum].t_selesai is None:
        belum += 1
    pertama, terakhir = data[0], data[len(data) - 1 - belum]
    lin, bin1 = svc.cari_linear("O-137442"), svc.cari_binary("O-137442")
    ms_indeks = svc.ms_bangun_indeks
    lin0, bin0 = svc.cari_linear("O-999999"), svc.cari_binary("O-999999")
    tot_l = tot_b = 0
    ms_l = ms_b = 0.0
    target = ("O-000500", "O-050000", "O-100000", "O-150000")
    for i in range(200):
        a, b = svc.cari_linear(target[i % 4]), svc.cari_binary(target[i % 4])
        tot_l += a.langkah
        tot_b += b.langkah
        ms_l += a.ms
        ms_b += b.ms
    print("M3 - SORT & SEARCH")
    print("Uji mandiri : " + str(n_cek) + " pengecekan lulus")
    print("Data        : " + fmt(n_m1) + " pesanan (M1) | " + fmt(n_m2) + " ANTRE (M2)")
    print("\n" + "SORT (kunci harga)".ljust(20) + "insertion sort".ljust(26)
          + "merge sort".ljust(26) + "rasio")
    print("n".ljust(10) + "perbandingan |      waktu   " + "perbandingan |      waktu")
    print("-" * 78)
    for n, a, b, ma, mb in baris:
        print(fmt(n).ljust(10) + _sel(a, ma) + "   " + _sel(b, mb) + "   " + str(round(a / b, 1)) + "x")
    print("200.000".ljust(10) + ("ditolak (maks " + fmt(BATAS_INSERTION) + ")").ljust(26)
          + "   " + _sel(penuh.langkah, penuh.ms))
    print("Hasil insertion = merge baris per baris (stabil, n=2.000) : "
          + ("YA" if banding.nilai[2] else "TIDAK"))
    print("\nLAPORAN HARIAN (kunci selesai) : " + fmt(len(data)) + " pesanan | "
          + fmt(lap.langkah) + " banding | " + format_ms(lap.ms))
    print("  selesai paling awal : " + pertama.oid + " " + format_jam(pertama.t_selesai)
          + " | paling akhir : " + terakhir.oid + " " + format_jam(terakhir.t_selesai)
          + " | belum selesai (di akhir) : " + fmt(belum))
    print("\nSEARCH O-137442")
    print("  linear : indeks " + fmt(lin.nilai[0]) + " | " + fmt(lin.langkah)
          + " banding | " + format_ms(lin.ms))
    print("  binary : baris " + fmt(bin1.nilai[0] + 1) + " | " + fmt(bin1.langkah)
          + " banding | " + format_ms(bin1.ms) + "  (indeks oid dibangun sekali: "
          + format_ms(ms_indeks) + ")")
    print("  tidak ada (O-999999) : linear " + fmt(lin0.langkah) + " banding | binary "
          + fmt(bin0.langkah) + " banding")
    print("  200x cari : linear " + format_ms(ms_l) + " (" + fmt(tot_l) + " banding) vs binary "
          + format_ms(ms_b) + " (" + fmt(tot_b) + " banding) + indeks sekali " + format_ms(ms_indeks))

if __name__ == "__main__":
    main()
