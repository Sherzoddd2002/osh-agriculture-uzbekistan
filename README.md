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
- Tuman/dala prognozi uchun aynan shu hudud va ekinga tegishli tarixiy CSV importi; CSV brauzer ichida qayta ishlanadi.

## Ilmiy va ma’lumot cheklovlari

- MAPSPAM 2020 — tarixiy fazoviy reference; 2026/2027-yil kuzatuvi yoki hosil prognozi emas.
- SIAT rasmiy avtomatik qatorlari viloyat darajasida; ular tuman ma’lumoti sifatida ishlatilmaydi.
- Tuman uchun AI ssenariysi kamida 12 yillik haqiqiy tuman/ekin hosildorlik CSV va mos ERA5-Land mavsumiy qatori talab qiladi.
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


## NASA data qatlamlari

NASA POWER Daily API’dan mavsumiy quyosh radiatsiyasi (`ALLSKY_SFC_SW_DWN`) olinadi va to‘liq qamrov topilganda AI Predict Ridge feature’iga kiritiladi. NASA MODIS MOD13Q1 NDVI/EVI 250 m / 16 kunlik raster qatlami keyingi integratsiyaga rejalashtirilgan; hozircha tuman zonal statistikasiga ulanmagan.
