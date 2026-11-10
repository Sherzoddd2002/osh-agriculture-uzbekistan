# Ma’lumot qamrovi va metodologiya

Ushbu hujjat public startup demo ichiga joylangan yoki undan olinadigan ma’lumotlarni va ularning chegaralarini qayd etadi.

## Tasdiqlangan statik qamrov

| Qatlam | Qamrov | Yil | Litsenziya / holat |
|---|---:|---:|---|
| O‘zbekiston ADM1 | 14 poligon | 2017 boundary vintage | ODbL 1.0 |
| O‘zbekiston ADM2 | 199 poligon | 2020 boundary vintage | CC BY 3.0 IGO |
| IFPRI MAPSPAM | 14 ADM1 + 199 ADM2; 46 ekin | 2020 | CC BY-SA 4.0 |
| SIAT bug‘doy | 13 qishloq xo‘jaligi hududi × 15 yil | 2010–2024 | CC BY 4.0 |
| SIAT kartoshka | 13 qishloq xo‘jaligi hududi × 15 yil | 2010–2024 | CC BY 4.0 |
| SIAT paxta (xom paxta) | 13 qishloq xo‘jaligi hududi × 15 yil | 2010–2024 | CC BY 4.0 |

MAPSPAM paketida 213 ta ma’muriy hudud (14 + 199) va 9,798 ta ekin xulosasi mavjud. Har bir hudud uchun 46 ekin qatori tekshiriladi. `NO_RASTER_CELLS` holatidagi hosildorlik NULL bo‘lib qoladi; NULL qiymat nolga aylantirilmaydi.

## AI Predict metodologiyasi

- Viloyat darajasida (ADM1) SIAT’dan ishlab chiqarish / ekilgan maydon nisbati olinadi. Bu t/ekilgan ga ko‘rsatkich; dala o‘lchovi yoki yig‘ib olingan maydonga asoslangan bevosita hosil o‘lchovi deb talqin qilinmaydi.
- Tuman (ADM2) uchun haqiqiy prognoz rejimida aynan tanlangan tuman va ekinga tegishli kamida 12 yillik CSV kerak. CSV ustunlari: `admin_name,crop_code,year,yield_t_ha`. Dastur `admin_name` va `crop_code` qiymatlarini tanlov bilan solishtiradi.
- Startup namoyishi uchun ayrim tuman/ekin juftliklarida alohida **demo proksi** ishlaydi: MAPSPAM 2020 tuman hosildorligi bazaviy qiymat bo‘ladi; ota-viloyatning SIAT 2010–2024 hosildorlik qatori 2020-yilga nisbatan o‘zgarish koeffitsienti sifatida qo‘llanadi. Shu orqali 2010–2024 tuman proksi qatori shakllantirilib, ERA5-Land iqlim xususiyatlari bilan Ridge modeliga beriladi.
- Hosildorlik qatori ERA5-Land mavsumiy harorat, yog‘in va ET₀ bilan moslashtiriladi.
- Ridge modelining expanding-window OOF MAE ko‘rsatkichi Persistence (o‘tgan yil hosili) benchmarki bilan solishtiriladi.
- Kelajakdagi ob-havo noma’lum bo‘lgani sababli target mavsum uchun oxirgi besh mos mavsumning iqlim normasi ishlatiladi. Natija ssenariy, kafolat yoki rasmiy operativ prognoz emas.

### Demo proksi cheklovlari

Demo proksi haqiqiy tuman yillik kuzatuvi emas: 2010–2024 qiymatlari MAPSPAM 2020 tuman bazasi va ota-viloyat SIAT nisbiy trendidan **hisoblab hosil qilingan**. Shu sababli demo natijada OOF MAE, Persistence MAE, aniqlik foizi yoki ishonch oralig‘i ko‘rsatilmaydi. Natija faqat mahsulot oqimini namoyish qilish va texnik sinov uchun; investitsion, sug‘urta, kredit yoki agronomik qaror uchun tasdiqlangan tuman prognozi sifatida ishlatilmasligi kerak. Haqiqiy tuman modeli uchun mustaqil yillik tuman hosildorligi va zonal iqlim/qishloq xo‘jaligi ma’lumotlari zarur.

## Hali integratsiya qilinmagan manbalar

O‘zbekiston Qishloq xo‘jaligi vazirligining geoaxborot tizimi rasmiy tavsifida ekin konturlari, dala monitoringi hamda yillar kesimida ekin holati/hosildorlik tarixini yuritish vazifalari keltirilgan. Biroq public, qayta foydalanishga ruxsat etilgan eksport/API endpointi ushbu build jarayonida tasdiqlanmagan. Shuning uchun u hozirgi AI modelga ulanmagan.

Sentinel-2 NDVI rasteri, tuproq va sug‘orish konturining zonal statistikasi ham hozirgi release tarkibida emas. Open-Meteo iqlim qiymatlari tanlangan hududning vakillik nuqtasi bo‘yicha olinadi; butun tuman poligoni bo‘yicha zonal o‘rtacha deb ko‘rsatilmaydi.

## Manbalar

- IFPRI MAPSPAM 2020 v2r2: https://doi.org/10.7910/DVN/SWPENT
- geoBoundaries metadata/API: https://www.geoboundaries.org/api/current/gbOpen/UZB/ADM1/ va https://www.geoboundaries.org/api/current/gbOpen/UZB/ADM2/
- SIAT: https://siat.stat.uz/
- SIAT bug‘doy ishlab chiqarish: https://siat.stat.uz/data/1458/?lang=en
- SIAT bug‘doy ekilgan maydoni: https://siat.stat.uz/data/2761/?lang=en
- Open-Meteo: https://open-meteo.com/
- Vazirlik agrogeoaxborot tizimi haqida: https://gov.uz/oz/agro/pages/geoaxborot-tizimi

## Release QA

GitHub Actions build jarayoni har bir release uchun:
- 14 ADM1 va 199 ADM2 feature sonini va noyob IDlarni tekshiradi;
- boundary ID’lar MAPSPAM ID’lariga aynan mosligini tekshiradi;
- 46 crop qatori, NULL/zero qoidasi va MAPSPAM metadata/litsenziyasini tekshiradi;
- SIAT qatorlari uchun 13 ta ADM1 nomi, 2010–2024 yillar va manba metadata’larini tekshiradi;
- Python va JavaScript sintaksisini tekshiradi.
