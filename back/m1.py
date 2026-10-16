import csv
import time
VIP = 1
PRIORITAS = 2
REGULER = 3
NAMA_JENIS = ("", "VIP", "PRIORITAS", "REGULER")  # indeks 1..3
STRUKTUR_ARRAY = "array"
STRUKTUR_LINKED = "linkedlist"

class Pesanan:
    __slots__ = ("oid", "pelanggan", "resto", "menu", "harga",
                 "prioritas", "t_masuk", "t_selesai", "status")

    def __init__(self, oid, pelanggan, resto, menu, harga,
                 prioritas, t_masuk, t_selesai, status):
        self.oid = oid
        self.pelanggan = pelanggan
        self.resto = resto
        self.menu = menu
        self.harga = harga
        self.prioritas = prioritas
        self.t_masuk = t_masuk
        self.t_selesai = t_selesai
        self.status = status

    def baris(self):
        return (
            ("oid", self.oid),
            ("pelanggan", self.pelanggan),
            ("resto", self.resto),
            ("menu", self.menu),
            ("harga", format_rupiah(self.harga)),
            ("prioritas", str(self.prioritas) + " (" + NAMA_JENIS[self.prioritas] + ")"),
            ("masuk", format_jam(self.t_masuk)),
            ("selesai", format_jam(self.t_selesai)),
            ("status", self.status),
        )

    def ringkas(self):
        return (self.oid + " | " + self.pelanggan + " | " + self.resto + " | "
                + self.menu + " | P" + str(self.prioritas) + " | " + self.status)

    def __repr__(self):
        return "Pesanan(" + self.ringkas() + ")"

def format_jam(detik):
    if detik is None:
        return "-"
    j = detik // 3600
    m = (detik % 3600) // 60
    s = detik % 60
    return _dua(j) + ":" + _dua(m) + ":" + _dua(s)

def _dua(n):
    return "0" + str(n) if n < 10 else str(n)

def format_rupiah(angka):
    teks = str(angka)
    hasil = ""
    hitung = 0
    i = len(teks) - 1
    while i >= 0:
        if hitung == 3:
            hasil = "." + hasil
            hitung = 0
        hasil = teks[i] + hasil
        hitung += 1
        i -= 1
    return hasil

class Array:

    def __init__(self, kapasitas=4):
        if kapasitas < 1:
            kapasitas = 1
        self._data = [None] * kapasitas
        self._n = 0
        self._kapasitas = kapasitas
        self.geseran_terakhir = 0
        self.salinan_terakhir = 0
        self.total_salinan = 0
        self.jumlah_resize = 0

    def __len__(self):
        return self._n

    def kapasitas(self):
        return self._kapasitas

    def _reset_hitung(self):
        self.geseran_terakhir = 0
        self.salinan_terakhir = 0

    def _lebarkan(self):
        baru = [None] * (self._kapasitas * 2)
        i = 0
        while i < self._n:                 # salin seluruh isi lama
            baru[i] = self._data[i]
            i += 1
        self._data = baru                  # petak lama dibuang
        self._kapasitas = self._kapasitas * 2
        self.salinan_terakhir += self._n
        self.total_salinan += self._n
        self.jumlah_resize += 1

    def get(self, i):
        self._reset_hitung()
        self._cek_indeks(i, self._n)
        return self._data[i]

    def append(self, v):
        self._reset_hitung()
        if self._n == self._kapasitas:
            self._lebarkan()
        self._data[self._n] = v
        self._n += 1

    def insert(self, i, v):
        self._reset_hitung()
        if i < 0 or i > self._n:
            raise IndexError("indeks sisip di luar jangkauan: " + str(i))
        if self._n == self._kapasitas:
            self._lebarkan()
        k = self._n
        while k > i:                       # geser ke kanan, dari belakang
            self._data[k] = self._data[k - 1]
            k -= 1
            self.geseran_terakhir += 1
        self._data[i] = v
        self._n += 1

    def remove_at(self, i):
        self._reset_hitung()
        self._cek_indeks(i, self._n)
        nilai = self._data[i]
        k = i
        while k < self._n - 1:
            self._data[k] = self._data[k + 1]
            k += 1
            self.geseran_terakhir += 1
        self._data[self._n - 1] = None     # lepas referensi
        self._n -= 1
        return nilai

    def tambah_reguler(self, v):
        self.append(v)                     # paling belakang

    def tambah_prioritas(self, v):
        self.insert(self._n // 2, v)       # tengah barisan

    def tambah_vip(self, v):
        self.insert(0, v)                  # urutan pertama

    def ke_list(self, mulai=0, jumlah=None):
        if jumlah is None or mulai + jumlah > self._n:
            akhir = self._n
        else:
            akhir = mulai + jumlah
        hasil = []
        i = mulai
        while i < akhir:
            hasil.append(self._data[i])
            i += 1
        return hasil
    @staticmethod
    def _cek_indeks(i, n):
        if i < 0 or i >= n:
            raise IndexError("indeks " + str(i) + " di luar jangkauan (0.." + str(n - 1) + ")")

    def stats(self):
        return (("panjang", self._n),
                ("kapasitas", self._kapasitas),
                ("jumlah_resize", self.jumlah_resize),
                ("total_salinan_resize", self.total_salinan))

class Simpul:
    __slots__ = ("nilai", "next")

    def __init__(self, nilai):
        self.nilai = nilai
        self.next = None

class LinkList:

    def __init__(self):
        self.head = None
        self.tail = None
        self._n = 0
        self.telusur_terakhir = 0
        self.total_telusur = 0

    def __len__(self):
        return self._n

    def _catat(self, langkah):
        self.telusur_terakhir = langkah
        self.total_telusur += langkah

    def get(self, i):
        self._cek_indeks(i, self._n)
        cur = self.head
        langkah = 0
        while langkah < i:
            cur = cur.next
            langkah += 1
        self._catat(langkah)
        return cur.nilai

    def append(self, v):
        baru = Simpul(v)
        if self.tail is None:
            self.head = baru
            self.tail = baru
        else:
            self.tail.next = baru
            self.tail = baru
        self._n += 1
        self._catat(0)

    def prepend(self, v):
        baru = Simpul(v)
        baru.next = self.head
        self.head = baru
        if self.tail is None:
            self.tail = baru
        self._n += 1
        self._catat(0)

    def insert(self, i, v):
        if i < 0 or i > self._n:
            raise IndexError("indeks sisip di luar jangkauan: " + str(i))
        if i == 0:
            self.prepend(v)
            return
        if i == self._n:
            self.append(v)
            return
        cur = self.head
        langkah = 0
        while langkah < i - 1:
            cur = cur.next
            langkah += 1
        baru = Simpul(v)
        baru.next = cur.next
        cur.next = baru
        self._n += 1
        self._catat(langkah)

    def remove_at(self, i):
        self._cek_indeks(i, self._n)
        if i == 0:
            nilai = self.head.nilai
            self.head = self.head.next
            if self.head is None:
                self.tail = None
            self._n -= 1
            self._catat(0)
            return nilai
        cur = self.head
        langkah = 0
        while langkah < i - 1:
            cur = cur.next
            langkah += 1
        target = cur.next
        cur.next = target.next
        if target is self.tail:            # yang dicabut adalah ekor
            self.tail = cur
        self._n -= 1
        self._catat(langkah)
        return target.nilai

    def tambah_reguler(self, v):
        self.append(v)                     # paling belakang

    def tambah_prioritas(self, v):
        self.insert(self._n // 2, v)       # tengah barisan

    def tambah_vip(self, v):
        self.prepend(v)                    # urutan pertama

    def ke_list(self, mulai=0, jumlah=None):
        hasil = []
        cur = self.head
        k = 0
        while cur is not None and k < mulai:
            cur = cur.next
            k += 1
        while cur is not None and (jumlah is None or len(hasil) < jumlah):
            hasil.append(cur.nilai)
            cur = cur.next
        return hasil
    @staticmethod
    def _cek_indeks(i, n):
        if i < 0 or i >= n:
            raise IndexError("indeks " + str(i) + " di luar jangkauan (0.." + str(n - 1) + ")")

    def stats(self):
        return (("panjang", self._n),
                ("total_telusur", self.total_telusur))

def muat_csv(path):
    hasil = []
    with open(path, "r", encoding="utf-8", newline="") as f:
        pembaca = csv.reader(f)
        pertama = True
        for r in pembaca:
            if pertama:                    # lewati header
                pertama = False
                continue
            if len(r) < 9:
                continue
            t_selesai = None
            if r[7] != "":
                t_selesai = int(r[7])
            hasil.append(Pesanan(r[0], r[1], r[2], r[3], int(r[4]),
                                 int(r[5]), int(r[6]), t_selesai, r[8]))
    return hasil

class Hasil:
    __slots__ = ("modul", "nilai", "ms", "langkah", "keterangan")

    def __init__(self, modul, nilai, ms, langkah, keterangan):
        self.modul = modul
        self.nilai = nilai
        self.ms = ms
        self.langkah = langkah
        self.keterangan = keterangan

    def __repr__(self):
        return "[" + self.modul + "] " + format_ms(self.ms) + " | " + self.keterangan

def format_ms(ms):
    teks = str(round(ms, 2))
    return teks.replace(".", ",") + " ms"

class LayananM1:

    def __init__(self):
        self.array = Array()
        self.linked = LinkList()
        self._oid_berikut = 1              # untuk pesanan baru: O-200001, ...

    def muat(self, path):
        self.array = Array()
        self.linked = LinkList()
        data = muat_csv(path)
        t0 = time.perf_counter()
        for p in data:
            self.array.append(p)
        ms_array = (time.perf_counter() - t0) * 1000.0
        t0 = time.perf_counter()
        for p in data:
            self.linked.append(p)
        ms_linked = (time.perf_counter() - t0) * 1000.0
        self._oid_berikut = len(data) + 1
        ket = (str(len(data)) + " pesanan dimuat | array " + format_ms(ms_array)
               + " (kapasitas " + str(self.array.kapasitas()) + ", "
               + str(self.array.jumlah_resize) + "x resize, "
               + str(self.array.total_salinan) + " elemen disalin) | linked list "
               + format_ms(ms_linked))
        return Hasil("M1 - load", len(data), ms_array + ms_linked, 0, ket)

    def _pilih(self, struktur):
        if struktur == STRUKTUR_ARRAY:
            return self.array
        if struktur == STRUKTUR_LINKED:
            return self.linked
        raise ValueError("struktur harus 'array' atau 'linkedlist'")

    def _oid_baru(self):
        n = self._oid_berikut
        self._oid_berikut += 1
        return "O-" + ("0" * (6 - len(str(n)))) + str(n)

    def lihat(self, struktur, i):
        s = self._pilih(struktur)
        t0 = time.perf_counter()
        p = s.get(i)
        ms = (time.perf_counter() - t0) * 1000.0
        if struktur == STRUKTUR_ARRAY:
            ket = "pesanan indeks " + str(i) + " | akses langsung, 0 langkah (O(1))"
            langkah = 0
            modul = "M1 - array"
        else:
            langkah = s.telusur_terakhir
            ket = ("pesanan indeks " + str(i) + " | " + str(langkah)
                   + " simpul ditelusuri (O(n))")
            modul = "M1 - linked list"
        return Hasil(modul, p, ms, langkah, ket)

    def _tambah(self, struktur, jenis, nama_pelanggan, resto, menu, harga, oid):
        s = self._pilih(struktur)
        if oid is None:
            oid = self._oid_baru()
        p = Pesanan(oid, nama_pelanggan, resto, menu, harga,
                    jenis, 28800, None, "ANTRE")
        n_sebelum = len(s)
        t0 = time.perf_counter()
        if jenis == REGULER:
            s.tambah_reguler(p)
            posisi = n_sebelum
        elif jenis == PRIORITAS:
            s.tambah_prioritas(p)
            posisi = n_sebelum // 2
        else:
            s.tambah_vip(p)
            posisi = 0
        ms = (time.perf_counter() - t0) * 1000.0
        if struktur == STRUKTUR_ARRAY:
            langkah = s.geseran_terakhir
            ket = (oid + " (" + NAMA_JENIS[jenis] + ") masuk di indeks " + str(posisi)
                   + " | " + str(langkah) + " elemen digeser")
            if s.salinan_terakhir > 0:
                ket += " | kapasitas dilipatduakan -> " + str(s.kapasitas()) \
                       + ", " + str(s.salinan_terakhir) + " elemen disalin"
            modul = "M1 - array"
        else:
            langkah = s.telusur_terakhir
            ket = (oid + " (" + NAMA_JENIS[jenis] + ") masuk di indeks " + str(posisi)
                   + " | " + str(langkah) + " simpul ditelusuri")
            modul = "M1 - linked list"
        return Hasil(modul, p, ms, langkah, ket)

    def tambah_reguler(self, struktur, pelanggan, resto="kafe-teknik",
                       menu="roti-bakar", harga=12000, oid=None):
        return self._tambah(struktur, REGULER, pelanggan, resto, menu, harga, oid)

    def tambah_prioritas(self, struktur, pelanggan, resto="kafe-teknik",
                         menu="roti-bakar", harga=12000, oid=None):
        return self._tambah(struktur, PRIORITAS, pelanggan, resto, menu, harga, oid)

    def tambah_vip(self, struktur, pelanggan, resto="kafe-teknik",
                   menu="roti-bakar", harga=12000, oid=None):
        return self._tambah(struktur, VIP, pelanggan, resto, menu, harga, oid)

    def tambah_keduanya(self, jenis, pelanggan, resto="kafe-teknik",
                        menu="roti-bakar", harga=12000):
        oid = self._oid_baru()
        a = self._tambah(STRUKTUR_ARRAY, jenis, pelanggan, resto, menu, harga, oid)
        b = self._tambah(STRUKTUR_LINKED, jenis, pelanggan, resto, menu, harga, oid)
        return a, b

    def hapus(self, struktur, i):
        s = self._pilih(struktur)
        t0 = time.perf_counter()
        p = s.remove_at(i)
        ms = (time.perf_counter() - t0) * 1000.0
        if struktur == STRUKTUR_ARRAY:
            langkah = s.geseran_terakhir
            ket = (p.oid + " dihapus dari indeks " + str(i) + " | "
                   + str(langkah) + " elemen digeser")
            modul = "M1 - array"
        else:
            langkah = s.telusur_terakhir
            ket = (p.oid + " dihapus dari indeks " + str(i) + " | "
                   + str(langkah) + " simpul ditelusuri")
            modul = "M1 - linked list"
        return Hasil(modul, p, ms, langkah, ket)

    def daftar(self, struktur, mulai=0, jumlah=20):
        s = self._pilih(struktur)
        return s.ke_list(mulai, jumlah)

    def stats(self):
        return (("array", self.array.stats()),
                ("linkedlist", self.linked.stats()))

def _cari_csv():
    import os
    import sys
    args = []
    for a in sys.argv[1:]:
        if not a.startswith("--"):
            args.append(a)
    if len(args) > 0:
        return args[0]
    lokasi = os.path.dirname(os.path.abspath(__file__))
    kandidat = (
        os.path.join(lokasi, "..", "data", "pesanan.csv"),
        os.path.join(lokasi, "data", "pesanan.csv"),
        os.path.join(lokasi, "pesanan.csv"),
        os.path.join(os.getcwd(), "data", "pesanan.csv"),
        os.path.join(os.getcwd(), "pesanan.csv"),
    )
    for p in kandidat:
        if os.path.exists(p):
            return p
    raise SystemExit("pesanan.csv tidak ditemukan. Taruh di folder data/ "
                     "atau beri path sebagai argumen.")

def _sel(h, satuan):
    return format_ms(h.ms).rjust(10) + " | " + format_rupiah(h.langkah).rjust(9) + " " + satuan

def _baris(label, a, b):
    print(label.ljust(20) + _sel(a, "geseran").ljust(32) + _sel(b, "simpul"))

def main():
    import sys
    detail = "--detail" in sys.argv
    svc = LayananM1()
    muat = svc.muat(_cari_csv())
    lihat_a = svc.lihat(STRUKTUR_ARRAY, 100000)
    lihat_l = svc.lihat(STRUKTUR_LINKED, 100000)
    tambah = []
    for jenis in (REGULER, PRIORITAS, VIP):
        a, b = svc.tambah_keduanya(jenis, "Pelanggan Uji " + NAMA_JENIS[jenis])
        tambah.append((NAMA_JENIS[jenis], a, b))
    hapus_a = svc.hapus(STRUKTUR_ARRAY, 100000)
    hapus_l = svc.hapus(STRUKTUR_LINKED, 100000)
    print("M1 - ARRAY vs LINKED LIST")
    print("Muat : " + muat.keterangan)
    print("")
    print("Operasi".ljust(20) + "Array".ljust(32) + "Linked list")
    print("-" * 74)
    _baris("Lihat ke-100.000", lihat_a, lihat_l)
    for nama, a, b in tambah:
        _baris("Tambah " + nama, a, b)
    _baris("Hapus ke-100.000", hapus_a, hapus_l)
    print("")
    p = lihat_a.nilai
    print("Pesanan indeks 100.000 : " + p.ringkas() + " | Rp " + format_rupiah(p.harga))
    print("Panjang akhir : array " + format_rupiah(len(svc.array))
          + " | linked list " + format_rupiah(len(svc.linked)))
    if detail:
        print("")
        for h in (lihat_a, lihat_l, hapus_a, hapus_l):
            print(h)
        for nama, a, b in tambah:
            print(a)
            print(b)
if __name__ == "__main__":
    main()