(() => {
"use strict";

const $ = (id) => document.getElementById(id);
const CROP_LIST = [
 ["whea","Bug‘doy"],["rice","Sholi"],["maiz","Makkajo‘xori"],["barl","Arpa"],
 ["mill","Mayda tariq"],["pmil","Marvarid tariq"],["sorg","Jo‘xori"],["ocer","Boshqa donli ekinlar"],
 ["pota","Kartoshka"],["swpo","Batata"],["yams","Yams"],["cass","Maniok"],
 ["orts","Boshqa ildizmevalar"],["bean","Loviya"],["chic","No‘xat"],["cowp","Sigir no‘xati"],
 ["pige","Kabutar no‘xati"],["lent","Yasmiq"],["opul","Boshqa dukkaklilar"],
 ["soyb","Soya"],["grou","Yeryong‘oq"],["cnut","Kokos"],["oilp","Moyli palma"],
 ["sunf","Kungaboqar"],["rape","Raps"],["sesa","Kunjut"],["ooil","Boshqa moyli ekinlar"],
 ["sugc","Shakarqamish"],["sugb","Qand lavlagi"],["cott","Paxta"],["ofib","Boshqa tolali ekinlar"],
 ["coff","Arabika qahvasi"],["rcof","Robusta qahvasi"],["coco","Kakao"],["teas","Choy"],
 ["toba","Tamaki"],["bana","Banan"],["plnt","Plantain"],["citr","Sitrus"],
 ["trof","Tropik mevalar"],["temf","Mo‘tadil iqlim mevalari"],["toma","Pomidor"],
 ["onio","Piyoz"],["vege","Boshqa sabzavotlar"],["rubb","Kauchuk"],["rest","Boshqa ekinlar"]
];
const UZB_NAMES = {
 "republic of karakalpakstan":"Qoraqalpog‘iston Respublikasi",
 "andijan region":"Andijon viloyati","namangan region":"Namangan viloyati","fergana region":"Farg‘ona viloyati",
 "xorazm region":"Xorazm viloyati","navoiy region":"Navoiy viloyati","surxondaryo region":"Surxondaryo viloyati",
 "samarkand region":"Samarqand viloyati","samarqand region":"Samarqand viloyati","tashkent region":"Toshkent viloyati","syrdarya region":"Sirdaryo viloyati","sirdaryo region":"Sirdaryo viloyati","qashqadaryo region":"Qashqadaryo viloyati",
 "jizzakh region":"Jizzax viloyati","bukhara region":"Buxoro viloyati","kashkadarya region":"Qashqadaryo viloyati",
 "termez":"Termiz tumani","nurata":"Nurota tumani","navoi city":"Navoiy shahri","jondor":"Jondor tumani",
 "bukhara":"Buxoro tumani","alat":"Olot tumani","karakul":"Qorako‘l tumani","kasbi":"Kasbi tumani",
 "mirishkar":"Mirishkor tumani","nishan":"Nishon tumani","mubarek":"Muborak tumani",
 "karaulbazar":"Qorovulbozor tumani","nurabad":"Nurobod tumani","shafirkan":"Shofirkon tumani",
 "ramitan":"Romitan tumani","peshku":"Peshku tumani","kagan":"Kogon tumani","kiziltepa":"Qiziltepa tumani",
 "kagan city":"Kogon shahri","bukhara city":"Buxoro shahri","pakhtachi":"Paxtachi tumani",
 "gijduvan":"G‘ijduvon tumani","vabkent":"Vobkent tumani","karmana":"Karmana tumani","navbakhor":"Navbahor tumani",
 "kitab":"Kitob tumani","kamashi":"Qamashi tumani","karshi":"Qarshi tumani","guzar":"G‘uzor tumani",
 "dehkanabad":"Dehqonobod tumani","kasan":"Koson tumani","karshi city":"Qarshi shahri",
 "chirakchi":"Chiroqchi tumani","baysun":"Boysun tumani","muzrabad":"Muzrabot tumani","sherabad":"Sherobod tumani",
 "angor":"Angor tumani","yakkabag":"Yakkabog‘ tumani","shakhrisabz":"Shahrisabz tumani",
 "pastdargom":"Pastdarg‘om tumani","ishtikhan":"Ishtixon tumani","narpay":"Narpay tumani",
 "kattakurgan":"Kattaqo‘rg‘on tumani","khatirchi":"Xatirchi tumani","kattakurgan city":"Kattaqo‘rg‘on shahri",
 "koshrabad":"Qo‘shrabot tumani","samarkand city":"Samarqand shahri","urgut":"Urgut tumani",
 "samarkand":"Samarqand tumani","taylak":"Toyloq tumani","dzhambay":"Jomboy tumani","payarik":"Payariq tumani",
 "akdarya":"Oqdaryo tumani","farish":"Forish tumani","gallyaaral":"G‘allaorol tumani","khiva":"Xiva tumani",
 "karauzyak":"Qorao‘zak tumani","kungrad":"Qo‘ng‘irot tumani","shavat":"Shovot tumani",
 "koshkupir":"Qo‘shko‘pir tumani","amudarya":"Amudaryo tumani","gurlen":"Gurlan tumani","chimbay":"Chimboy tumani",
 "kanlikul":"Qanliko‘l tumani","shumanay":"Shumanay tumani","khojeyli":"Xo‘jayli tumani","kegeyli":"Kegeyli tumani",
 "muynak":"Mo‘ynoq tumani","nukus":"Nukus tumani","takhtakupir":"Taxtako‘pir tumani","nukus city":"Nukus shahri",
 "turtkul":"To‘rtko‘l tumani","uchkuduk":"Uchquduq tumani","khazarasp":"Xazorasp tumani",
 "kanimekh":"Konimex tumani","tamdi":"Tomdi tumani","ellikkala":"Ellikqal’a tumani","khanka":"Xonqa tumani",
 "yangiarik":"Yangiariq tumani","bagat":"Bog‘ot tumani","urgench":"Urganch tumani","beruniy":"Beruniy tumani",
 "yangibazar":"Yangibozor tumani","urgench city":"Urganch shahri","zarafshan city":"Zarafshon shahri",
 "bagdad":"Bag‘dod tumani","yangiabad":"Yangiobod tumani","sariasiya":"Sariosiyo tumani",
 "dzharkurgan":"Jarqo‘rg‘on tumani","termez city":"Termiz shahri","kizirik":"Qiziriq tumani",
 "shurchi":"Sho‘rchi tumani","kumkurgan":"Qumqo‘rg‘on tumani","uzun":"Uzun tumani","altinsay":"Oltinsoy tumani",
 "denau":"Denov tumani","dzhizak city":"Jizzax shahri","bakhmal":"Baxmal tumani","bulungur":"Bulung‘ur tumani",
 "sharof rashidov":"Sharof Rashidov tumani","zafarabad":"Zafarobod tumani","zarbdar":"Zarbdor tumani",
 "zaamin":"Zomin tumani","sardoba":"Sardoba tumani","paxtakor":"Paxtakor tumani","dustlik":"Do‘stlik tumani",
 "khavas":"Xovos tumani","mirzaabad":"Mirzaobod tumani","bekabad":"Bekobod tumani",
 "uzbekistan":"O‘zbekiston tumani","besharik":"Beshariq tumani","sokh":"So‘x tumani",
 "fergana":"Farg‘ona tumani","bekabad city":"Bekobod shahri","bayaut":"Boyovut tumani",
 "shirin city":"Shirin shahri","yangiyer city":"Yangiyer shahri","rishtan":"Rishton tumani",
 "altiarik":"Oltiariq tumani","uchkuprik":"Uchko‘prik tumani","kuvasay city":"Quvasoy shahri",
 "fergana city":"Farg‘ona shahri","pap":"Pop tumani","urtachirchik":"O‘rtachirchiq tumani",
 "gulistan city":"Guliston shahri","saykhunabad":"Sayxunobod tumani","mirzachul":"Mirzacho‘l tumani",
 "arnasay":"Arnasoy tumani","gulistan":"Guliston tumani","akaltin":"Oqoltin tumani",
 "sirdarya":"Sirdaryo tumani","kuyichirchik":"Quyi Chirchiq tumani","chinaz":"Chinoz tumani",
 "akhangaran":"Ohangaron tumani","akhangaran city":"Ohangaron shahri","buka":"Bo‘ka tumani",
 "akkurgan":"Oqqo‘rg‘on tumani","pskent":"Piskent tumani","almalik city":"Olmaliq shahri",
 "bektemir":"Bektemir tumani","sergeli":"Sergeli tumani","yangiyul":"Yangiyo‘l tumani",
 "yangiyul city":"Yangiyo‘l shahri","zangiata":"Zangiota tumani","chilanzar":"Chilonzor tumani",
 "uchtepa":"Uchtepa tumani","tashkent":"Toshkent tumani","yakkasaray":"Yakkasaroy tumani",
 "almazar":"Olmazor tumani","shaykhantokhur":"Shayxontohur tumani","yunusabad":"Yunusobod tumani",
 "yukarichirchik":"Yuqori Chirchiq tumani","parkent":"Parkent tumani","angren city":"Angren shahri",
 "kibray":"Qibray tumani","yashnobod":"Yashnobod tumani","mirabad":"Mirobod tumani",
 "mirzo ulugbek":"Mirzo Ulug‘bek tumani","bostanlik":"Bo‘stonliq tumani","chirchik city":"Chirchiq shahri",
 "andijan":"Andijon tumani","ulugnar":"Ulug‘nor tumani","kokand city":"Qo‘qon shahri","furkat":"Furqat tumani",
 "kushtepa":"Qo‘shtepa tumani","buvayda":"Buvayda tumani","dangara":"Dang‘ara tumani",
 "yazyavan":"Yozyovon tumani","mingbulak":"Mingbuloq tumani","khadjaabad":"Xo‘jaobod tumani",
 "kuva":"Quva tumani","tashlak":"Toshloq tumani","margilan city":"Marg‘ilon shahri",
 "markhamat":"Marhamat tumani","asaka":"Asaka tumani","shakhrixan":"Shahrixon tumani",
 "boz":"Bo‘z tumani","djalalkuduk":"Jalolquduq tumani","bulakbashi":"Buloqboshi tumani",
 "kurgantepa":"Qo‘rg‘ontepa tumani","narin":"Norin tumani","chust":"Chust tumani",
 "namangan":"Namangan tumani","turakurgan":"To‘raqo‘rg‘on tumani","balikchi":"Baliqchi tumani",
 "yangikurgan":"Yangiqo‘rg‘on tumani","kasansay":"Kosonsoy tumani","namangan city":"Namangan shahri",
 "uychi":"Uychi tumani","chartak":"Chortoq tumani","khanabad city":"Xonobod shahri",
 "altinkul":"Oltinko‘l tumani","andijan city":"Andijon shahri","uchkurgan":"Uchqo‘rg‘on tumani",
 "izboskan":"Izboskan tumani","paxtaabad":"Paxtaobod tumani","khiva city":"Xiva shahri",
 "nurafshon city":"Nurafshon shahri","shakhrisabz city":"Shahrisabz shahri"
};
const WEATHER_SEASONS = {
 whea:["10-01","06-30"],
 cott:["04-01","10-31"],
 pota:["03-01","09-30"],
 rice:["03-01","09-30"],
 maiz:["03-01","09-30"]
};
const SIAT_FILES = {
 whea:"./data/official-yield/UZB_ADM1_WHEA_2010_2024.json",
 pota:"./data/official-yield/UZB_ADM1_POTA_2010_2024.json",
 cott:"./data/official-yield/UZB_ADM1_COTT_2010_2024.json"
};
const state = {
  adm1:null, adm2:null, mapspam:null, siat:{}, map:null, boundaryLayer:null,
  level:"ADM1", selected:null, selectedProvinceId:"", crop:"whea", boundariesReady:false
};

function escapeHTML(value){
 return String(value ?? "").replace(/[&<>"']/g, ch => ({
  "&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"
 })[ch]);
}
function normalize(value){
 return String(value ?? "").normalize("NFD").replace(/[\u0300-\u036f]/g,"")
  .toLowerCase().replace(/[‘’ʻʼ'\u02bb]/g,"").replace(/\s+/g," ").trim();
}
function featureId(feature){
 const p=feature?.properties||{};
 return String(p.shapeID||p.shape_id||p.shapeISO||"").trim();
}
function featureRawName(feature){
 const p=feature?.properties||{};
 return p.shapeName||p.shape_name||p.shapeNameEn||p.NAME_1||p.NAME_2||p.name||p.NAME||"Hudud";
}
function featureName(feature){
 const raw=String(featureRawName(feature)).trim();
 return UZB_NAMES[normalize(raw)] || raw;
}
function currentAreas(){
 return state.mapspam?.levels?.[state.level]?.areas || {};
}
function areaForFeature(feature, level=state.level){
 const areas=state.mapspam?.levels?.[level]?.areas||{};
 const id=featureId(feature);
 if(id && areas[id])return areas[id];
 const wanted=normalize(featureName(feature));
 const matches=Object.values(areas).filter(row=>normalize(row.name)===wanted);
 return matches.length===1?matches[0]:null;
}
function recordForFeature(feature,crop=state.crop,level=state.level){
 const area=areaForFeature(feature,level);
 return area?.crops?.[crop] ?? null;
}
function fmt(value,digits=0){
 if(value===null||value===undefined||!Number.isFinite(Number(value)))return "—";
 return Number(value).toLocaleString("uz-UZ",{minimumFractionDigits:digits,maximumFractionDigits:digits});
}
function setStatus(text,kind=""){
 const el=$("map-status"); if(!el)return;
 el.textContent=text; el.className=kind?"status-"+kind:"";
}
function loadCropOptions(){
 $("crop-select").innerHTML=CROP_LIST.map(([code,name])=>
  '<option value="'+code+'">'+escapeHTML(name)+' · '+code.toUpperCase()+'</option>'
 ).join("");
 $("crop-select").value="whea";
}

async function fetchJSON(url, label){
 const response=await fetch(url,{cache:"no-cache",headers:{Accept:"application/json, application/geo+json"}});
 if(!response.ok)throw new Error(label+" HTTP "+response.status);
 return response.json();
}
async function loadMapspam(){
 const response=await fetch("./data/mapspam/UZB.json.gz",{cache:"force-cache"});
 if(!response.ok)throw new Error("MAPSPAM paketi HTTP "+response.status);
 if(!("DecompressionStream" in window))throw new Error("Brauzer gzip ochishni qo‘llamaydi. Chrome yoki Edge'ni yangilang.");
 const stream=response.body.pipeThrough(new DecompressionStream("gzip"));
 const payload=await new Response(stream).json();
 if(payload.country_iso3!=="UZB"||payload.dataset_id!=="mapspam-2020-v2r2"||
    payload.source_year!==2020||payload.license!=="CC BY-SA 4.0") {
   throw new Error("MAPSPAM UZB paketi metama’lumot tekshiruvidan o‘tmadi.");
 }
 for(const [level,expected] of [["ADM1",14],["ADM2",199]]){
  const layer=payload.levels?.[level];
  if(!layer||Object.keys(layer.areas||{}).length!==expected)throw new Error(level+" paketida "+expected+" ta hudud topilmadi.");
  for(const area of Object.values(layer.areas)){
   if(Object.keys(area.crops||{}).length!==46)throw new Error(level+" crop qatori 46 ta emas.");
  }
 }
 state.mapspam=payload;
}
async function loadSIAT(){
 const entries=Object.entries(SIAT_FILES);
 await Promise.all(entries.map(async([crop,url])=>{
  try{
   const payload=await fetchJSON(url,"SIAT "+crop);
   if(payload.country_iso3!=="UZB"||payload.admin_level!=="ADM1"||
      payload.crop_code!==crop||payload.license!=="CC BY 4.0"||
      payload.district_yield_available!==false||!Array.isArray(payload.regions)) {
     throw new Error("SIAT metadata mos emas");
   }
   state.siat[crop]=payload;
  }catch(error){
   console.warn("SIAT "+crop+" avtomatik qatori mavjud emas:",error.message);
  }
 }));
}

function colorFor(value,min,max){
 if(value===null||value===undefined||!Number.isFinite(Number(value)))return "#e4e9e1";
 const t=max===min?0.5:Math.max(0,Math.min(1,(Number(value)-min)/(max-min)));
 const stops=[[240,234,193],[151,194,134],[43,119,76]];
 const pos=t*2, i=Math.min(1,Math.floor(pos)), f=pos-i;
 const a=stops[i],b=stops[i+1];
 const rgb=a.map((v,k)=>Math.round(v+(b[k]-v)*f));
 return "rgb("+rgb.join(",")+")";
}
function visibleFeatures(){
 const features=(state.level==="ADM1"?state.adm1:state.adm2)?.features||[];
 if(state.level==="ADM2"&&state.selectedProvinceId){
  return features.filter(f=>String(areaForFeature(f,"ADM2")?.parent_admin_id||"")===state.selectedProvinceId);
 }
 return features;
}
function getValueRange(features){
 const values=features.map(f=>recordForFeature(f)?.yield_t_ha).filter(v=>v!==null&&v!==undefined&&Number.isFinite(Number(v))).map(Number);
 return values.length?{min:Math.min(...values),max:Math.max(...values)}:{min:0,max:1};
}
function styleFeature(feature,range){
 const record=recordForFeature(feature);
 const selected=state.selected&&featureId(feature)===featureId(state.selected);
 return {
  color:selected?"#fff4c9":"#55745a",
  weight:selected?2.5:1,
  opacity:.95,
  fillColor:colorFor(record?.yield_t_ha,range.min,range.max),
  fillOpacity:(record?.yield_t_ha===null||record?.yield_t_ha===undefined)?0.32:0.84
 };
}
function initMap(){
 if(!window.L){setStatus("Leaflet kutubxonasi yuklanmadi. Internet ulanishini tekshiring.","error");return;}
 state.map=L.map("map",{zoomControl:false,scrollWheelZoom:true}).setView([41.2,64.5],5.2);
 L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",{
  maxZoom:18,attribution:'&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap</a>'
 }).addTo(state.map);
 L.control.zoom({position:"topright"}).addTo(state.map);
 renderBoundaryLayer();
 $("zoom-country").addEventListener("click",()=>fitCountry());
 $("map-fullscreen").addEventListener("click",()=>{
  $("map-fullscreen").closest(".map-panel").classList.toggle("fullscreen");
  setTimeout(()=>state.map.invalidateSize(),120);
 });
}
function renderBoundaryLayer(){
 if(!state.map||!state.boundariesReady)return;
 if(state.boundaryLayer){state.map.removeLayer(state.boundaryLayer);state.boundaryLayer=null;}
 const features=visibleFeatures();
 const range=getValueRange(features);
 state.boundaryLayer=L.geoJSON({type:"FeatureCollection",features},{
  style:f=>styleFeature(f,range),
  onEachFeature:(feature,layer)=>{
   const name=featureName(feature);
   const row=recordForFeature(feature);
   const value=row?.yield_t_ha===null||row?.yield_t_ha===undefined?"Ma’lumot mavjud emas":fmt(row.yield_t_ha,2)+" t/ga";
   layer.bindTooltip("<b>"+escapeHTML(name)+"</b><br>"+escapeHTML(value),{sticky:true,direction:"auto"});
   layer.on("click",()=>selectFeature(feature,true));
   layer.on("mouseover",()=>layer.setStyle({weight:2,color:"#fff"}));
   layer.on("mouseout",()=>layer.setStyle(styleFeature(feature,range)));
  }
 }).addTo(state.map);
 if(state.selected&&features.some(f=>featureId(f)===featureId(state.selected))){
  const selectedLayer=state.boundaryLayer.getLayers().find(l=>featureId(l.feature)===featureId(state.selected));
  if(selectedLayer)selectedLayer.setStyle({color:"#fff4c9",weight:3,fillOpacity:.95});
 }
 $("map-title").textContent=state.level==="ADM1"?"O‘zbekiston · Viloyatlar":"O‘zbekiston · Tumanlar va shaharlar";
 $("map-subtitle").textContent=features.length.toLocaleString("uz-UZ")+" ta hudud · "+CROP_LIST.find(c=>c[0]===state.crop)?.[1]+" · 2020";
 setStatus(features.length+" ta hudud xaritaga joylandi · rang hosildorlikni bildiradi.");
}
function fitCountry(){
 if(state.map&&state.boundaryLayer&&state.boundaryLayer.getLayers().length){
  state.map.fitBounds(state.boundaryLayer.getBounds(),{padding:[25,25]});
 }else state.map?.setView([41.2,64.5],5.2);
}
function featureBounds(feature){
 try{return L.geoJSON(feature).getBounds();}catch(_){return null;}
}
function setProvinceOptions(){
 const features=state.adm1?.features||[];
 const select=$("province-select");
 select.innerHTML='<option value="">Barcha viloyatlar</option>'+
  features.map(f=>'<option value="'+escapeHTML(featureId(f))+'">'+escapeHTML(featureName(f))+'</option>').join("");
}
function setDistrictOptions(){
 const select=$("district-select");
 const all=state.adm2?.features||[];
 let features=all;
 if(state.selectedProvinceId){
  features=all.filter(f=>String(areaForFeature(f,"ADM2")?.parent_admin_id||"")===state.selectedProvinceId);
 }
 const query=normalize($("area-search").value);
 if(query)features=features.filter(f=>normalize(featureName(f)).includes(query));
 select.innerHTML='<option value="">Tuman / shaharni tanlang…</option>'+
  features.slice().sort((a,b)=>featureName(a).localeCompare(featureName(b),"uz"))
   .map(f=>'<option value="'+escapeHTML(featureId(f))+'">'+escapeHTML(featureName(f))+'</option>').join("");
 select.disabled=features.length===0;
}
function applyLevel(){
 state.level=$("admin-level").value;
 state.selected=null;
 if(state.level==="ADM1"){
  $("district-select").disabled=true;
  $("district-select").innerHTML='<option value="">ADM1 darajasi tanlangan</option>';
  $("province-select").disabled=false;
  const selectedId=$("province-select").value;
  state.selectedProvinceId=selectedId||"";
 }else{
  $("province-select").disabled=false;
  state.selectedProvinceId=$("province-select").value||"";
  setDistrictOptions();
 }
 renderBoundaryLayer();
 updateSelection(null);
 if(state.level==="ADM1"&&state.selectedProvinceId){
  const f=state.adm1.features.find(x=>featureId(x)===state.selectedProvinceId);
  if(f)selectFeature(f,true);
 }else if(state.level==="ADM2"&&state.selectedProvinceId){
  const province=state.adm1.features.find(x=>featureId(x)===state.selectedProvinceId);
  const bounds=province&&featureBounds(province);
  if(bounds&&bounds.isValid())state.map.fitBounds(bounds,{padding:[28,28]});
 }else fitCountry();
}
function selectFeature(feature,zoom){
 if(!feature)return;
 const level=String(feature.properties?.shapeType||state.level).toUpperCase();
 state.selected=feature;
 if(level==="ADM2"){
  state.level="ADM2";$("admin-level").value="ADM2";
  const row=areaForFeature(feature,"ADM2");
  state.selectedProvinceId=String(row?.parent_admin_id||"");
  $("province-select").value=state.selectedProvinceId;
  setDistrictOptions();
  $("district-select").value=featureId(feature);
 }else{
  state.level="ADM1";$("admin-level").value="ADM1";
  state.selectedProvinceId=featureId(feature);
  $("province-select").value=state.selectedProvinceId;
  $("district-select").disabled=true;
  $("district-select").innerHTML='<option value="">Viloyat darajasi tanlangan</option>';
 }
 renderBoundaryLayer();
 updateSelection(feature);
 if(zoom){
  const bounds=featureBounds(feature);
  if(bounds&&bounds.isValid())state.map.fitBounds(bounds,{padding:[28,28],maxZoom:9});
 }
}
function updateSelection(feature){
 if(!feature){
  $("selected-name").textContent="Hudud tanlanmagan";
  $("selected-meta").textContent="Xaritadan viloyat yoki tumanni tanlang.";
  $("selected-level").textContent="ADM —";
  $("selected-yield").innerHTML="— <em>t/ga</em>";
  $("yield-status").textContent="Hudud tanlanmagan";
  ["selected-production","selected-harvested","selected-physical","selected-cells"].forEach(id=>$(id).textContent="—");
  $("crop-ranking").innerHTML='<div class="empty-state">Hududni tanlang.</div>';
  $("detail-source").textContent="Manba: IFPRI MAPSPAM 2020 v2r2 · CC BY-SA 4.0.";
  $("climate-location").textContent="Hudud tanlanmagan";
  $("forecast-heading").textContent="Avval xaritadan hudud va ekinni tanlang";
  $("forecast-source").textContent="Viloyat darajasida SIAT qatori mavjud ekinlar avtomatik ishlaydi. Tuman uchun CSV kerak.";
  $("weather-temp").textContent="—°";$("weather-label").textContent="Ob-havo ma’lumoti";
  $("weather-rain").textContent="—";$("weather-wind").textContent="—";
  updateForecastAvailability();
  return;
 }
 const level=String(feature.properties?.shapeType||state.level).toUpperCase();
 const area=areaForFeature(feature,level);
 const name=featureName(feature);
 const crop=CROP_LIST.find(x=>x[0]===state.crop);
 const row=recordForFeature(feature,state.crop,level);
 const metadata=state.mapspam?.levels?.[level]||{};
 $("selected-name").textContent=name;
 $("selected-meta").textContent=(level==="ADM1"?"Viloyat / Qoraqalpog‘iston Respublikasi":"Tuman / shahar")+" · "+(area?.name||name);
 $("selected-level").textContent=level+" · UZB";
 if(!row){
  $("selected-yield").innerHTML="— <em>t/ga</em>";
  $("yield-status").textContent="Tanlangan ekin qatori topilmadi";
  ["selected-production","selected-harvested","selected-physical","selected-cells"].forEach(id=>$(id).textContent="—");
 }else if(row.yield_t_ha===null||row.spatial_status==="NO_RASTER_CELLS"){
  $("selected-yield").innerHTML="— <em>t/ga</em>";
  $("yield-status").textContent="Yaroqli raster katak yo‘q · 0 t/ga emas";
  $("selected-production").textContent=fmt(row.production_t);
  $("selected-harvested").textContent=fmt(row.harvested_area_ha);
  $("selected-physical").textContent=fmt(row.physical_area_ha);
  $("selected-cells").textContent=fmt(row.valid_cells);
 }else{
  $("selected-yield").innerHTML=fmt(row.yield_t_ha,2)+' <em>t/ga</em>';
  $("yield-status").textContent="MAPSPAM 2020 · "+fmt(row.valid_cells)+" yaroqli raster katak";
  $("selected-production").textContent=fmt(row.production_t);
  $("selected-harvested").textContent=fmt(row.harvested_area_ha);
  $("selected-physical").textContent=fmt(row.physical_area_ha);
  $("selected-cells").textContent=fmt(row.valid_cells);
 }
 renderCropRanking(area);
 const boundaryYear=area?.boundary_year||metadata.boundary_year||"manbada ko‘rsatilmagan";
 $("detail-source").textContent="IFPRI MAPSPAM 2020 · "+level+" · chegara vintage: "+boundaryYear+" · CC BY-SA 4.0. Grid ~9.3 km (ekvatorda); dala o‘lchovi emas.";
 $("forecast-heading").textContent=name+" · "+(crop?.[1]||state.crop)+" uchun AI ssenariysi";
 $("climate-location").textContent=name;
 renderBoundaryLayer();
 updateForecastAvailability();
 loadWeather(feature).catch(error=>{console.warn(error);$("climate-state").textContent="ULANMADI";});
}
function renderCropRanking(area){
 if(!area?.crops){$("crop-ranking").innerHTML='<div class="empty-state">Ekin xulosasi topilmadi.</div>';return;}
 const rows=Object.entries(area.crops).map(([code,row])=>({
  code,row,name:CROP_LIST.find(c=>c[0]===code)?.[1]||code.toUpperCase()
 })).filter(x=>Number.isFinite(Number(x.row.production_t))&&Number(x.row.production_t)>0)
  .sort((a,b)=>Number(b.row.production_t)-Number(a.row.production_t)).slice(0,5);
 if(!rows.length){$("crop-ranking").innerHTML='<div class="empty-state">Ishlab chiqarish bo‘yicha yetarli qator yo‘q.</div>';return;}
 $("crop-ranking").innerHTML=rows.map((x,i)=>
  '<div class="rank-row"><span class="rank-index">0'+(i+1)+'</span><span class="rank-label"><b>'+escapeHTML(x.name)+'</b><small>'+fmt(x.row.harvested_area_ha)+' ga yig‘im maydoni</small></span><span class="rank-value">'+fmt(x.row.production_t)+' t</span></div>'
 ).join("");
}
function syncCrop(){
 state.crop=$("crop-select").value;
 renderBoundaryLayer();
 if(state.selected)updateSelection(state.selected);
}
function setDataHealth(label,ok){
 const el=$("data-health");
 el.innerHTML='<span class="pulse" style="background:'+(ok?"#6bbf7f":"#d0a45d")+'"></span><span>'+escapeHTML(label)+'</span>';
}
async function loadWeather(feature){
 const bounds=featureBounds(feature);
 if(!bounds||!bounds.isValid())return;
 const center=bounds.getCenter();
 const params=new URLSearchParams({
  latitude:center.lat.toFixed(4),longitude:center.lng.toFixed(4),
  current:"temperature_2m,precipitation,wind_speed_10m",
  daily:"precipitation_sum,temperature_2m_max,temperature_2m_min",
  forecast_days:"7",timezone:"auto"
 });
 const response=await fetch("https://api.open-meteo.com/v1/forecast?"+params.toString(),{signal:AbortSignal.timeout(18000)});
 if(!response.ok)throw new Error("Open-Meteo HTTP "+response.status);
 const data=await response.json();
 const current=data.current||{};
 $("weather-temp").textContent=Number.isFinite(Number(current.temperature_2m))?fmt(current.temperature_2m,0)+"°":"—°";
 $("weather-label").textContent="Joriy harorat · "+(data.timezone||"mahalliy vaqt");
 $("weather-updated").textContent="7 kunlik prognoz · Open-Meteo";
 const rain=(data.daily?.precipitation_sum||[]).slice(0,7).reduce((s,v)=>s+(Number(v)||0),0);
 $("weather-rain").textContent=fmt(rain,1)+" mm";
 $("weather-wind").textContent=fmt(current.wind_speed_10m,1)+" km/soat";
 $("climate-state").textContent="ULANGAN";
}

function parseCSV(text){
 const lines=String(text).replace(/^\uFEFF/,"").split(/\r?\n/).filter(x=>x.trim());
 if(lines.length<9)throw new Error("CSV faylida header va kamida 8 ta kuzatuv bo‘lishi kerak.");
 const first=lines[0],delimiter=(first.match(/;/g)||[]).length>(first.match(/,/g)||[]).length?";":",";
 function split(line){
  const values=[];let current="",quoted=false;
  for(let i=0;i<line.length;i++){
   const ch=line[i];
   if(ch==='"'&&line[i+1]==='"'&&quoted){current+='"';i++;}
   else if(ch==='"')quoted=!quoted;
   else if(ch===delimiter&&!quoted){values.push(current.trim());current="";}
   else current+=ch;
  }
  values.push(current.trim());return values;
 }
 const header=split(first).map(v=>v.trim().toLowerCase());
 const yearIndex=header.indexOf("year");
 const yieldIndex=header.indexOf("yield_t_ha");
 if(yearIndex<0||yieldIndex<0)throw new Error("CSV sarlavhasi year,yield_t_ha bo‘lishi kerak.");
 const rows=lines.slice(1).map((line,index)=>{
  const values=split(line);
  return {year:Number(values[yearIndex]),yield:Number(String(values[yieldIndex]??"").replace(",", ".")),line:index+2};
 }).filter(x=>Number.isInteger(x.year)&&Number.isFinite(x.yield));
 if(rows.length<8)throw new Error("Kamida 8 ta to‘g‘ri year/yield_t_ha kuzatuvi kerak.");
 if(rows.some(x=>x.yield<0||x.yield>1000))throw new Error("Hosildorlik qiymati 0–1000 t/ga oralig‘ida bo‘lishi kerak. Birlikni tekshiring.");
 rows.sort((a,b)=>a.year-b.year);
 if(new Set(rows.map(x=>x.year)).size!==rows.length)throw new Error("CSV ichida takroriy yil bor. Har yil uchun bitta qator qoldiring.");
 return rows.map(({year,yield:yieldValue})=>({year,yield:yieldValue}));
}
function getOfficialSeries(){
 const feature=state.selected;
 if(!feature||String(feature.properties?.shapeType||"").toUpperCase()!=="ADM1")return null;
 const payload=state.siat[state.crop];
 if(!payload)return null;
 const wanted=normalize(featureName(feature));
 const aliases={
  "qoraqalpogiston respublikasi":["qoraqalpogiston","republic of karakalpakstan"],
  "toshkent shahri":["tashkent city"],
  "qashqadaryo viloyati":["kashkadarya region"],
  "surxondaryo viloyati":["surkhandarya region"]
 };
 const item=(payload.regions||[]).find(r=>{
  const key=normalize(r.name_uz);
  return key===wanted||(aliases[wanted]||[]).some(a=>normalize(a)===key);
 });
 if(!item)return null;
 return item.records.map(r=>({year:Number(r.year),yield:Number(r.yield)}))
  .filter(r=>Number.isInteger(r.year)&&Number.isFinite(r.yield)&&r.yield>0)
  .sort((a,b)=>a.year-b.year);
}
function updateForecastAvailability(){
 const button=$("run-forecast"),file=$("yield-csv").files[0];
 const autoSeries=getOfficialSeries();
 const selected=state.selected;
 const crop=CROP_LIST.find(x=>x[0]===state.crop);
 if(!selected){
  button.disabled=true;
  $("forecast-source").textContent="Avval xaritadan viloyat yoki tumanni tanlang.";
  $("forecast-status").textContent="Prognoz uchun hudud tanlanmagan.";
  return;
 }
 const isDistrict=String(selected.properties?.shapeType||"").toUpperCase()==="ADM2";
 if(autoSeries&&!file){
  button.disabled=false;
  $("forecast-source").textContent="SIAT rasmiy viloyat qatori tayyor: "+featureName(selected)+" · "+crop?.[1]+" · 2010–2024. CSV shart emas.";
  $("forecast-status").textContent="Rasmiy SIAT qatori topildi. AI ssenariysini hisoblash mumkin.";
 }else if(file){
  button.disabled=false;
  $("forecast-source").textContent="Tanlangan hudud/ekin uchun foydalanuvchi CSV qatori ishlatiladi. Fayl serverga yuklanmaydi.";
  $("forecast-status").textContent="CSV tanlandi. Uning aynan "+featureName(selected)+" · "+(crop?.[1]||"tanlangan ekin")+" ma’lumoti ekanini tasdiqlang.";
 }else if(isDistrict){
  button.disabled=true;
  $("forecast-source").textContent="Tuman tanlandi. SIAT ochiq qatorlari viloyat darajasida; aynan shu tuman va ekin uchun kamida 8 yillik haqiqiy CSV kerak.";
  $("forecast-status").textContent="Tuman uchun CSV yuklang. Viloyat ko‘rsatkichini tuman prognozi sifatida ishlatmaymiz.";
 }else{
  button.disabled=true;
  $("forecast-source").textContent="Bu viloyat/ekin uchun avtomatik SIAT qatori topilmadi. Aynan shu hudud va ekinga tegishli CSV yuklang.";
  $("forecast-status").textContent="CSV talab qilinadi.";
 }
}
function seasonForYear(year,start,end){
 const [sm,sd]=start.split("-").map(Number),[em,ed]=end.split("-").map(Number);
 const startYear=(sm>em)?year-1:year;
 return {
  start:new Date(Date.UTC(startYear,sm-1,sd)),
  end:new Date(Date.UTC(year,em-1,ed))
 };
}
function dateKey(date){return date.toISOString().slice(0,10);}
async function fetchClimateSeries(center,series,start,end){
 const minYear=Math.min(...series.map(x=>x.year)),maxYear=Math.max(...series.map(x=>x.year));
 const first=seasonForYear(minYear,start,end).start,last=seasonForYear(maxYear,start,end).end;
 const params=new URLSearchParams({
  latitude:center.lat.toFixed(4),longitude:center.lng.toFixed(4),
  start_date:dateKey(first),end_date:dateKey(last),
  daily:"temperature_2m_mean,precipitation_sum,et0_fao_evapotranspiration",
  models:"era5_land",timezone:"UTC"
 });
 const response=await fetch("https://archive-api.open-meteo.com/v1/archive?"+params.toString(),{signal:AbortSignal.timeout(60000)});
 if(!response.ok)throw new Error("ERA5-Land arxiv xizmati HTTP "+response.status);
 const data=await response.json(),daily=data.daily||{};
 const dates=daily.time||[],temps=daily.temperature_2m_mean||[],rain=daily.precipitation_sum||[],et0=daily.et0_fao_evapotranspiration||[];
 const byDate=new Map();
 dates.forEach((date,i)=>byDate.set(date,{temp:temps[i],rain:rain[i],et0:et0[i]}));
 const result={};
 for(const row of series){
  const window=seasonForYear(row.year,start,end);
  const values=[];const cursor=new Date(window.start);
  while(cursor<=window.end){const date=dateKey(cursor),v=byDate.get(date);if(v)values.push(v);cursor.setUTCDate(cursor.getUTCDate()+1);}
  const expected=Math.floor((window.end-window.start)/86400000)+1;
  const valid=key=>values.map(v=>v[key]).filter(v=>v!==null&&v!==undefined&&Number.isFinite(Number(v))).map(Number);
  const t=valid("temp"),p=valid("rain"),e=valid("et0");
  const coverage=Math.min(t.length,p.length,e.length)/expected;
  if(coverage<.8||!t.length||!p.length||!e.length){result[row.year]={usable:false,coverage};continue;}
  result[row.year]={
   usable:true,coverage,
   tmean:t.reduce((a,b)=>a+b,0)/t.length,
   rain:p.reduce((a,b)=>a+b,0),
   et0:e.reduce((a,b)=>a+b,0),
   gdd:t.reduce((s,v)=>s+Math.max(0,v-5),0)
  };
 }
 return result;
}
function solveLinear(matrix,vector){
 const a=matrix.map((row,i)=>row.slice().concat(vector[i])),n=vector.length;
 for(let col=0;col<n;col++){
  let pivot=col;
  for(let row=col+1;row<n;row++)if(Math.abs(a[row][col])>Math.abs(a[pivot][col]))pivot=row;
  if(Math.abs(a[pivot][col])<1e-12)throw new Error("Ridge matritsasi singular.");
  [a[col],a[pivot]]=[a[pivot],a[col]];
  const divisor=a[col][col];
  for(let k=col;k<=n;k++)a[col][k]/=divisor;
  for(let row=0;row<n;row++){
   if(row===col)continue;
   const factor=a[row][col];
   for(let k=col;k<=n;k++)a[row][k]-=factor*a[col][k];
  }
 }
 return a.map(row=>row[n]);
}
function fitRidge(xRows,yRows,xValid,alpha=3){
 const n=xRows.length,p=xValid.length,means=Array(p).fill(0),scales=Array(p).fill(1);
 for(let j=0;j<p;j++)means[j]=xRows.reduce((sum,row)=>sum+row[j],0)/n;
 for(let j=0;j<p;j++){
  const variance=xRows.reduce((sum,row)=>sum+Math.pow(row[j]-means[j],2),0)/n;
  scales[j]=Math.sqrt(variance)||1;
 }
 const yMean=yRows.reduce((a,b)=>a+b,0)/n;
 const xs=xRows.map(row=>row.map((v,j)=>(v-means[j])/scales[j]));
 const matrix=Array.from({length:p},()=>Array(p).fill(0)),vector=Array(p).fill(0);
 for(let i=0;i<n;i++)for(let j=0;j<p;j++){
  vector[j]+=xs[i][j]*(yRows[i]-yMean);
  for(let k=0;k<p;k++)matrix[j][k]+=xs[i][j]*xs[i][k];
 }
 for(let j=0;j<p;j++)matrix[j][j]+=alpha;
 const beta=solveLinear(matrix,vector);
 const valid=xValid.map((v,j)=>(v-means[j])/scales[j]);
 return yMean+valid.reduce((sum,v,j)=>sum+v*beta[j],0);
}
function mean(values){return values.reduce((a,b)=>a+b,0)/values.length;}
function stdev(values){
 const m=mean(values);return Math.sqrt(mean(values.map(v=>Math.pow(v-m,2))));
}
function makeFeatures(aligned,index){
 const previous=aligned.slice(Math.max(0,index-3),index);
 const climate=aligned.slice(Math.max(0,index-5),index).map(x=>x.climate);
 if(previous.length<3||!climate.length)throw new Error("Model feature qatori yetarli emas.");
 return [
  aligned[index].year,
  previous[previous.length-1].yield,
  mean(previous.map(x=>x.yield)),
  stdev(previous.map(x=>x.yield)),
  mean(climate.map(x=>x.tmean)),
  mean(climate.map(x=>x.rain)),
  mean(climate.map(x=>x.et0))
 ];
}
function runYieldRidge(series,climate,targetYear){
 const aligned=series.filter(row=>climate[row.year]?.usable).map(row=>({...row,climate:climate[row.year]}));
 if(aligned.length<8)throw new Error("ERA5-Land bilan kamida 8 ta mavsum mos kelishi kerak. Mos qator: "+aligned.length+" / "+series.length+".");
 const x=[],y=[];
 for(let i=3;i<aligned.length;i++){x.push(makeFeatures(aligned,i));y.push(aligned[i].yield);}
 const oof=[];
 for(let i=5;i<aligned.length;i++){
  const trainX=[],trainY=[];
  for(let j=3;j<i;j++){trainX.push(makeFeatures(aligned,j));trainY.push(aligned[j].yield);}
  const prediction=Math.max(0,fitRidge(trainX,trainY,makeFeatures(aligned,i),3));
  const actual=aligned[i].yield,persistence=aligned[i-1].yield;
  oof.push({year:aligned[i].year,actual,prediction,persistence,error:Math.abs(actual-prediction)});
 }
 if(!oof.length)throw new Error("Expanding-window validatsiya uchun OOF qator hosil bo‘lmadi.");
 const recent=aligned.slice(-5);
 const previous=aligned.slice(-3);
 const futureX=[
  targetYear,
  aligned[aligned.length-1].yield,
  mean(previous.map(x=>x.yield)),
  stdev(previous.map(x=>x.yield)),
  mean(recent.map(x=>x.climate.tmean)),
  mean(recent.map(x=>x.climate.rain)),
  mean(recent.map(x=>x.climate.et0))
 ];
 const forecast=Math.max(0,fitRidge(x,y,futureX,3));
 const mae=mean(oof.map(x=>x.error));
 const persistenceMae=mean(oof.map(x=>Math.abs(x.actual-x.persistence)));
 return {
  forecast,mae,persistenceMae,beatsPersistence:mae<persistenceMae,
  last:aligned[aligned.length-1].yield,lastYear:aligned[aligned.length-1].year,
  rows:aligned.length,oof,coverage:mean(aligned.map(x=>x.climate.coverage)),
  climateNormalYears:recent.map(x=>x.year)
 };
}
function getSelectedCenter(){
 if(!state.selected)return null;
 const bounds=featureBounds(state.selected);
 if(!bounds||!bounds.isValid())return null;
 const center=bounds.getCenter();return {lat:center.lat,lon:center.lng};
}
function showForecastResult(result,target,cropName,areaName,source){
 const lower=Math.max(0,result.forecast-result.mae),upper=result.forecast+result.mae;
 const rows=result.oof.slice(-6).map(row=>'<tr><td>'+row.year+'</td><td>'+fmt(row.actual,2)+'</td><td>'+fmt(row.prediction,2)+'</td><td>'+fmt(row.persistence,2)+'</td><td>'+fmt(row.error,2)+'</td></tr>').join("");
 $("forecast-result").innerHTML=
  '<div class="forecast-kpis">'+
   '<div class="forecast-kpi"><small>'+target+' YIL · AI SSENARIY</small><strong>'+fmt(result.forecast,2)+'</strong><em>tonna / gektar</em></div>'+
   '<div class="forecast-kpi"><small>OOF MAE</small><strong>'+fmt(result.mae,3)+'</strong><em>t/ga · validatsiya xatosi</em></div>'+
   '<div class="forecast-kpi"><small>PERSISTENCE MAE</small><strong>'+fmt(result.persistenceMae,3)+'</strong><em>t/ga · o‘tgan yil baseline</em></div>'+
  '</div>'+
  '<div class="forecast-benchmark"><b>'+escapeHTML(areaName)+' · '+escapeHTML(cropName)+'</b><br>'+
  'Manba: '+escapeHTML(source)+' · oxirgi kuzatuv: '+result.lastYear+' yilda '+fmt(result.last,2)+' t/ga. Taxminiy diapazon: '+fmt(lower,2)+'–'+fmt(upper,2)+' t/ga (± OOF MAE). '+
  'Persistence bilan solishtirish: <b>'+(result.beatsPersistence?"OOF MAE undan past":"OOF MAE undan past emas")+'</b>. Iqlim qamrovi: '+fmt(result.coverage*100,1)+'%.</div>'+
  '<div class="forecast-benchmark">Kelajak ob-havosi kuzatilmagan. Model '+result.climateNormalYears[0]+'–'+result.climateNormalYears[result.climateNormalYears.length-1]+' yillardagi mavsumiy iqlim normasi bilan hisoblandi. Bu ssenariy, kafolat emas.</div>'+
  '<table class="forecast-table"><thead><tr><th>Yil</th><th>Haqiqiy</th><th>Ridge</th><th>Persistence</th><th>|Xato|</th></tr></thead><tbody>'+rows+'</tbody></table>';
}
async function runForecast(){
 const feature=state.selected;
 if(!feature)throw new Error("Avval xaritadan hududni tanlang.");
 const cropName=CROP_LIST.find(x=>x[0]===state.crop)?.[1]||state.crop;
 const target=Number($("target-year").value);
 if(!Number.isInteger(target)||target<2026||target>2040)throw new Error("Maqsadli yil 2026–2040 oralig‘ida bo‘lishi kerak.");
 const inputFile=$("yield-csv").files[0];
 let series,source;
 if(inputFile){
  series=parseCSV(await inputFile.text());
  source="Foydalanuvchi CSV · lokal brauzer";
 }else{
  series=getOfficialSeries();
  if(!series)throw new Error("Tanlangan hudud/ekin uchun rasmiy avtomatik qator yo‘q. CSV yuklang.");
  source="SIAT rasmiy viloyat statistikasi";
 }
 if(series.length<8)throw new Error("Kamida 8 ta yillik kuzatuv kerak.");
 if(target<=series[series.length-1].year)throw new Error("Maqsadli yil oxirgi kuzatilgan yildan keyin bo‘lishi kerak.");
 const start=$("season-start").value.trim(),end=$("season-end").value.trim();
 const valid=value=>{
  if(!/^\d{2}-\d{2}$/.test(value))return false;
  const [m,d]=value.split("-").map(Number),date=new Date(Date.UTC(2000,m-1,d));
  return date.getUTCMonth()===m-1&&date.getUTCDate()===d;
 };
 if(!valid(start)||!valid(end)||start===end)throw new Error("Mavsum sanalari haqiqiy MM-DD formatida bo‘lsin.");
 const center=getSelectedCenter();
 if(!center)throw new Error("Hudud koordinatasi aniqlanmadi.");
 $("run-forecast").disabled=true;
 $("forecast-status").textContent="ERA5-Land mavsumiy qatori olinmoqda. Bu jarayon bir oz vaqt olishi mumkin…";
 try{
  const climate=await fetchClimateSeries(center,series,start,end);
  $("forecast-status").textContent="Iqlim va hosildorlik qatorlari moslandi. Ridge + Persistence validatsiyasi hisoblanmoqda…";
  const result=runYieldRidge(series,climate,target);
  showForecastResult(result,target,cropName,featureName(feature),source);
  $("forecast-status").textContent="Ssenariy tayyor · "+result.rows+" ta mos yield+iqlim yili · CSV serverga yuborilmadi.";
 }finally{
  updateForecastAvailability();
 }
}

function wireUI(){
 $("admin-level").addEventListener("change",applyLevel);
 $("province-select").addEventListener("change",()=>{
  state.selected=null;
  state.selectedProvinceId=$("province-select").value||"";
  if(state.level==="ADM1"){
   renderBoundaryLayer();
   if(state.selectedProvinceId){
    const f=state.adm1.features.find(x=>featureId(x)===state.selectedProvinceId);
    if(f)selectFeature(f,true);else updateSelection(null);
   }else{renderBoundaryLayer();updateSelection(null);fitCountry();}
  }else{
   setDistrictOptions();renderBoundaryLayer();updateSelection(null);
   if(state.selectedProvinceId){
    const f=state.adm1.features.find(x=>featureId(x)===state.selectedProvinceId);
    const bounds=f&&featureBounds(f);if(bounds&&bounds.isValid())state.map.fitBounds(bounds,{padding:[25,25]});
   }else fitCountry();
  }
 });
 $("district-select").addEventListener("change",()=>{
  const id=$("district-select").value;
  const feature=(state.adm2?.features||[]).find(f=>featureId(f)===id);
  if(feature)selectFeature(feature,true);
 });
 $("crop-select").addEventListener("change",()=>{
  state.crop=$("crop-select").value;
  renderBoundaryLayer();
  if(state.selected)updateSelection(state.selected);
 });
 $("area-search").addEventListener("input",()=>{
  if(state.level==="ADM2"){setDistrictOptions();}
  else{
   const q=normalize($("area-search").value);
   const features=state.adm1.features.filter(f=>normalize(featureName(f)).includes(q));
   if(features.length===1)selectFeature(features[0],true);
  }
 });
 $("yield-csv").addEventListener("change",()=>{
  $("csv-label").textContent=$("yield-csv").files[0]?.name||"Tuman yoki boshqa ekin uchun kamida 8 yillik haqiqiy qator";
  updateForecastAvailability();
 });
 $("run-forecast").addEventListener("click",async()=>{
  try{await runForecast();}catch(error){$("forecast-status").textContent=error.message;$("forecast-result").innerHTML='<div class="forecast-empty"><span>!</span><b>Prognoz hisoblanmadi</b><p>'+escapeHTML(error.message)+'</p></div>';}
 });
 $("mobile-menu").addEventListener("click",()=>$("mobile-menu").previousElementSibling.classList.toggle("open"));
 document.querySelectorAll(".nav-link").forEach(link=>link.addEventListener("click",()=>{
  document.querySelectorAll(".nav-link").forEach(x=>x.classList.remove("active"));
  link.classList.add("active");document.querySelector(".main-nav").classList.remove("open");
 }));
}
async function init(){
 loadCropOptions();wireUI();
 if(!window.L){setDataHealth("Xarita kutubxonasi yuklanmadi",false);setStatus("Leaflet CDN yuklanmadi.","error");return;}
 initMap();
 try{
  setStatus("O‘zbekiston ma’lumot qatlamlari yuklanmoqda…");
  const [adm1,adm2]=await Promise.all([
   fetchJSON("./data/boundaries/UZB_ADM1.geojson","UZB ADM1"),
   fetchJSON("./data/boundaries/UZB_ADM2.geojson","UZB ADM2")
  ]);
  if(adm1.type!=="FeatureCollection"||adm1.features?.length!==14)throw new Error("ADM1 chegaralari 14 ta emas.");
  if(adm2.type!=="FeatureCollection"||adm2.features?.length!==199)throw new Error("ADM2 chegaralari 199 ta emas.");
  adm1.features.forEach(f=>{f.properties=f.properties||{};f.properties.shapeType="ADM1";});
  adm2.features.forEach(f=>{f.properties=f.properties||{};f.properties.shapeType="ADM2";});
  state.adm1=adm1;state.adm2=adm2;
  setProvinceOptions();state.boundariesReady=true;
  renderBoundaryLayer();fitCountry();
  setStatus("14 viloyat va 199 tuman chegaralari yuklandi.");
  await loadMapspam();
  $("metric-provinces").textContent="14";$("metric-districts").textContent="199";$("metric-crops").textContent="46";
  setStatus("Hududlar va 2020-yil ekin ma’lumotlari tayyor.");
  setDataHealth("Ma’lumot paketlari tekshirildi · 14 / 199 / 46",true);
  renderBoundaryLayer();updateForecastAvailability();
  loadSIAT().then(()=>updateForecastAvailability());
  applyLevel();
 }catch(error){
  console.error(error);setDataHealth("Ma’lumot yuklashda xato",false);
  setStatus(error.message,"error");
  $("forecast-status").textContent="Ma’lumotlar tayyor bo‘lmagani uchun prognoz vaqtincha o‘chiq.";
 }
}
document.addEventListener("DOMContentLoaded",init);
})();