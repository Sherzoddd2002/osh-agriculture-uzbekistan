# OSH AgroAI Uzbekistan

**O‘zbekiston qishloq xo‘jaligi uchun hududiy ma’lumotlar va hosildorlik tahlili platformasi.**

Public demo: https://sherzoddd2002.github.io/osh-agriculture-uzbekistan/

## AI Predict demo rejimi

Viloyat darajasida SIAT rasmiy qatorlari ishlatiladi. Ayrim tuman/ekin juftliklarida demo proksi MAPSPAM 2020 tuman bazasini ota-viloyat SIAT nisbiy trendi bilan kengaytiradi. Bu tarixiy tuman kuzatuvi emas; demo natijada validatsiya aniqligi ko‘rsatilmaydi. Haqiqiy tuman prognozi uchun aynan shu tuman bo‘yicha kamida 12 yillik tekshirilgan qator kerak.

## Nima bor?

- O‘zbekistonning 14 ta viloyati (ADM1) va 199 ta tumani (ADM2) bo‘yicha interaktiv xarita.
- IFPRI MAPSPAM 2020 v2r2: 46 ekin bo‘yicha maydon, yig‘im maydoni, ishlab chiqarish va hosildorlikning tarixiy fazoviy ko‘rsatkichlari.
- Tuman/viloyat va ekin bo‘yicha qidirish, xaritada rangli ko‘rsatish va hududiy taqqoslash.
- Open-Meteo orqali tanlangan hudud markazi uchun ob-havo ma’lumotlari.
- O‘zbekistonning viloyat darajasidagi SIAT qatorlari mavjud bo‘lgan ekinlar uchun avtomatik AI ssenariysi.
- Global OSH PostgreSQL arxividan alohida eksport qilingach, FAOSTAT QCL milliy qatori (1961–2024) boshqa ekinlar uchun ham FAOSTAT milliy trendi × MAPSPAM 2020 hududiy bazasi ko‘rinishidagi aniq belgilangan proksi ssenariysini beradi.
- Tuman/dala prognozi uchun aynan shu hudud va ekinga tegishli tarixiy CSV importi; CSV brauzer ichida qayta ishlanadi.

## Ilmiy va ma’lumot cheklovlari

- MAPSPAM 2020 — tarixiy fazoviy reference; 2026/2027-yil kuzatuvi yoki hosil prognozi emas.
- SIAT rasmiy avtomatik qatorlari viloyat darajasida; ular tuman ma’lumoti sifatida ishlatilmaydi.
- FAOSTAT QCL milliy ADM0 qatoridir. U viloyat/tuman kuzatuvi emas. FAOSTAT yillik nisbiy trendi MAPSPAM 2020 fazoviy bazasiga qo‘llansa, natija faqat hududiy proksi bo‘ladi; haqiqiy submilliy tarix yoki mustaqil tasdiqlangan prognoz emas.
- Tuman uchun AI ssenariysi kamida 12 yillik haqiqiy tuman/ekin hosildorlik CSV va mos tarixiy iqlim qatori talab qiladi. ERA5-Land birlamchi, ERA5 esa zaxira manba; harorat va yog‘in mavsumiy qamrovi kamida 80% bo‘lishi shart. ET₀ yetarli qamrovda bo‘lsagina model belgisi sifatida qo‘shiladi.
- Prognoz — kelajak ob-havosi uchun tarixiy iqlim normasi ishlatiladigan ssenariy; kafolat yoki kuzatilgan natija emas.
- MAPSPAM rasterining ekvatordagi nominal aniqligi taxminan 9.3 km; mayda dala chegarasi buni yuqori aniqlikdagi o‘lchovga aylantirmaydi.
- GitHub Pages statik hosting: foydalanuvchi hisobi, server-side Python, markaziy ma’lumotlar bazasi yoki doimiy foydalanuvchi fayl saqlash bu MVP tarkibiga kirmaydi.

## Bir martalik GitHub Pages sozlamasi

Birinchi deploydan oldin repository egasi quyidagini bir marta yoqadi:

1. **Settings → Pages** sahifasini oching.
2. **Build and deployment → Source** maydonida **GitHub Actions** ni tanlang.
3. Saqlang. Keyingi `main` push avtomatik build va deploy qiladi.

GitHub Actions workflow ma’lumot paketlarini yig‘adi, tekshiradi va statik saytni joylaydi. GitHub Pages yoqilmagan bo‘lsa, build muvaffaqiyatli tugashi mumkin, lekin deploy bajarilmaydi.

## Deploy

Repository `main` branch'ga push qilinganda GitHub Actions:
1. O‘zbekiston ADM1/ADM2 GeoJSON qatlamlarini yuklab oladi va 14/199 feature count hamda IDlarni tekshiradi.
2. Global OSH repository'dagi tekshirilgan UZB MAPSPAM gzip paketini oladi va 14 viloyat/199 tuman/46 ekin sxemasini tekshiradi.
3. SIAT rasmiy manbalaridan mavjud viloyat hosildorlik qatorlarini tayyorlaydi. SIAT vaqtincha ishlamasa, boshqa modullarni joylash davom etadi va SIAT bo‘limi CSV fallback bilan ishlaydi.
4. Statik saytni GitHub Pages'ga chiqaradi.

## Manbalar va litsenziyalar

- IFPRI MAPSPAM 2020 v2r2 — [DOI](https://doi.org/10.7910/DVN/SWPENT), CC BY-SA 4.0.
- geoBoundaries UZB ADM1/ADM2 — metadata va manba litsenziyalari build hisobotida ko‘rsatiladi; geoBoundaries attribution talab qiladi.
- SIAT — O‘zbekiston Milliy statistika qo‘mitasining rasmiy ko‘rsatkichlari; har bir faylda indicator code, birlik va manba URL saqlanadi.
- Ob-havo — [Open-Meteo](https://open-meteo.com/).

## Ishga tushirish

GitHub Pages manzili:
https://sherzoddd2002.github.io/osh-agriculture-uzbekistan/

Lokal test:
```powershell
python -m http.server 8080
```
So‘ng http://localhost:8080 ni oching. Data paketlari uchun `.github/workflows/pages.yml` dagi build bosqichini bajaring yoki `python scripts/build_data.py --output site/data` buyrug‘ini ishlating.


## FAOSTAT global arxivini O‘zbekiston AI Predict'ga ulash

Global loyiha repozitoriysi o‘zgartirilmaydi. O‘zbekiston sayti statik GitHub Pages bo‘lgani sababli E: diskdagi PostgreSQL'ga to‘g‘ridan-to‘g‘ri ulanmaydi. Faqat global_crop_statistics jadvalidagi source_code=FAOSTAT_QCL va country_iso3=UZB qatorlari read-only SELECT bilan eksport qilinadi.

1. O‘zbekiston repositoriyasini alohida clone qiling (papka mavjud bo‘lsa clone qilmang; git pull ishlating):

   ```powershell
   cd E:\
   git clone https://github.com/Sherzoddd2002/osh-agriculture-uzbekistan.git
   cd E:\osh-agriculture-uzbekistan
   ```

2. Eksportni bajaring:

   ```powershell
   .\ops\export-faostat-uzb.ps1
   ```

Skript mavjud global PostgreSQL 5433 / osh_agriculture_global bazasidan faqat UZB FAOSTAT qatorlarini o‘qiydi. Parol chatga yoki repozitoriyga yozilmaydi; local pgpass.conf ishlatiladi.

3. data/faostat/UZB_QCL.json faylini tekshirib, faqat shu JSON'ni commit/push qiling:

   ```powershell
   git status --short
   git add data/faostat/UZB_QCL.json
   git commit -m "Publish Uzbekistan FAOSTAT QCL history"
   git push origin main
   ```

Exporter bitta normalized crop code bir nechta FAOSTAT item code bilan bog‘langan bo‘lsa, ularni sun’iy birlashtirmaydi va noaniq crop kodini chiqarib tashlaydi. 12 yildan kam yoki 2020 bazaviy yili yo‘q qatorlar audit uchun saqlanadi, ammo proksi bashoratda ishlatilmaydi. FAOSTAT JSON e’lon qilinmaguncha SIAT va CSV rejimlari ishlashda davom etadi.

## NASA data qatlamlari

NASA POWER Daily API’dan mavsumiy quyosh radiatsiyasi (`ALLSKY_SFC_SW_DWN`) olinadi va to‘liq qamrov topilganda AI Predict Ridge feature’iga kiritiladi. NASA MODIS MOD13Q1 NDVI/EVI 250 m / 16 kunlik raster qatlamining birinchi 2025-yil qatori 199 tuman uchun `data/modis/UZB_ADM2_MOD13Q1.json` faylida joylangan. MODIS modelga faqat kamida 12 mos hosil mavsumi va har mavsumda kamida 3 sifatli kompozit bo‘lgandagina kiritiladi.


## NASA MODIS district zonal statistics

The optional MOD13Q1.061 ingestion workflow uses NASA AppEEARS and Earthdata Login secrets to create quality-screened NDVI/EVI summaries for all 199 Uzbekistan ADM2 districts. Output is stored in `data/modis/UZB_ADM2_MOD13Q1.json`. Add repository Actions secrets `NASA_EARTHDATA_USERNAME` and `NASA_EARTHDATA_PASSWORD`, then run the `NASA MODIS — build district vegetation time series` workflow. Each request is limited to 550 days; run incremental date windows to build a longer history. The model consumes MODIS only when at least 12 yield seasons each have three or more valid 16-day composites.
