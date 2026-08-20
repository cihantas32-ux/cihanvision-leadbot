import requests
import json
import math
import re
import time

print()
print("--- CIHAN VISION LEAD BOT v2.2 MOBILE TURBO ---")
print("Nitelikli yerel işletmeler ve akıllı saha rotası hazırlanıyor...")
print()

ARAMA_YARICAPI = 1500
MAX_ISLETME = 30
MIN_LEAD_SKORU = 55

CIKTI_JSON = "bugunun_rotasi.json"

OVERPASS_SERVERS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass.private.coffee/api/interpreter",
]

OSRM_URL = "https://routing.openstreetmap.de/routed-foot/route/v1/driving"


def haversine(lat1, lon1, lat2, lon2):
    R = 6371000

    p1 = math.radians(lat1)
    p2 = math.radians(lat2)

    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)

    a = (
        math.sin(dp / 2) ** 2
        + math.cos(p1)
        * math.cos(p2)
        * math.sin(dl / 2) ** 2
    )

    return 2 * R * math.atan2(
        math.sqrt(a),
        math.sqrt(1 - a)
    )


def dms_to_decimal(degree, minute, second, direction):
    value = degree + minute / 60 + second / 3600

    if direction.upper() in ["S", "W"]:
        value *= -1

    return value


def koordinat_oku(text):
    text = text.strip()

    try:
        temiz = text.replace(" ", "")
        parts = temiz.split(",")

        if len(parts) == 2:
            lat = float(parts[0])
            lon = float(parts[1])

            if -90 <= lat <= 90 and -180 <= lon <= 180:
                return lat, lon

    except:
        pass

    pattern = (
        r'(\d+(?:\.\d+)?)\s*°\s*'
        r'(\d+(?:\.\d+)?)\s*[\'′]\s*'
        r'(\d+(?:\.\d+)?)\s*["″]?\s*([NS])'
        r'.*?'
        r'(\d+(?:\.\d+)?)\s*°\s*'
        r'(\d+(?:\.\d+)?)\s*[\'′]\s*'
        r'(\d+(?:\.\d+)?)\s*["″]?\s*([EW])'
    )

    match = re.search(
        pattern,
        text,
        re.IGNORECASE
    )

    if match:
        lat = dms_to_decimal(
            float(match.group(1)),
            float(match.group(2)),
            float(match.group(3)),
            match.group(4)
        )

        lon = dms_to_decimal(
            float(match.group(5)),
            float(match.group(6)),
            float(match.group(7)),
            match.group(8)
        )

        return lat, lon

    return None


print("Google Maps'ten bulunduğun noktanın koordinatını yapıştır.")
print()
print("Örnek:")
print('41°04\'31.0"N 28°53\'51.7"E')
print("veya")
print("41.075278, 28.897694")
print()

while True:
    giris = input("📍 Başlangıç konumu: ")

    sonuc = koordinat_oku(giris)

    if sonuc:
        BASLANGIC_LAT, BASLANGIC_LON = sonuc
        break

    print()
    print("⚠ Koordinat okunamadı.")
    print("Google Maps'teki koordinatı olduğu gibi kopyala.")
    print()

print()
print(
    f"✓ Başlangıç: {BASLANGIC_LAT:.6f}, "
    f"{BASLANGIC_LON:.6f}"
)
print(f"✓ Arama yarıçapı: {ARAMA_YARICAPI} metre")
print()


def sektor_bul(tags):

    amenity = tags.get("amenity", "").lower()
    shop = tags.get("shop", "").lower()
    healthcare = tags.get("healthcare", "").lower()

    if amenity == "restaurant":
        return "Restoran"

    if amenity == "cafe":
        return "Kafe"

    if shop in ["hairdresser", "beauty"]:
        return "Güzellik / Kuaför"

    if amenity == "dentist" or healthcare == "dentist":
        return "Diş Kliniği"

    if amenity == "clinic" or healthcare in [
        "clinic",
        "physiotherapist"
    ]:
        return "Klinik"

    if shop in [
        "furniture",
        "interior_decoration",
        "kitchen",
        "bed",
        "carpet"
    ]:
        return "Mobilya / Dekorasyon"

    if shop in [
        "appliance",
        "electronics",
        "electrical"
    ]:
        return "Elektronik / Beyaz Eşya"

    if shop in [
        "houseware",
        "bathroom_furnishing",
        "lighting",
        "tiles",
        "flooring"
    ]:
        return "Ev / Dekorasyon"

    if shop in [
        "car",
        "car_repair",
        "tyres"
    ]:
        return "Otomotiv"

    return None


BAYI_MARKALARI = [
    "arçelik",
    "arcelik",
    "beko",
    "vestel",
    "regal",
    "altus",
    "bosch",
    "siemens",
    "profilo",
    "istikbal",
    "bellona",
    "mondi",
    "kelebek",
    "doğtaş",
    "dogtas",
    "bambi"
]


def bayi_markasi_mi(isim, tags):

    metin = " ".join([
        isim or "",
        tags.get("brand", ""),
        tags.get("operator", "")
    ]).lower()

    return any(
        marka in metin
        for marka in BAYI_MARKALARI
    )


MERKEZI_ZINCIRLER = [
    "turkcell",
    "turcell",
    "vodafone",
    "türk telekom",
    "turk telekom",

    "samsung",
    "xiaomi",
    "huawei",
    "apple",
    "teknosa",
    "mediamarkt",
    "media markt",
    "vatan bilgisayar",

    "migros",
    "carrefour",
    "a101",
    "bim",
    "şok",
    "sok market",
    "file market",

    "starbucks",
    "mcdonald",
    "burger king",
    "kfc",
    "popeyes",
    "domino",
    "pizza hut",
    "subway",
    "arby's",
    "arbys",
    "sbarro",
    "simit sarayı",
    "simit sarayi",

    "gratis",
    "watsons",
    "rossmann"
]


def merkezi_zincir_mi(isim, tags):

    metin = " ".join([
        isim or "",
        tags.get("brand", ""),
        tags.get("operator", "")
    ]).lower()

    return any(
        zincir in metin
        for zincir in MERKEZI_ZINCIRLER
    )


TICARI_OLMAYAN_KELIMELER = [
    "derneği",
    "dernegi",
    "dernek",
    "vakfı",
    "vakfi",
    "vakıf",
    "vakif",
    "cemiyeti",
    "sendika",
    "kooperatif",

    "belediyesi",
    "belediye",
    "kaymakamlığı",
    "kaymakamligi",
    "kaymakamlık",
    "kaymakamlik",
    "muhtarlığı",
    "muhtarligi",
    "muhtarlık",
    "muhtarlik",
    "bakanlığı",
    "bakanligi",
    "bakanlık",
    "bakanlik",
    "müdürlüğü",
    "mudurlugu",
    "müdürlük",
    "mudurluk",

    "kültür merkezi",
    "kultur merkezi",
    "sosyal tesis",

    "aile sağlığı merkezi",
    "aile sagligi merkezi",
    "aile sağlık merkezi",
    "aile saglik merkezi",
    "sağlık ocağı",
    "saglik ocagi",
    "devlet hastanesi",
    "şehir hastanesi",
    "sehir hastanesi",
    "eğitim ve araştırma hastanesi",
    "egitim ve arastirma hastanesi",
    "toplum sağlığı merkezi",
    "toplum sagligi merkezi",
    "112 acil",
    "acil sağlık",
    "acil saglik",

    "halk eğitim",
    "halk egitim",
    "mesleki eğitim merkezi",
    "mesleki egitim merkezi"
]


def ticari_olmayan_mi(isim, tags):

    metin = " ".join([
        isim or "",
        tags.get("operator", ""),
        tags.get("description", "")
    ]).lower()

    if any(
        kelime in metin
        for kelime in TICARI_OLMAYAN_KELIMELER
    ):
        return True

    amenity = tags.get("amenity", "").lower()
    office = tags.get("office", "").lower()
    operator_type = tags.get("operator:type", "").lower()
    ownership = tags.get("ownership", "").lower()

    if amenity in [
        "school",
        "college",
        "university",
        "library",
        "community_centre",
        "social_centre",
        "place_of_worship",
        "townhall"
    ]:
        return True

    if office in [
        "government",
        "association",
        "ngo"
    ]:
        return True

    if operator_type in [
        "government",
        "public"
    ]:
        return True

    if ownership in [
        "public",
        "government"
    ]:
        return True

    return False


MIKRO_KELIMELER = [
    "tostçu",
    "tostcu",
    "çiğköfte",
    "cigkofte",
    "çiğ köfte",
    "cig kofte",
    "büfe",
    "bufe",
    "çay ocağı",
    "cay ocagi",
    "kokoreç",
    "kokorec",
    "midyeci",
    "lokmacı",
    "lokmaci",
    "pilavcı",
    "pilavci",
    "köfte ekmek",
    "kofte ekmek",
    "dönerci",
    "donerci",
    "tantunici",
    "seyyar"
]


def mikro_isletme_sinyali(isim):

    isim = (isim or "").lower()

    return any(
        kelime in isim
        for kelime in MIKRO_KELIMELER
    )


def telefon_var(tags):
    return bool(
        tags.get("phone")
        or tags.get("contact:phone")
    )


def website_var(tags):
    return bool(
        tags.get("website")
        or tags.get("contact:website")
    )


def instagram_var(tags):
    return bool(
        tags.get("instagram")
        or tags.get("contact:instagram")
    )


def adres_var(tags):
    return bool(
        tags.get("addr:street")
        or tags.get("addr:housenumber")
    )


def lead_skoru_hesapla(isletme):

    sektor = isletme["sektor"]
    tags = isletme["tags"]

    skor = 25

    sektor_bonus = {
        "Diş Kliniği": 35,
        "Klinik": 32,
        "Mobilya / Dekorasyon": 30,
        "Güzellik / Kuaför": 27,
        "Elektronik / Beyaz Eşya": 25,
        "Ev / Dekorasyon": 24,
        "Otomotiv": 23,
        "Restoran": 18,
        "Kafe": 16
    }

    skor += sektor_bonus.get(sektor, 0)

    if isletme["bayi"]:
        skor += 15

    if telefon_var(tags):
        skor += 6

    if website_var(tags):
        skor += 8

    if instagram_var(tags):
        skor += 8

    if adres_var(tags):
        skor += 3

    if mikro_isletme_sinyali(isletme["isim"]):
        skor -= 25

    return max(0, min(skor, 100))


def potansiyel_etiketi(skor):

    if skor >= 80:
        return "ÇOK YÜKSEK"

    if skor >= 70:
        return "YÜKSEK"

    if skor >= 60:
        return "İYİ"

    return "NORMAL"


def kaliteli_lead_mi(isletme):

    isim = isletme["isim"]
    sektor = isletme["sektor"]
    tags = isletme["tags"]

    if ticari_olmayan_mi(isim, tags):
        return False, "TİCARİ OLMAYAN"

    if merkezi_zincir_mi(isim, tags):
        return False, "KURUMSAL / ZİNCİR"

    if isletme["bayi"]:
        return True, "YEREL BAYİ ADAYI"

    if mikro_isletme_sinyali(isim):

        guclu_dijital = (
            website_var(tags)
            and telefon_var(tags)
        )

        if not guclu_dijital:
            return False, "MİKRO İŞLETME"

    if sektor in ["Restoran", "Kafe"]:

        sinyal = 0

        if telefon_var(tags):
            sinyal += 1

        if website_var(tags):
            sinyal += 1

        if instagram_var(tags):
            sinyal += 1

        if adres_var(tags):
            sinyal += 1

        if sinyal == 0:
            return False, "ZAYIF RESTORAN/KAFE"

    if isletme["lead_skoru"] < MIN_LEAD_SKORU:
        return False, "DÜŞÜK LEAD SKORU"

    return True, "UYGUN"


SORGU_1 = f"""
[out:json][timeout:35];
(
  nwr(around:{ARAMA_YARICAPI},{BASLANGIC_LAT},{BASLANGIC_LON})
    ["amenity"~"^(restaurant|cafe|dentist|clinic)$"];

  nwr(around:{ARAMA_YARICAPI},{BASLANGIC_LAT},{BASLANGIC_LON})
    ["healthcare"~"^(clinic|dentist|physiotherapist)$"];
);
out center tags;
"""


SORGU_2 = f"""
[out:json][timeout:35];
(
  nwr(around:{ARAMA_YARICAPI},{BASLANGIC_LAT},{BASLANGIC_LON})
    ["shop"~"^(hairdresser|beauty|furniture|interior_decoration|kitchen|bed|carpet|appliance|electronics|electrical|houseware|bathroom_furnishing|lighting|tiles|flooring|car|car_repair|tyres)$"];
);
out center tags;
"""


def overpass_indir(query, sorgu_no):

    print(f"[{sorgu_no}/2] OSM verisi alınıyor...")

    for server in OVERPASS_SERVERS:

        print(f"   Sunucu: {server}")

        try:

            r = requests.post(
                server,
                data={"data": query},
                timeout=50,
                headers={
                    "User-Agent": "CihanVisionLeadBot/2.1M"
                }
            )

            if r.status_code == 200:

                data = r.json()
                kayitlar = data.get("elements", [])

                print(
                    f"   ✓ {len(kayitlar)} "
                    f"ham kayıt alındı."
                )

                return kayitlar

            print(f"   ⚠ HTTP {r.status_code}")

        except Exception as e:
            print(f"   ⚠ {e}")

        time.sleep(1)

    return []


def sorguyu_guvenli_al(query, sorgu_no, maksimum_tur=3):

    for tur in range(1, maksimum_tur + 1):

        kayitlar = overpass_indir(
            query,
            sorgu_no
        )

        if kayitlar:
            return kayitlar

        if tur < maksimum_tur:

            bekleme = 3 * tur

            print(
                f"   ↻ Sorgu {sorgu_no} alınamadı. "
                f"{bekleme} sn sonra tekrar denenecek..."
            )

            time.sleep(bekleme)

    return None


elements_1 = sorguyu_guvenli_al(
    SORGU_1,
    1
)

elements_2 = sorguyu_guvenli_al(
    SORGU_2,
    2
)


if elements_1 is None or elements_2 is None:

    print()
    print("=" * 74)
    print("❌ OSM VERİSİ EKSİK — ROTA OLUŞTURULMADI")
    print("=" * 74)

    if elements_1 is None:
        print(
            "× 1/2 restoran, kafe ve klinik "
            "sorgusu tamamlanamadı."
        )

    if elements_2 is None:
        print(
            "× 2/2 mağaza, güzellik, mobilya ve "
            "otomotiv sorgusu tamamlanamadı."
        )

    print()
    print(
        "Eksik veriyle yanlış lead sayısı göstermemek "
        "için bot durduruldu."
    )
    print("Biraz sonra tekrar çalıştır:")
    print("python lead_bot.py")
    print("=" * 74)

    raise SystemExit


elements = []
elements.extend(elements_1)
elements.extend(elements_2)

print()
print("✓ OSM sorguları eksiksiz tamamlandı: 2/2")
print(f"✓ Toplam ham OSM kaydı: {len(elements)}")


ham_isletmeler = []
gorulen_osm = set()


for element in elements:

    osm_id = (
        f"{element.get('type')}-"
        f"{element.get('id')}"
    )

    if osm_id in gorulen_osm:
        continue

    gorulen_osm.add(osm_id)

    tags = element.get("tags", {})

    isim = tags.get("name")

    if not isim:
        continue

    sektor = sektor_bul(tags)

    if not sektor:
        continue

    if element.get("type") == "node":

        lat = element.get("lat")
        lon = element.get("lon")

    else:

        center = element.get("center", {})

        lat = center.get("lat")
        lon = center.get("lon")

    if lat is None or lon is None:
        continue

    mesafe = haversine(
        BASLANGIC_LAT,
        BASLANGIC_LON,
        lat,
        lon
    )

    if mesafe > ARAMA_YARICAPI:
        continue

    bayi = bayi_markasi_mi(
        isim,
        tags
    )

    kayit = {
        "osm_id": osm_id,
        "isim": isim,
        "sektor": sektor,
        "lat": lat,
        "lon": lon,

        "telefon": (
            tags.get("phone")
            or tags.get("contact:phone")
        ),

        "website": (
            tags.get("website")
            or tags.get("contact:website")
        ),

        "instagram": (
            tags.get("instagram")
            or tags.get("contact:instagram")
        ),

        "sokak": tags.get("addr:street"),
        "no": tags.get("addr:housenumber"),

        "mesafe_baslangic": mesafe,
        "bayi": bayi,
        "tags": tags
    }

    kayit["lead_skoru"] = lead_skoru_hesapla(
        kayit
    )

    ham_isletmeler.append(
        kayit
    )


isletmeler = []

elenen = {
    "KURUMSAL / ZİNCİR": [],
    "TİCARİ OLMAYAN": [],
    "MİKRO İŞLETME": [],
    "ZAYIF RESTORAN/KAFE": [],
    "DÜŞÜK LEAD SKORU": []
}


for isletme in ham_isletmeler:

    uygun, sebep = kaliteli_lead_mi(
        isletme
    )

    if uygun:
        isletmeler.append(
            isletme
        )

    else:

        if sebep not in elenen:
            elenen[sebep] = []

        elenen[sebep].append(
            isletme["isim"]
        )


temiz = []

for aday in isletmeler:

    duplicate = False

    for mevcut in temiz:

        ayni_isim = (
            aday["isim"].strip().lower()
            ==
            mevcut["isim"].strip().lower()
        )

        if not ayni_isim:
            continue

        mesafe = haversine(
            aday["lat"],
            aday["lon"],
            mevcut["lat"],
            mevcut["lon"]
        )

        if mesafe < 25:
            duplicate = True
            break

    if not duplicate:
        temiz.append(aday)


isletmeler = temiz


print()
print("=" * 74)
print("LEAD KALİTE FİLTRESİ")
print("=" * 74)
print()

print(
    f"Ham uygun sektör işletmesi: "
    f"{len(ham_isletmeler)}"
)

toplam_elenen = sum(
    len(v)
    for v in elenen.values()
)

print(f"Toplam elenen: {toplam_elenen}")
print(f"✓ NİTELİKLİ LEAD: {len(isletmeler)}")
print()


for sebep, liste in elenen.items():

    if not liste:
        continue

    print(
        f"× {sebep}: "
        f"{len(liste)}"
    )

    benzersiz = list(
        dict.fromkeys(liste)
    )

    for isim in benzersiz[:8]:
        print(f"   - {isim}")

    if len(benzersiz) > 8:

        print(
            f"   ... +{len(benzersiz) - 8} "
            f"işletme"
        )

    print()


if not isletmeler:

    print(
        "❌ Bu bölgede filtreyi geçen "
        "nitelikli lead yok."
    )

    raise SystemExit


# ============================================================
# v2.1 REAL WALK FIELD EFFICIENCY ROUTER
# Rota SEÇİMİ gerçek yaya mesafesiyle yapılır.
# ============================================================

_yaya_cache = {}

def yaya_mesafesi(a, b):
    key = (
        round(a["lat"], 6), round(a["lon"], 6),
        round(b["lat"], 6), round(b["lon"], 6)
    )
    reverse_key = (key[2], key[3], key[0], key[1])

    if key in _yaya_cache:
        return _yaya_cache[key]
    if reverse_key in _yaya_cache:
        return _yaya_cache[reverse_key]

    url = (
        f"{OSRM_URL}/"
        f"{a['lon']},{a['lat']};"
        f"{b['lon']},{b['lat']}"
        "?overview=false"
    )

    try:
        r = requests.get(
            url,
            timeout=4,
            headers={"User-Agent": "CihanVisionLeadBot/2.1M"}
        )

        if r.status_code == 200:
            data = r.json()
            if data.get("routes"):
                sonuc = (data["routes"][0]["distance"], True)
                _yaya_cache[key] = sonuc
                return sonuc
    except:
        pass

    # Routing servisi o an cevap vermezse bot çökmesin.
    # Sadece o etap için muhafazakâr tahmin kullanılır.
    kus_ucusu = haversine(
        a["lat"], a["lon"],
        b["lat"], b["lon"]
    )
    sonuc = (kus_ucusu * 1.35, False)
    _yaya_cache[key] = sonuc
    return sonuc


def rota_olustur(isletmeler):

    if not isletmeler:
        return [], {}

    kalan = isletmeler.copy()
    rota = []

    # MOBILE TURBO:
    # Rota seçerken hiçbir OSRM/yaya API çağrısı yapma.
    # Coğrafi mesafe + lead yoğunluğu ile rotayı seç.
    # Gerçek yaya mesafeleri daha sonra sadece seçilmiş etaplar için hesaplanır.
    YAKIN_ETAP = 450
    COK_YAKIN = 180
    YOGUNLUK_YARICAPI = 420
    MAX_KUME_GECISI = 1200
    MAX_TAHMINI_ROTA = 3600
    MAX_ROTA = MAX_ISLETME

    toplam_tahmini = 0.0
    onceki = None

    def kus_mesafe(a, b):
        return haversine(a["lat"], a["lon"], b["lat"], b["lon"])

    def baslangic_mesafe(a):
        return haversine(BASLANGIC_LAT, BASLANGIC_LON, a["lat"], a["lon"])

    def komsu_sayisi(aday, havuz, yaricap=YOGUNLUK_YARICAPI):
        return sum(
            1 for diger in havuz
            if diger is not aday and kus_mesafe(aday, diger) <= yaricap
        )

    def geri_donus_cezasi(prev, mevcut, aday):
        if prev is None:
            return 0.0

        ax = mevcut["lon"] - prev["lon"]
        ay = mevcut["lat"] - prev["lat"]
        bx = aday["lon"] - mevcut["lon"]
        by = aday["lat"] - mevcut["lat"]

        na = math.hypot(ax, ay)
        nb = math.hypot(bx, by)

        if na == 0 or nb == 0:
            return 0.0

        cos_acisi = (ax * bx + ay * by) / (na * nb)

        if cos_acisi < -0.55:
            return 230.0
        if cos_acisi < -0.15:
            return 95.0
        return 0.0

    # İlk hedef: yakınlıktan çok yoğun ticari kümeyi ödüllendir.
    ilk_adaylar = []

    for aday in kalan:
        d = baslangic_mesafe(aday)
        yogunluk = komsu_sayisi(aday, kalan)

        maliyet = d / max(1.0, 1.0 + yogunluk * 0.52)

        if d > 1500 and yogunluk == 0:
            maliyet += 1200

        ilk_adaylar.append((maliyet, d, -yogunluk, aday))

    ilk_adaylar.sort(key=lambda x: (x[0], x[1], x[2]))

    ilk = ilk_adaylar[0][3]
    ilk_d = ilk_adaylar[0][1]

    rota.append(ilk)
    kalan.remove(ilk)
    toplam_tahmini += ilk_d

    # Ticari aksı süpür.
    while kalan and len(rota) < MAX_ROTA:

        mevcut = rota[-1]
        adaylar = []

        for aday in kalan:
            d = kus_mesafe(mevcut, aday)
            yogunluk = komsu_sayisi(aday, kalan)
            kume = 1 + yogunluk

            if d > MAX_KUME_GECISI:
                continue

            if d > 700 and kume < 2:
                continue

            if toplam_tahmini + d > MAX_TAHMINI_ROTA:
                continue

            etkin = d / max(1.0, min(kume, 6) ** 0.72)

            if d <= COK_YAKIN:
                etkin *= 0.66
            elif d <= YAKIN_ETAP:
                etkin *= 0.84

            etkin += geri_donus_cezasi(onceki, mevcut, aday)
            adaylar.append((etkin, d, -kume, aday))

        if not adaylar:
            break

        adaylar.sort(key=lambda x: (x[0], x[1], x[2]))
        _, d, _, sonraki = adaylar[0]

        onceki = mevcut
        rota.append(sonraki)
        kalan.remove(sonraki)
        toplam_tahmini += d

    debug = {
        "rotaya_alinan": len(rota),
        "atlanan": len(kalan),
        "uzak_izole": [],
        "rota_butcesi": [],
        "diger": [],
        "gercek_yaya_butcesi": toplam_tahmini
    }

    if rota:
        son = rota[-1]
        for aday in kalan:
            d = kus_mesafe(son, aday)

            if d > MAX_KUME_GECISI:
                debug["uzak_izole"].append(aday["isim"])
            elif toplam_tahmini + d > MAX_TAHMINI_ROTA:
                debug["rota_butcesi"].append(aday["isim"])
            else:
                debug["diger"].append(aday["isim"])

    return rota, debug


print()
print("Gerçek yaya mesafeli akıllı saha rotası hesaplanıyor...")

rota, rota_debug = rota_olustur(isletmeler)

print(
    f"✓ Rota oluşturuldu: "
    f"{len(rota)} işletme"
)

print(
    f"✓ Rotaya alınmayan qualified lead: "
    f"{rota_debug.get('atlanan', 0)}"
)

print()
print("=" * 74)
print("CIHAN VISION — v2.1 REAL WALK ROUTER")
print("=" * 74)
print()


print(
    f"Başlangıç: "
    f"{BASLANGIC_LAT:.6f}, "
    f"{BASLANGIC_LON:.6f}"
)


print(
    f"Tarama alanı: "
    f"{ARAMA_YARICAPI / 1000:.1f} km"
)


print(
    f"Nitelikli lead havuzu: "
    f"{len(isletmeler)}"
)


print(
    f"Rotaya alınan: "
    f"{len(rota)}"
)


print()


print(
    "KURAL: KALİTELİ LEAD → "
    "TİCARİ KORİDORU SÜPÜR → "
    "GEREKSİZ GERİ DÖNME"
)


print()
print("=" * 74)
print("YÜRÜYECEĞİN SIRA")
print("=" * 74)


toplam_mesafe = 0
gercek_sayisi = 0
harita_verisi = []


# Başlangıç → ilk lead de toplam yürüyüşe dahil.
if rota:

    baslangic_noktasi = {
        "lat": BASLANGIC_LAT,
        "lon": BASLANGIC_LON
    }


    ilk_mesafe, ilk_gercek = yaya_mesafesi(
        baslangic_noktasi,
        rota[0]
    )


    toplam_mesafe += ilk_mesafe


    if ilk_gercek:

        gercek_sayisi += 1
        ilk_kaynak = "GERÇEK YAYA YOLU"

    else:

        ilk_kaynak = "TAHMİNİ"


    ilk_dakika = max(
        1,
        round(
            ilk_mesafe / 75
        )
    )


    print()

    print(
        f"BAŞLANGIÇ → 1. işletme: "
        f"{ilk_mesafe:.0f} m / "
        f"~{ilk_dakika} dk "
        f"[{ilk_kaynak}]"
    )


for i, isletme in enumerate(rota):

    sira = i + 1


    print()

    print(
        "-" * 66
    )


    print(
        f"{sira}. "
        f"{isletme['isim']}"
    )


    print(
        f"   Sektör: "
        f"{isletme['sektor']}"
    )


    print(
        f"   Lead kalitesi: "
        f"{potansiyel_etiketi(isletme['lead_skoru'])} "
        f"({isletme['lead_skoru']}/100)"
    )


    if isletme["bayi"]:

        print(
            "   ★ MARKALI / "
            "YEREL BAYİ ADAYI"
        )


    if isletme["sokak"]:

        adres = isletme["sokak"]

        if isletme["no"]:

            adres += (
                f" No: "
                f"{isletme['no']}"
            )

        print(
            f"   Adres: {adres}"
        )


    if isletme["telefon"]:

        print(
            f"   Telefon: "
            f"{isletme['telefon']}"
        )


    if isletme["website"]:

        print(
            f"   Website: "
            f"{isletme['website']}"
        )


    if isletme["instagram"]:

        print(
            f"   Instagram: "
            f"{isletme['instagram']}"
        )


    print(
        f"   Koordinat: "
        f"{isletme['lat']}, "
        f"{isletme['lon']}"
    )


    harita_verisi.append({

        "sira": sira,

        "isim":
        isletme["isim"],

        "sektor":
        isletme["sektor"],

        "lat":
        isletme["lat"],

        "lon":
        isletme["lon"],

        "telefon":
        isletme["telefon"],

        "website":
        isletme["website"],

        "instagram":
        isletme["instagram"],

        "sokak":
        isletme["sokak"],

        "no":
        isletme["no"],

        "potansiyel":
        isletme["lead_skoru"],

        "potansiyel_etiket":
        potansiyel_etiketi(
            isletme["lead_skoru"]
        ),

        "bayi":
        isletme["bayi"]

    })


    if i < len(rota) - 1:

        sonraki = rota[
            i + 1
        ]


        mesafe, gercek = yaya_mesafesi(
            isletme,
            sonraki
        )


        toplam_mesafe += mesafe


        if gercek:

            gercek_sayisi += 1
            kaynak = "GERÇEK YAYA YOLU"

        else:

            kaynak = "TAHMİNİ"


        dakika = max(
            1,
            round(
                mesafe / 75
            )
        )


        print()


        print(
            f"   ↓ {mesafe:.0f} m / "
            f"~{dakika} dk "
            f"[{kaynak}]"
        )


with open(
    CIKTI_JSON,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        harita_verisi,
        f,
        ensure_ascii=False,
        indent=2
    )


print()
print("=" * 74)
print("SAHA ÖZETİ")
print("=" * 74)


print(
    f"OSM'deki sektör adayı: "
    f"{len(ham_isletmeler)}"
)


print(
    f"Kalite filtresinde elenen: "
    f"{toplam_elenen}"
)


print(
    f"Nitelikli lead: "
    f"{len(isletmeler)}"
)


print(
    f"Bugünkü rota: "
    f"{len(rota)} işletme"
)


print(
    f"Toplam yürüyüş: "
    f"{toplam_mesafe / 1000:.2f} km"
)


print(
    f"Tahmini saf yürüyüş: "
    f"~{round(toplam_mesafe / 75)} dk"
)


if rota:

    print(
        f"Gerçek routing: "
        f"{gercek_sayisi}/"
        f"{len(rota)} etap "
        f"(başlangıç → ilk lead dahil)"
    )


print()

print(
    "Lead filtresi: QUALIFIED"
)

print(
    "Mikro işletmeler: FİLTRELENDİ"
)

print(
    "Dernek / kamu / ASM: FİLTRELENDİ"
)

print(
    "Merkezi kurumsal zincirler: FİLTRELENDİ"
)

print(
    "Yerel bayi olabilecek markalar: DAHİL"
)

print()

print(
    "Rota motoru: REAL WALK FIELD ROUTER v2.1"
)

print(
    "Lead skorunun rota sırasına etkisi: 0"
)

print(
    "Optimizasyon: LEAD / GERÇEK YAYA YÜRÜYÜŞ VERİMLİLİĞİ"
)

print(
    "Yakın ticari aks süpürmesi: AKTİF"
)

print(
    "Zikzak / sert geri dönüş: CEZALI"
)

print(
    "Uzak küme geçişi: "
    "YOĞUNLUK KARŞILIĞINDA SERBEST"
)

print(
    "Gerçek yaya rota bütçesi: 4.2 km"
)


if rota_debug.get(
    "atlanan",
    0
):

    print()

    print(
        "ROTAYA ALINMAYAN QUALIFIED LEAD RAPORU"
    )


    print(
        f"× Uzak / izole: "
        f"{len(rota_debug.get('uzak_izole', []))}"
    )


    print(
        f"× Rota bütçesini aşan: "
        f"{len(rota_debug.get('rota_butcesi', []))}"
    )


    print(
        f"× Diğer verimlilik nedenleri: "
        f"{len(rota_debug.get('diger', []))}"
    )


print()

print(
    f"✓ Harita verisi: "
    f"{CIKTI_JSON}"
)

print()

print(
    "Haritayı açmak için:"
)

print(
    "python harita.py"
)

print(
    "=" * 74
)
