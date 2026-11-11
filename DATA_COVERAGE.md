# Ma’lumot qamrovi va metodologiya

Ushbu hujjat public startup demo ichiga joylangan yoki undan olinadigan ma’lumotlarni va ularning chegaralarini qayd etadi.

## Tasdiqlangan statik qamrov

| Qatlam | Qamrov | Yil | Litsenziya / holat |
|---|---:|---:|---|
| O‘zbekiston ADM1 | 14 poligon | 2017 boundary vintage | ODbL 1.0 |
| O‘zbekiston ADM2 | 199 poligon | 2020 boundary vintage | CC BY 3.0 IGO |
| IFPRI MAPSPAM | 14 ADM1 + 199 ADM2; 46 ekin; ADM2: 3 409 / 9 154 yaroqli kombinatsiya (37,2%) | 2020 | CC BY-SA 4.0 |
| FAOSTAT QCL Uzbekistan | 21 ekin kodi; 647 yillik yozuv; 20 ta proksi uchun yaroqli qator | 1992–2024 | Milliy ADM0 · FAO |
| NASA MODIS MOD13Q1.061 | 199 ADM2; 14 kompozit sanasi (2 786 tuman-kompozit yozuvi; 2 548 QA-usable) | 2025-03-22–2025-10-16 | NASA LP DAAC / AppEEARS |
| ERA5-Land / ERA5 | Tarixiy kunlik iqlim API’dan hisoblash vaqtida olinadi | API so‘rovi | Vakillik nuqtasi |
| NASA POWER Daily | Quyosh radiatsiyasi API’dan hisoblash vaqtida olinadi | Kunlik API | ~0,5° source grid |
| SIAT bug‘doy | 13 qishloq xo‘jaligi hududi × 15 yil | 2010–2024 | CC BY 4.0 |
| SIAT kartoshka | 13 qishloq xo‘jaligi hududi × 15 yil | 2010–2024 | CC BY 4.0 |
| SIAT paxta (xom paxta) | 13 qishloq xo‘jaligi hududi × 15 yil | 2010–2024 | CC BY 4.0 |

MAPSPAM paketida 213 ta ma’muriy hudud (14 + 199) va 9 798 ta ekin xulosasi mavjud. ADM2 kesimida 199 × 46 = 9 154 ta tuman–ekin kombinatsiyasidan 3 409 tasida (37,2%) yaroqli raster katak va hosildorlik qiymati bor; 5 745 tasida yaroqli raster qiymati yo‘q. 29 tumanda 46 ekinning birortasi uchun ham yaroqli raster katagi topilmagan. `NO_RASTER_CELLS` holatidagi hosildorlik NULL bo‘lib qoladi; NULL qiymat nolga aylantirilmaydi. Bu MAPSPAM fazoviy bahosi, yillik tuman statistika kuzatuvi emas.

## Ob-havo, vegetatsiya va yer qamrovi

- **Open-Meteo Forecast:** joriy ob-havo va 7 kunlik prognoz tanlangan hududning vakillik koordinatasida olinadi.
- **Open-Meteo Historical Weather:** AI hisoblashida ERA5-Land kunlik arxivi birlamchi manba sifatida so‘raladi; kamida 12 ta mos mavsum topilmasa ERA5 zaxirasi sinab ko‘riladi. Bu ma’lumotlar statik JSON paketida saqlanmaydi, foydalanuvchi so‘rovi vaqtida API’dan olinadi. Harorat va yog‘in har mavsumda kamida 80% qamrovga ega bo‘lishi shart; ET₀ yetarli bo‘lsa qo‘shiladi.
- **NASA POWER:** ALLSKY_SFC_SW_DWN quyosh radiatsiyasi kunlik API’dan hisoblash paytida olinadi; taxminan 0,5° panjara bo‘yicha. To‘liq model qatorida kamida 80% kunlik qamrov bo‘lmasa feature qo‘shilmaydi.
- **NASA MODIS:** joriy statik faylda 199 tuman uchun 2025-03-22 dan 2025-10-16 gacha 14 kompozit oynasi (jami 2 786 tuman-kompozit yozuvi) mavjud; 2 548 yozuv loyiha QA quality_usable belgisidan o‘tgan. Har bir tuman uchun yaroqli kompozitlar soni farq qiladi. Bu ko‘p yillik qator emas va hozir AI modelga ulanmagan.
- **Yer/tuproq:** MAPSPAM ekin maydoni va hosil bo‘yicha fazoviy qatlam beradi. Kadastr dala konturlari, tuproq pH/sho‘rlanishi, laboratoriya unumdorligi, sug‘orish va suv ta’minoti bo‘yicha tekshirilgan tuman/dala vaqt qatori hozirgi release’da mavjud emas.

## AI Predict metodologiyasi

- Viloyat darajasida (ADM1) SIAT’dan ishlab chiqarish / ekilgan maydon nisbati olinadi. Bu t/ekilgan ga ko‘rsatkich; dala o‘lchovi yoki yig‘ib olingan maydonga asoslangan bevosita hosil o‘lchovi deb talqin qilinmaydi.
- Tuman (ADM2) uchun haqiqiy prognoz rejimida aynan tanlangan tuman va ekinga tegishli kamida 12 yillik CSV kerak. CSV ustunlari: `admin_name,crop_code,year,yield_t_ha`. Dastur `admin_name` va `crop_code` qiymatlarini tanlov bilan solishtiradi.
- Startup namoyishi uchun ayrim tuman/ekin juftliklarida alohida **demo proksi** ishlaydi: MAPSPAM 2020 tuman hosildorligi bazaviy qiymat bo‘ladi; ota-viloyatning SIAT 2010–2024 hosildorlik qatori 2020-yilga nisbatan o‘zgarish koeffitsienti sifatida qo‘llanadi. Shu orqali 2010–2024 tuman proksi qatori shakllantirilib, ERA5-Land iqlim xususiyatlari bilan Ridge modeliga beriladi.
- Hosildorlik qatori Open-Meteo Historical Weather API’dan olinadigan ERA5-Land mavsumiy harorat va yog‘in, kerak bo‘lsa ET₀ bilan moslashtiriladi; ERA5 zaxira manbasi ham tekshiriladi. Qiymatlar tanlangan hududning vakillik nuqtasiga tegishli.
- NASA POWER Daily Point API’dan `ALLSKY_SFC_SW_DWN` kunlik quyosh radiatsiyasi olinadi. Mavsum bo‘yicha o‘rtacha MJ/m²/kun hisoblanadi va barcha mos hosil yillarida kamida 80% kunlik qamrov mavjud bo‘lsa Ridge modeliga qo‘shimcha feature sifatida kiritiladi. NASA so‘rovi taxminan 0,5° source-grid nuqtasiga yumaloqlanadi va brauzer seansida shu panjara bo‘yicha keshlanadi. NASA API ishlamasa yoki qamrov yetarli bo‘lmasa, model ERA5-Land bilan davom etadi va natijada NASA belgisi ishlatilmagani ko‘rsatiladi.
- Ridge modelining expanding-window OOF MAE ko‘rsatkichi Persistence (o‘tgan yil hosili) benchmarki bilan solishtiriladi.
- Kelajakdagi ob-havo noma’lum bo‘lgani sababli target mavsum uchun oxirgi besh mos mavsumning iqlim normasi ishlatiladi. Natija ssenariy, kafolat yoki rasmiy operativ prognoz emas.

### Demo proksi cheklovlari

Demo proksi haqiqiy tuman yillik kuzatuvi emas: 2010–2024 qiymatlari MAPSPAM 2020 tuman bazasi va ota-viloyat SIAT nisbiy trendidan **hisoblab hosil qilingan**. Shu sababli demo natijada OOF MAE, Persistence MAE, aniqlik foizi yoki ishonch oralig‘i ko‘rsatilmaydi. Natija faqat mahsulot oqimini namoyish qilish va texnik sinov uchun; investitsion, sug‘urta, kredit yoki agronomik qaror uchun tasdiqlangan tuman prognozi sifatida ishlatilmasligi kerak. Haqiqiy tuman modeli uchun mustaqil yillik tuman hosildorligi va zonal iqlim/qishloq xo‘jaligi ma’lumotlari zarur.

## Hali integratsiya qilinmagan manbalar

O‘zbekiston Qishloq xo‘jaligi vazirligining geoaxborot tizimi rasmiy tavsifida ekin konturlari, dala monitoringi hamda yillar kesimida ekin holati/hosildorlik tarixini yuritish vazifalari keltirilgan. Biroq public, qayta foydalanishga ruxsat etilgan eksport/API endpointi ushbu build jarayonida tasdiqlanmagan. Shuning uchun u hozirgi AI modelga ulanmagan.

NASA MODIS MOD13Q1 NDVI/EVI (250 m, 16 kunlik) uchun AppEEARS zonal-statistika pipeline’i qo‘shildi. Joriy e’lon qilingan faylda 2025-03-22–2025-10-16 oralig‘idagi 14 kompozit oynasi va 199 tuman uchun 2 786 yozuv mavjud; ulardan 2 548 tasi loyiha QA mezonidan o‘tgan. Bu hali ko‘p yillik vegetatsiya tarixi emas. Pipeline O‘zbekiston ADM2 chegaralarining soddalashtirilgan union poligonini NASA’ga yuboradi, qaytgan 250 m rastrlarni asl 199 ta tuman geometriyasi bo‘yicha hisoblaydi. NDVI/EVI scale factor 0.0001 qo‘llanadi; VI Quality bitlari orqali bulut, qor, soya, suv va past sifatli piksellar chiqariladi. Tuman/kompozit natijalari `data/modis/UZB_ADM2_MOD13Q1.json` faylida saqlanadi. AI model bu qatlamni faqat kamida 12 ta hosil mavsumi bilan mos va har mavsumda kamida 3 ta sifatli 16 kunlik kompozit bo‘lsa ishlatadi. Sentinel-2 NDVI rasteri, tuproq va sug‘orish konturining zonal statistikasi ham hozirgi release tarkibida emas. Open-Meteo iqlim qiymatlari tanlangan hududning vakillik nuqtasi bo‘yicha olinadi; butun tuman poligoni bo‘yicha zonal o‘rtacha deb ko‘rsatilmaydi.

### NASA MODIS ma’lumotlarini olish

MODIS ma’lumotini olish uchun bepul NASA Earthdata Login hisobidan AppEEARS API tokeni olinadi. Login va parol GitHub Actions Secrets orqali beriladi: `NASA_EARTHDATA_USERNAME` va `NASA_EARTHDATA_PASSWORD`. Maxfiy qiymatlar kodga, commitga yoki brauzerga yozilmaydi. Repozitoriydagi `NASA MODIS — build district vegetation time series` workflow’ini sana oralig‘i bilan qo‘lda ishga tushirish mumkin. AppEEARS bir so‘rovda ko‘pi bilan 550 kun qabul qiladi; 12–15 yillik tarixni bir nechta sana oralig‘ida yuklash kerak.

Sifat filtri VI Quality bitlarida eng yaxshi umumiy sifat (bits 0–1 = 0), VI usefulness ≤ 8, qo‘shni bulut yo‘q, aralash bulut yo‘q, quruqlik, qor yo‘q va soya yo‘q shartlarini qo‘llaydi. Har bir tuman/kompozitda kamida 10 ta sifatli piksel va candidate piksellarning kamida 20% sifatli bo‘lishi talab qilinadi. Bu loyiha ichidagi qat’iy QA siyosati; yaroqsiz qiymatlar NULL bo‘lib qoladi va nolga almashtirilmaydi.

## Manbalar

- IFPRI MAPSPAM 2020 v2r2: https://doi.org/10.7910/DVN/SWPENT
- geoBoundaries metadata/API: https://www.geoboundaries.org/api/current/gbOpen/UZB/ADM1/ va https://www.geoboundaries.org/api/current/gbOpen/UZB/ADM2/
- SIAT: https://siat.stat.uz/
- SIAT bug‘doy ishlab chiqarish: https://siat.stat.uz/data/1458/?lang=en
- SIAT bug‘doy ekilgan maydoni: https://siat.stat.uz/data/2761/?lang=en
- Open-Meteo: https://open-meteo.com/
- NASA POWER Daily API: https://power.larc.nasa.gov/docs/services/api/temporal/daily/
- NASA POWER foydalanuvchi hamjamiyatlari va manba metodologiyasi: https://power.larc.nasa.gov/docs/methodology/communities/
- NASA MODIS MOD13Q1 V6.1 (NDVI/EVI): https://doi.org/10.5067/MODIS/MOD13Q1.061
- Vazirlik agrogeoaxborot tizimi haqida: https://gov.uz/oz/agro/pages/geoaxborot-tizimi

## Release QA

GitHub Actions build jarayoni har bir release uchun:
- 14 ADM1 va 199 ADM2 feature sonini va noyob IDlarni tekshiradi;
- boundary ID’lar MAPSPAM ID’lariga aynan mosligini tekshiradi;
- 46 crop qatori, NULL/zero qoidasi va MAPSPAM metadata/litsenziyasini tekshiradi;
- SIAT qatorlari uchun 13 ta ADM1 nomi, 2010–2024 yillar va manba metadata’larini tekshiradi;
- Python va JavaScript sintaksisini tekshiradi.

## FAOSTAT QCL — global arxivdan UZB milliy qatori

Global OSH arxiv inventarizatsiyasida FAOSTAT QCL qatori 1961–2024 yillar va 202 ta mamlakat/hudud bo‘yicha mavjud. Bu global arxiv diapazoni; O‘zbekiston uchun saytda e’lon qilingan eksport 1992–2024 yillarni qamraydi. Eksportda 21 ta ekin kodi va 647 ta yillik yozuv bor; 20 ta qator kamida 12 yil hamda 2020 bazasi talabiga javob beradi. Soya (soyb) 9 yillik bo‘lgani uchun model proksisida ishlatilmaydi. Geografik daraja ADM0 (milliy); bu viloyat yoki tuman hosildorlik statistikasi emas.

UZB repo ichidagi scripts/export_faostat_uzb.py va ops/export-faostat-uzb.ps1 mavjud osh_agriculture_global PostgreSQL bazasidan faqat SELECT bajaradi va data/faostat/UZB_QCL.json yaratadi. GitHub Pages build ushbu JSON'ni site/data/faostat/ ichiga joylaydi. Maxfiy ma’lumotlar yoki global DB dump eksport qilinmaydi.

AI Predict tanlangan viloyat/tuman bo‘yicha avval SIAT rasmiy qatorini afzal ko‘radi. Mos SIAT qatori yo‘q bo‘lsa, FAOSTAT milliy yillik yield nisbatini (har yil / 2020-yil) MAPSPAM 2020 ADM1/ADM2 bazaviy hosildorligiga qo‘llashi mumkin. Bu FAOSTAT milliy trend proksisi deb belgilanadi; u tarixiy tuman kuzatuvi, rasmiy tuman statistikasi yoki mustaqil submilliy validatsiya emas. MAPSPAM 2020 esa alohida bitta spatial baseline, 46 yillik ma’lumot emas.

FAOSTAT qatorlarida bitta normalized crop code bir nechta FAOSTAT item code bilan bog‘liq bo‘lsa, exporter noaniq qatorlarni chiqarib tashlaydi. 12 yillik kuzatuv va 2020 bazasi bo‘lmagan qatorlar modelga kiritilmaydi. Eksport bo‘yicha Windows ko‘rsatmasi README.md ichidagi FAOSTAT global arxivini O‘zbekiston AI Predict'ga ulash bo‘limida.