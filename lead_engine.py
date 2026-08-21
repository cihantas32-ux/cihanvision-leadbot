import requests
import math
import time


# ============================================================
# CIHAN VISION LEAD ENGINE — WEB / MOBILE
# ============================================================

ARAMA_YARICAPI = 1500
MAX_ISLETME = 30
MIN_LEAD_SKORU = 48

OVERPASS_SERVERS = [
    "https://maps.mail.ru/osm/tools/overpass/api/interpreter",
    "https://overpass.private.coffee/api/interpreter",
    "https://overpass-api.de/api/interpreter",
]

OSRM_URL = "https://routing.openstreetmap.de/routed-foot/route/v1/driving"


# ============================================================
# MESAFE
# ============================================================

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


# ============================================================
# SEKTÖR
# ============================================================

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

    if shop in [
        "clothes",
        "shoes",
        "jewelry",
        "optician",
        "florist",
        "gift",
        "mobile_phone",
        "computer",
        "hardware",
        "doityourself",
        "paint",
        "curtain",
        "fabric",
        "cosmetics",
        "perfumery",
        "sports",
        "boutique",
        "pet",
        "travel_agency"
    ]:
        return "Yerel Mağaza / Perakende"

    return None


# ============================================================
# BAYİ MARKALARI
# ============================================================

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


# ============================================================
# MERKEZİ / KURUMSAL ZİNCİRLER
# ============================================================

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


# ============================================================
# TİCARİ OLMAYAN
# ============================================================

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


# ============================================================
# MİKRO İŞLETME
# ============================================================

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


# ============================================================
# DİJİTAL SİNYALLER
# ============================================================

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


# ============================================================
# LEAD SKORU
# ============================================================

def lead_skoru_hesapla(isletme):
    sektor = isletme["sektor"]
    tags = isletme["tags"]

    skor = 28

    sektor_bonus = {
        "Diş Kliniği": 35,
        "Klinik": 32,
        "Mobilya / Dekorasyon": 30,
        "Güzellik / Kuaför": 27,
        "Elektronik / Beyaz Eşya": 25,
        "Ev / Dekorasyon": 24,
        "Otomotiv": 23,
        "Yerel Mağaza / Perakende": 22,
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
        return False

    if merkezi_zincir_mi(isim, tags):
        return False

    if isletme["bayi"]:
        return True

    if mikro_isletme_sinyali(isim):
        guclu_dijital = (
            website_var(tags)
            and telefon_var(tags)
        )

        if not guclu_dijital:
            return False

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

        # Dijital izi olmayan restoran/kafeleri tamamen çöpe atmak yerine
        # isim + konum verisi varsa düşük skorlu aday olarak havuzda tut.
        # Mikro işletme filtresi yukarıda hâlâ aktif.
        if sinyal == 0 and not isim.strip():
            return False

    if isletme["lead_skoru"] < MIN_LEAD_SKORU:
        return False

    return True


# ============================================================
# OVERPASS
# ============================================================

def overpass_indir(query):
    headers = {
        "User-Agent": "CihanVisionLeadBot/3.2",
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Referer": "https://cihanvision-leadbot.onrender.com/",
    }

    son_hatalar = []

    # Her sunucuyu sırayla dene. Bir sunucu sorunluysa diğerine geç.
    for server in OVERPASS_SERVERS:
        for deneme in range(2):
            try:
                r = requests.post(
                    server,
                    data={"data": query},
                    timeout=(8, 28),
                    headers=headers,
                )

                if r.status_code == 200:
                    try:
                        data = r.json()
                    except ValueError:
                        son_hatalar.append(f"{server} JSON döndürmedi")
                        break

                    elements = data.get("elements")
                    if isinstance(elements, list):
                        print(
                            f"OVERPASS OK: {server} | "
                            f"{len(elements)} kayıt",
                            flush=True,
                        )
                        return elements

                    son_hatalar.append(f"{server} geçersiz cevap")
                    break

                son_hatalar.append(
                    f"{server} HTTP {r.status_code}"
                )

                # Kota / geçici sunucu hatalarında kısa bekleyip bir kez daha dene.
                if r.status_code in (429, 500, 502, 503, 504):
                    time.sleep(2 + deneme)
                    continue

                break

            except requests.Timeout:
                son_hatalar.append(f"{server} timeout")
                time.sleep(1 + deneme)

            except requests.RequestException as e:
                son_hatalar.append(
                    f"{server} bağlantı hatası: {type(e).__name__}"
                )
                time.sleep(1)
                break

            except Exception as e:
                son_hatalar.append(
                    f"{server} beklenmeyen hata: {type(e).__name__}"
                )
                break

    print("OVERPASS BAŞARISIZ:", " | ".join(son_hatalar), flush=True)
    return None


# ============================================================
# ROTA
# ============================================================

def rota_olustur(isletmeler, start_lat, start_lon):
    """
    v4.2 — QUALIFIED KORİDOR SWEEP

    Qualified havuzdan başlangıca yakın bir lead seçer ve her adımda
    en yakın kalan qualified lead'e ilerler. Tek adım 550 metreyi
    aşarsa rota biter. Böylece aynı ticari bölgede 15-20 lead
    toplanabilir ama başka mahalleye sert sıçrama yapılmaz.
    """
    if not isletmeler:
        return []

    kalan = isletmeler.copy()
    rota = []

    MAX_ROTA = min(MAX_ISLETME, 20)
    MAX_ADIM = 900
    YAKIN_BONUS = 250

    def mesafe(a, b):
        return haversine(
            a["lat"], a["lon"],
            b["lat"], b["lon"]
        )

    def baslangic_mesafe(a):
        return haversine(
            start_lat, start_lon,
            a["lat"], a["lon"]
        )

    def komsu_sayisi(aday, havuz, yaricap=300):
        return sum(
            1 for diger in havuz
            if diger is not aday
            and mesafe(aday, diger) <= yaricap
        )

    # Başlangıca yakın, aynı zamanda çevresinde başka lead'ler bulunan
    # bir ticari çekirdek seç.
    ilk_adaylar = []
    for aday in kalan:
        d = baslangic_mesafe(aday)
        yogunluk = komsu_sayisi(aday, kalan)
        maliyet = d / max(1.0, 1.0 + min(yogunluk, 6) * 0.25)
        ilk_adaylar.append((maliyet, d, -yogunluk, aday))

    ilk_adaylar.sort(key=lambda x: (x[0], x[1], x[2]))
    _, _, _, ilk = ilk_adaylar[0]

    rota.append(ilk)
    kalan.remove(ilk)

    while kalan and len(rota) < MAX_ROTA:
        mevcut = rota[-1]
        adaylar = []

        for aday in kalan:
            d = mesafe(mevcut, aday)

            # Başka mahalleye sert sıçrama yok.
            if d > MAX_ADIM:
                continue

            yogunluk = komsu_sayisi(aday, kalan)

            # Esas kriter mesafe. Yoğunluk sadece küçük bir avantaj sağlar.
            maliyet = d

            if d <= 120:
                maliyet *= 0.55
            elif d <= YAKIN_BONUS:
                maliyet *= 0.75
            elif d > 550:
                maliyet *= 1.80

            maliyet /= max(
                1.0,
                1.0 + min(yogunluk, 4) * 0.10
            )

            adaylar.append((maliyet, d, aday))

        if not adaylar:
            break

        adaylar.sort(key=lambda x: (x[0], x[1]))
        _, _, sonraki = adaylar[0]

        rota.append(sonraki)
        kalan.remove(sonraki)

    return rota


# ============================================================
# WEB'DEN ÇAĞRILAN ANA FONKSİYON
# ============================================================

def make_leads(lat, lon):
    lat = float(lat)
    lon = float(lon)

    sorgu = f"""
[out:json][timeout:20];
(
  nwr(around:{ARAMA_YARICAPI},{lat},{lon})
    ["amenity"~"^(restaurant|cafe|dentist|clinic)$"];

  nwr(around:{ARAMA_YARICAPI},{lat},{lon})
    ["healthcare"~"^(clinic|dentist|physiotherapist)$"];

  nwr(around:{ARAMA_YARICAPI},{lat},{lon})
    ["shop"~"^(hairdresser|beauty|furniture|interior_decoration|kitchen|bed|carpet|appliance|electronics|electrical|houseware|bathroom_furnishing|lighting|tiles|flooring|car|car_repair|tyres|clothes|shoes|jewelry|optician|florist|gift|mobile_phone|computer|hardware|doityourself|paint|curtain|fabric|cosmetics|perfumery|sports|boutique|pet|travel_agency)$"];
);
out center tags;
"""

    elements = overpass_indir(sorgu)

    if elements is None:
        raise RuntimeError(
            "OSM sunucularından veri alınamadı."
        )

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
            isletme_lat = element.get("lat")
            isletme_lon = element.get("lon")
        else:
            center = element.get("center", {})
            isletme_lat = center.get("lat")
            isletme_lon = center.get("lon")

        if isletme_lat is None or isletme_lon is None:
            continue

        uzaklik = haversine(
            lat,
            lon,
            isletme_lat,
            isletme_lon
        )

        if uzaklik > ARAMA_YARICAPI:
            continue

        bayi = bayi_markasi_mi(
            isim,
            tags
        )

        kayit = {
            "osm_id": osm_id,
            "isim": isim,
            "sektor": sektor,
            "lat": isletme_lat,
            "lon": isletme_lon,

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

            "mesafe_baslangic": uzaklik,
            "bayi": bayi,
            "tags": tags
        }

        kayit["lead_skoru"] = (
            lead_skoru_hesapla(kayit)
        )

        if kaliteli_lead_mi(kayit):
            ham_isletmeler.append(kayit)

    # Duplicate temizliği
    temiz = []

    for aday in ham_isletmeler:
        duplicate = False

        for mevcut in temiz:
            ayni_isim = (
                aday["isim"].strip().lower()
                ==
                mevcut["isim"].strip().lower()
            )

            if not ayni_isim:
                continue

            d = haversine(
                aday["lat"],
                aday["lon"],
                mevcut["lat"],
                mevcut["lon"]
            )

            if d < 25:
                duplicate = True
                break

        if not duplicate:
            temiz.append(aday)

    if not temiz:
        return {
            "leads": [],
            "summary": {
                "raw_osm": len(elements),
                "sector_candidates": len(ham_isletmeler),
                "qualified": 0,
                "route_count": 0,
                "walk_km": 0,
                "walk_min": 0
            }
        }

    rota = rota_olustur(
        temiz,
        lat,
        lon
    )

    # ========================================================
    # ÇIKTI
    # ========================================================

    harita_verisi = []

    toplam_mesafe = 0.0

    onceki = {
        "lat": lat,
        "lon": lon
    }

    for i, isletme in enumerate(rota):
        etap_mesafe = haversine(
            onceki["lat"],
            onceki["lon"],
            isletme["lat"],
            isletme["lon"]
        )

        # Kuş uçuşunu yaklaşık yaya mesafesine dönüştür.
        etap_mesafe *= 1.30

        toplam_mesafe += etap_mesafe

        harita_verisi.append({
            "sira": i + 1,
            "isim": isletme["isim"],
            "sektor": isletme["sektor"],
            "lat": isletme["lat"],
            "lon": isletme["lon"],
            "telefon": isletme["telefon"],
            "website": isletme["website"],
            "instagram": isletme["instagram"],
            "sokak": isletme["sokak"],
            "no": isletme["no"],
            "potansiyel": isletme["lead_skoru"],
            "potansiyel_etiket": potansiyel_etiketi(
                isletme["lead_skoru"]
            ),
            "bayi": isletme["bayi"]
        })

        onceki = isletme

    walk_km = round(
        toplam_mesafe / 1000,
        2
    )

    walk_min = round(
        toplam_mesafe / 75
    )

    return {
        "leads": harita_verisi,

        "summary": {
            "raw_osm": len(elements),
            "sector_candidates": len(ham_isletmeler),
            "qualified": len(temiz),
            "route_count": len(harita_verisi),
            "walk_km": walk_km,
            "walk_min": walk_min
        }
    }
