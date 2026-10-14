import os
import sys
import time
import importlib.util
_LOKASI = os.path.dirname(os.path.abspath(__file__))

def _impor_m1():
    import importlib.machinery
    folder = (_LOKASI, os.path.join(_LOKASI, "..", "backend"),
              os.path.join(_LOKASI, "..", "back"))
    for d in folder:
        if not os.path.isdir(d):
            continue
        for n in os.listdir(d):
            low = n.lower()
            if not low.startswith("m1"):
                continue
            if os.path.splitext(low)[1] not in ("", ".py"):
                continue
            p = os.path.join(d, n)
            if not os.path.isfile(p):
                continue
            loader = importlib.machinery.SourceFileLoader("m1_pesanan", p)
            spec = importlib.util.spec_from_loader("m1_pesanan", loader)
            modul = importlib.util.module_from_spec(spec)
            loader.exec_module(modul)
            if hasattr(modul, "LayananM1"):
                return modul
    raise SystemExit("M1 tidak ditemukan. Taruh berkas M1 (M1_A+LL.py) "
                     "di folder yang sama dengan berkas ini.")
_M1 = _impor_m1()
Array = _M1.Array
Pesanan = _M1.Pesanan
Hasil = _M1.Hasil
muat_csv = _M1.muat_csv
format_ms = _M1.format_ms
format_rupiah = _M1.format_rupiah

def _angka_str(x):
    if isinstance(x, float):
        if x == int(x):
            x = int(x)
        else:
            return str(round(x, 2)).replace(".", ",")
    if x < 0:
        return "-" + format_rupiah(-x)
    return format_rupiah(x)

def _gabung(daftar):
    if len(daftar) == 0:
        return "kosong"
    hasil = ""
    for i in range(len(daftar)):
        if i > 0:
            hasil += " "
        hasil += str(daftar[i])
    return hasil

class Stack:
    def __init__(self):
        self._a = Array()
    def __len__(self):
        return len(self._a)
    def kosong(self):
        return len(self._a) == 0
    def push(self, x):
        self._a.append(x)
    def pop(self):
        if len(self._a) == 0:
            raise IndexError("stack kosong")
        return self._a.remove_at(len(self._a) - 1)
    def peek(self):
        if len(self._a) == 0:
            raise IndexError("stack kosong")
        return self._a.get(len(self._a) - 1)
    def kosongkan(self):
        while len(self._a) > 0:
            self._a.remove_at(len(self._a) - 1)
    def ke_list(self):
        return self._a.ke_list()

def tokenisasi(ekspresi):
    token = []
    i = 0
    n = len(ekspresi)
    while i < n:
        c = ekspresi[i]
        if c == " " or c == "\t":
            i += 1
            continue
        if ("0" <= c <= "9") or c == ".":
            j = i
            while j < n and (("0" <= ekspresi[j] <= "9") or ekspresi[j] == "."):
                j += 1
            token.append(ekspresi[i:j])
            i = j
            continue
        if c in "+-*/()":
            token.append(c)
            i += 1
            continue
        raise ValueError("karakter tidak dikenal: '" + c + "'")
    return token

def _adalah_angka(t):
    return ("0" <= t[0] <= "9") or t[0] == "."

def _ke_angka(t):
    try:
        if "." in t:
            return float(t)
        return int(t)
    except ValueError:
        raise ValueError("angka tidak valid: '" + t + "'")

def _kuat(op):
    if op == "*" or op == "/":
        return 2
    return 1

def ke_postfix(ekspresi):
    token = tokenisasi(ekspresi)
    if len(token) == 0:
        raise ValueError("ekspresi kosong")
    st = Stack()
    keluar = []
    baris = []
    nomor = 0
    for t in token:
        nomor += 1
        if _adalah_angka(t):
            _ke_angka(t)
            keluar.append(t)
            tindakan = "angka, langsung keluar"
        elif t == "(":
            st.push(t)
            tindakan = "push ("
        elif t == ")":
            ketemu = False
            while not st.kosong():
                atas = st.pop()
                if atas == "(":
                    ketemu = True
                    break
                keluar.append(atas)
            if not ketemu:
                raise ValueError("tanda ) tidak punya pasangan (")
            tindakan = "pop sampai (, buang ("
        else:
            tindakan = ""
            while (not st.kosong()) and st.peek() != "(" and _kuat(st.peek()) >= _kuat(t):
                atas = st.pop()
                keluar.append(atas)
                alasan = "sama kuat" if _kuat(atas) == _kuat(t) else "lebih kuat"
                tindakan += "pop " + atas + " (" + alasan + "), "
            st.push(t)
            tindakan += "push " + t
        baris.append(("1." + str(nomor), t, tindakan,
                      _gabung(st.ke_list()), _gabung_keluar(keluar)))
    while not st.kosong():
        atas = st.pop()
        if atas == "(":
            raise ValueError("tanda ( tidak punya pasangan )")
        keluar.append(atas)
    baris.append(("1.akhir", "-", "pop sisa stack", "kosong", _gabung_keluar(keluar)))
    return keluar, baris

def _gabung_keluar(keluar):
    if len(keluar) == 0:
        return ""
    return _gabung(keluar)

def _bagi(a, b):
    if b == 0:
        raise ValueError("pembagian dengan nol")
    if isinstance(a, int) and isinstance(b, int) and a % b == 0:
        return a // b
    return a / b

def hitung(postfix):
    if isinstance(postfix, str):
        postfix = tokenisasi_postfix(postfix)
    st = Stack()
    baris = []
    nomor = 0
    for t in postfix:
        nomor += 1
        if _adalah_angka(t):
            st.push(_ke_angka(t))
            tindakan = "operand, push " + t
        else:
            if len(st) < 2:
                raise ValueError("operand kurang untuk operator '" + t + "'")
            b = st.pop()
            a = st.pop()
            if t == "+":
                r = a + b
            elif t == "-":
                r = a - b
            elif t == "*":
                r = a * b
            else:
                r = _bagi(a, b)
            st.push(r)
            tindakan = ("pop " + _angka_str(b) + " dan " + _angka_str(a) + " -> "
                        + _angka_str(a) + " " + t + " " + _angka_str(b)
                        + " = " + _angka_str(r))
        isi = st.ke_list()
        teks = ""
        for k in range(len(isi)):
            if k > 0:
                teks += " "
            teks += _angka_str(isi[k])
        baris.append(("2." + str(nomor), t, tindakan, teks, ""))
    if len(st) != 1:
        raise ValueError("ekspresi tidak valid (sisa " + str(len(st)) + " nilai di stack)")
    return st.pop(), baris

def tokenisasi_postfix(teks):
    return tokenisasi(teks)

class AntreanNaif:
    def __init__(self):
        self._a = Array()
        self.total_geseran = 0
    def __len__(self):
        return len(self._a)
    def kapasitas(self):
        return self._a.kapasitas()
    def is_empty(self):
        return len(self._a) == 0
    def enqueue(self, x):
        self._a.append(x)
    def dequeue(self):
        if len(self._a) == 0:
            return None
        x = self._a.remove_at(0)
        self.total_geseran += self._a.geseran_terakhir
        return x
    def push_front(self, x):
        self._a.insert(0, x)
        self.total_geseran += self._a.geseran_terakhir
    def pop_back(self):
        if len(self._a) == 0:
            return None
        return self._a.remove_at(len(self._a) - 1)
    def ke_list(self, mulai=0, jumlah=None):
        return self._a.ke_list(mulai, jumlah)

class AntreanMelingkar:
    def __init__(self, kapasitas=8):
        if kapasitas < 1:
            kapasitas = 1
        self._data = [None] * kapasitas
        self._k = kapasitas
        self.front = 0
        self.rear = 0
        self.count = 0
        self.jumlah_tumbuh = 0
    def __len__(self):
        return self.count
    def kapasitas(self):
        return self._k
    def is_empty(self):
        return self.count == 0
    def is_full(self):
        return self.count == self._k
    def _tumbuh(self):
        baru = [None] * (self._k * 2)
        idx = self.front
        i = 0
        while i < self.count:
            baru[i] = self._data[idx]
            idx = (idx + 1) % self._k
            i += 1
        self._data = baru
        self._k = self._k * 2
        self.front = 0
        self.rear = self.count
        self.jumlah_tumbuh += 1
    def enqueue(self, x):
        if self.count == self._k:
            self._tumbuh()
        self._data[self.rear] = x
        self.rear = (self.rear + 1) % self._k
        self.count += 1
    def dequeue(self):
        if self.count == 0:
            return None
        x = self._data[self.front]
        self._data[self.front] = None
        self.front = (self.front + 1) % self._k
        self.count -= 1
        return x
    def push_front(self, x):
        if self.count == self._k:
            self._tumbuh()
        self.front = (self.front - 1) % self._k
        self._data[self.front] = x
        self.count += 1
    def pop_back(self):
        if self.count == 0:
            return None
        self.rear = (self.rear - 1) % self._k
        x = self._data[self.rear]
        self._data[self.rear] = None
        self.count -= 1
        return x
    def peek(self):
        if self.count == 0:
            return None
        return self._data[self.front]
    def ke_list(self, mulai=0, jumlah=None):
        hasil = []
        i = mulai
        while i < self.count and (jumlah is None or len(hasil) < jumlah):
            hasil.append(self._data[(self.front + i) % self._k])
            i += 1
        return hasil
NAIF = "naif"
MELINGKAR = "circular"

class LayananM2:
    def __init__(self):
        self.naif = AntreanNaif()
        self.melingkar = AntreanMelingkar(8)
        self.undo = Stack()
        self.redo = Stack()
        self._oid_berikut = 1
    def muat(self, path):
        data = muat_csv(path)
        self.naif = AntreanNaif()
        self.melingkar = AntreanMelingkar(8)
        self.undo = Stack()
        self.redo = Stack()
        t0 = time.perf_counter()
        n = 0
        for p in data:
            if p.status == "ANTRE":
                self.naif.enqueue(p)
                self.melingkar.enqueue(p)
                n += 1
        ms = (time.perf_counter() - t0) * 1000.0
        self._oid_berikut = len(data) + 1
        ket = (_angka_str(len(data)) + " baris dibaca | " + _angka_str(n)
               + " pesanan berstatus ANTRE masuk ke KEDUA antrean | kapasitas circular "
               + _angka_str(self.melingkar.kapasitas()))
        return Hasil("M2 - load", n, ms, 0, ket)
    def _oid_baru(self):
        n = self._oid_berikut
        self._oid_berikut += 1
        return "O-" + ("0" * (6 - len(str(n)))) + str(n)
    def _panjang(self):
        return ("naif " + _angka_str(len(self.naif)) + ", circular "
                + _angka_str(len(self.melingkar)))
    def _depth(self):
        return ("tumpukan undo " + str(len(self.undo)) + ", redo " + str(len(self.redo)))
    def stack_postfix(self, ekspresi):
        t0 = time.perf_counter()
        try:
            postfix, baris1 = ke_postfix(ekspresi)
            total, baris2 = hitung(postfix)
        except ValueError as e:
            ms = (time.perf_counter() - t0) * 1000.0
            return Hasil("M2 - stack", None, ms, 0, "ERROR: " + str(e))
        ms = (time.perf_counter() - t0) * 1000.0
        postfix_teks = _gabung(postfix)
        baris = baris1 + baris2
        ket = ("postfix: " + postfix_teks + " | TOTAL : Rp " + _angka_str(total))
        return Hasil("M2 - stack", (postfix_teks, total, baris), ms, len(baris), ket)
    def _catat(self, rec):
        self.undo.push(rec)
        self.redo.kosongkan()
    def aksi_order(self, pesanan):
        self._catat(("ORDER", None, pesanan))
    def queue_enqueue(self, pelanggan, resto="kafe-teknik", menu="roti-bakar",
                      harga=12000, prioritas=3):
        oid = self._oid_baru()
        p = Pesanan(oid, pelanggan, resto, menu, harga, prioritas, 28800, None, "ANTRE")
        t0 = time.perf_counter()
        self.naif.enqueue(p)
        self.melingkar.enqueue(p)
        ms = (time.perf_counter() - t0) * 1000.0
        self._catat(("ENQUEUE", None, p))
        ket = (oid + " masuk paling belakang KEDUA antrean | panjang "
               + self._panjang() + " | " + self._depth())
        return Hasil("M2 - queue", p, ms, 0, ket)
    def _dequeue(self, antrean, nama, k):
        diambil = []
        g0 = 0
        if nama == NAIF:
            g0 = antrean.total_geseran
        t0 = time.perf_counter()
        i = 0
        while i < k:
            x = antrean.dequeue()
            if x is None:
                break
            diambil.append(x)
            i += 1
        ms = (time.perf_counter() - t0) * 1000.0
        geser = 0
        if nama == NAIF:
            geser = antrean.total_geseran - g0
        if len(diambil) > 0:
            self._catat(("DEQUEUE", nama, diambil))
        return diambil, geser, ms
    def queue_dequeue_naive(self, k=1):
        diambil, geser, ms = self._dequeue(self.naif, NAIF, k)
        ket = (_angka_str(len(diambil)) + " pesanan keluar | " + _angka_str(geser)
               + " elemen digeser | sisa antrean naif " + _angka_str(len(self.naif)))
        if len(diambil) < k:
            ket += " | antrean habis"
        return Hasil("M2 - queue naif", diambil, ms, geser, ket)
    def queue_dequeue_circular(self, k=1):
        diambil, geser, ms = self._dequeue(self.melingkar, MELINGKAR, k)
        ket = (_angka_str(len(diambil)) + " pesanan keluar | 0 elemen digeser | front="
               + str(self.melingkar.front) + ", rear=" + str(self.melingkar.rear)
               + ", kapasitas " + _angka_str(self.melingkar.kapasitas())
               + " | sisa antrean circular " + _angka_str(len(self.melingkar)))
        if len(diambil) < k:
            ket += " | antrean habis"
        return Hasil("M2 - queue circular", diambil, ms, 0, ket)
    def _antrean(self, nama):
        if nama == NAIF:
            return self.naif
        return self.melingkar
    def undo_last(self):
        t0 = time.perf_counter()
        if self.undo.kosong():
            return Hasil("M2 - stack", None, 0.0, 0,
                         "tumpukan undo kosong, tidak ada yang dibatalkan")
        jenis, nama, data = self.undo.pop()
        if jenis == "ENQUEUE":
            self.naif.pop_back()
            self.melingkar.pop_back()
            ket = ("Pembatalan enqueue: " + data.oid + " dikeluarkan lagi dari belakang. "
                   "Panjang antrean sekarang: " + self._panjang())
        elif jenis == "DEQUEUE":
            antrean = self._antrean(nama)
            i = len(data) - 1
            while i >= 0:
                antrean.push_front(data[i])
                i -= 1
            ket = (_angka_str(len(data)) + " pesanan dikembalikan ke DEPAN antrean "
                   + nama + ". Panjang antrean sekarang: " + self._panjang())
        else:
            data.status = "CANCEL"
            ket = "Pembatalan order: " + data.oid + " ditandai CANCEL"
        self.redo.push((jenis, nama, data))
        ms = (time.perf_counter() - t0) * 1000.0
        return Hasil("M2 - stack", data, ms, 0, ket + " | " + self._depth())
    def redo_last(self):
        t0 = time.perf_counter()
        if self.redo.kosong():
            return Hasil("M2 - stack", None, 0.0, 0,
                         "tumpukan redo kosong, tidak ada yang diulang")
        jenis, nama, data = self.redo.pop()
        if jenis == "ENQUEUE":
            self.naif.enqueue(data)
            self.melingkar.enqueue(data)
            ket = ("Enqueue dikerjakan lagi: " + data.oid + " masuk kembali ke belakang. "
                   "Panjang antrean sekarang: " + self._panjang())
        elif jenis == "DEQUEUE":
            antrean = self._antrean(nama)
            i = 0
            while i < len(data):
                antrean.dequeue()
                i += 1
            ket = (_angka_str(len(data)) + " pesanan keluar lagi dari antrean " + nama
                   + ". Panjang antrean sekarang: " + self._panjang())
        else:
            data.status = "ANTRE"
            ket = "Order dikerjakan lagi: " + data.oid + " kembali ANTRE"
        self.undo.push((jenis, nama, data))
        ms = (time.perf_counter() - t0) * 1000.0
        return Hasil("M2 - stack", data, ms, 0, ket + " | " + self._depth())
    def history(self):
        isi = self.undo.ke_list()
        hasil = []
        for i in range(len(isi)):
            jenis, nama, data = isi[i]
            if jenis == "DEQUEUE":
                teks = "DEQUEUE x" + str(len(data)) + " (" + nama + ")"
            else:
                teks = jenis + " " + data.oid
            hasil.append(str(i + 1) + ". " + teks)
        return hasil
    def isi_antrean(self, nama, jumlah=5):
        return self._antrean(nama).ke_list(0, jumlah)
    def stats(self):
        return (("queue_len_naif", len(self.naif)),
                ("queue_len_circular", len(self.melingkar)),
                ("queue_capacity_naif", self.naif.kapasitas()),
                ("queue_capacity_circular", self.melingkar.kapasitas()),
                ("total_geseran_naif", self.naif.total_geseran),
                ("undo_depth", len(self.undo)),
                ("redo_depth", len(self.redo)))
_DETAIL = "--detail" in sys.argv
_LULUS = [0]

def _cek(kondisi, pesan):
    if not kondisi:
        raise AssertionError("GAGAL: " + pesan)
    _LULUS[0] += 1
    if _DETAIL:
        print("  OK  " + pesan)

def uji_mandiri():
    if _DETAIL:
        print("")
        print("=" * 78)
        print("0. UJI MANDIRI (kebenaran logika)")
        print("=" * 78)
    s = Stack()
    s.push(1)
    s.push(2)
    s.push(3)
    _cek(s.peek() == 3 and s.pop() == 3 and s.pop() == 2 and len(s) == 1, "stack LIFO")
    _cek(_gabung(ke_postfix("3 + 4 * 2")[0]) == "3 4 2 * +", "postfix tanpa kurung")
    _cek(_gabung(ke_postfix("(3 + 4) * 2")[0]) == "3 4 + 2 *", "postfix berkurung")
    _cek(_gabung(ke_postfix("10 - 3 - 2")[0]) == "10 3 - 2 -", "postfix '-' beruntun")
    _cek(_gabung(ke_postfix("((2 + 3) * (4 - 1))")[0]) == "2 3 + 4 1 - *", "postfix kurung bersarang")
    _cek(_gabung(ke_postfix("( 3 * 12000 ) + ( 2 * 8500 ) - 5000")[0])
         == "3 12000 * 2 8500 * + 5000 -", "contoh modul: postfix struk kasir")
    _cek(hitung("20 5 -")[0] == 15, "20 - 5 = 15 (bukan -15)")
    _cek(hitung("100 5 / 2 /")[0] == 10, "100 / 5 / 2 = 10")
    _cek(hitung(ke_postfix("10 - 3 - 2")[0])[0] == 5, "10 - 3 - 2 = 5")
    _cek(hitung(ke_postfix("( 3 * 12000 ) + ( 2 * 8500 ) - 5000")[0])[0] == 48000,
         "total struk kasir = Rp 48.000")
    _cek(hitung(ke_postfix("12000 / 4 - 500")[0])[0] == 2500, "angka berdigit banyak satu token")
    svc0 = LayananM2()
    _cek(svc0.stack_postfix("3 + (4").keterangan.startswith("ERROR"), "kurung tak berpasangan -> ERROR")
    _cek(svc0.stack_postfix("5 / 0").keterangan.startswith("ERROR"), "bagi nol -> ERROR")
    _cek(svc0.stack_postfix("3 +").keterangan.startswith("ERROR"), "operand kurang -> ERROR")
    q = AntreanMelingkar(4)
    q.enqueue("a"); q.enqueue("b"); q.enqueue("c")
    _cek(q.dequeue() == "a" and q.dequeue() == "b", "circular: keluar 2 (FIFO)")
    q.enqueue("d"); q.enqueue("e"); q.enqueue("f")
    _cek(q.rear == 2 and q.front == 2 and q.count == 4, "circular: penunjuk berputar, penuh (front==rear tapi count=4)")
    _cek(q.ke_list() == ["c", "d", "e", "f"], "circular: isi tetap benar setelah berputar")
    q.enqueue("g")
    _cek(q.kapasitas() == 8 and q.ke_list() == ["c", "d", "e", "f", "g"], "circular: penuh -> tumbuh 2x, urutan terjaga")
    _cek(AntreanMelingkar(4).dequeue() is None and AntreanMelingkar(4).is_empty(), "circular: dequeue saat kosong -> None")
    svc = LayananM2()
    for i in range(300):
        svc.queue_enqueue("P" + str(i))
    a = svc.queue_dequeue_naive(50)
    b = svc.queue_dequeue_circular(50)
    sama = True
    for i in range(50):
        if a.nilai[i].oid != b.nilai[i].oid:
            sama = False
    _cek(sama, "naif & circular mengeluarkan pesanan yang SAMA persis")
    _cek(a.langkah > 0 and b.langkah == 0, "geseran: naif > 0, circular = 0")
    svc = LayananM2()
    svc.queue_enqueue("A")
    svc.queue_enqueue("B")
    svc.queue_dequeue_circular(1)
    _cek(len(svc.history()) == 3, "history() mencatat 3 aksi")
    svc.undo_last()
    _cek(len(svc.melingkar) == 2 and len(svc.history()) == 2 and svc.melingkar.peek().pelanggan == "A",
         "undo DEQUEUE: kembali ke DEPAN, history ikut berkurang")
    svc.redo_last()
    _cek(len(svc.melingkar) == 1 and len(svc.history()) == 3, "redo: aksi asli dikerjakan lagi")
    svc.undo_last()
    svc.queue_enqueue("C")
    _cek(len(svc.redo) == 0 and svc.redo_last().nilai is None, "aksi baru mengosongkan redo")
    if _DETAIL:
        print("  Semua uji mandiri lulus")
    return _LULUS[0]

def _garis(judul):
    print("")
    print("=" * 78)
    print(judul)
    print("=" * 78)

def _cetak_tabel(baris):
    print("  " + "langkah".ljust(8) + "token".ljust(8) + "tindakan".ljust(52)
          + "stack".ljust(22) + "keluaran")
    print("  " + "-" * 7 + " " + "-" * 7 + " " + "-" * 51 + " " + "-" * 21 + " " + "-" * 20)
    for (lg, tk, tind, stk, out) in baris:
        print("  " + lg.ljust(8) + tk.ljust(8) + tind.ljust(52) + stk.ljust(22) + out)

def _cari_csv():
    args = []
    for a in sys.argv[1:]:
        if not a.startswith("--"):
            args.append(a)
    if len(args) > 0:
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

def _pendek(ket):
    k = ket
    i = k.find(". Panjang")
    if i >= 0:
        k = k[:i]
    j = k.find(" | ")
    if j >= 0:
        k = k[:j]
    return k

def _sel(h):
    return (format_ms(h.ms).rjust(10) + " | " + _angka_str(h.langkah).rjust(10) + " geseran")

def main():
    n_cek = uji_mandiri()
    svc = LayananM2()
    muat = svc.muat(_cari_csv())
    struk = "( 3 * 12000 ) + ( 2 * 8500 ) - 5000"
    kasir = svc.stack_postfix(struk)
    postfix_teks, total, baris_langkah = kasir.nilai
    uji_op = []
    for e in ("20 - 5", "100 / 5 / 2", "10 - 3 - 2"):
        uji_op.append(e + " = " + _angka_str(svc.stack_postfix(e).nilai[1]))
    enq = svc.queue_enqueue("Pelanggan Baru")
    panjang_enq = len(svc.naif)
    n1 = svc.queue_dequeue_naive(1)
    c1 = svc.queue_dequeue_circular(1)
    n100 = svc.queue_dequeue_naive(100)
    c100 = svc.queue_dequeue_circular(100)
    identik = len(n100.nilai) == len(c100.nilai)
    for i in range(len(n100.nilai)):
        if identik and n100.nilai[i] is not c100.nilai[i]:
            identik = False
    riwayat = svc.history()
    u = svc.undo_last()
    len_undo = len(svc.melingkar)
    r = svc.redo_last()
    len_redo = len(svc.melingkar)
    svc.queue_enqueue("Pencabang")
    r2 = svc.redo_last()
    print("M2 - STACK & QUEUE")
    print("Uji mandiri : " + str(n_cek) + " pengecekan lulus")
    print("Data        : " + _angka_str(muat.nilai) + " pesanan ANTRE di KEDUA antrean "
          "(kapasitas circular " + _angka_str(svc.melingkar.kapasitas()) + ")")
    print("")
    print("KASIR   " + struk)
    print("  postfix : " + postfix_teks)
    print("  TOTAL   : Rp " + _angka_str(total))
    print("  uji - dan / : " + " | ".join(uji_op))
    print("")
    print("DEQUEUE (data sama persis)".ljust(30) + "Naif".center(26) + " " + "Circular".center(26))
    print("-" * 74)
    print("  1 pesanan".ljust(30) + _sel(n1).ljust(30) + _sel(c1))
    print("  100 pesanan".ljust(30) + _sel(n100).ljust(30) + _sel(c100))
    print("  100 pesanan yang keluar identik : " + ("YA" if identik else "TIDAK"))
    print("")
    print("UNDO / REDO")
    print("  riwayat : " + " | ".join(riwayat))
    print("  undo    : " + _pendek(u.keterangan) + " (circular jadi " + _angka_str(len_undo) + ")")
    print("  redo    : " + _pendek(r.keterangan) + " (circular jadi " + _angka_str(len_redo) + ")")
    print("  aksi baru lalu redo : " + r2.keterangan)
    print("")
    print("Akhir : naif " + _angka_str(len(svc.naif)) + " | circular "
          + _angka_str(len(svc.melingkar)) + " | undo " + str(len(svc.undo))
          + " | redo " + str(len(svc.redo)))
    if _DETAIL:
        _garis("DETAIL: tabel langkah kasir")
        _cetak_tabel(baris_langkah)
        _garis("DETAIL: keterangan lengkap")
        for h in (enq, n1, c1, n100, c100, u, r):
            print(h)
if __name__ == "__main__":
    main()
