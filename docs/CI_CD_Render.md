# CI/CD gratuit — GitHub Actions și Render

Scop: aplicația poate fi prezentată de pe orice laptop cu un browser, fără instalarea Java, Node sau a dependențelor pe acel laptop.

## Ce este configurat în repository

- `.github/workflows/ci.yml` rulează la PR, la push pe `main` și manual: teste + pachet backend cu MongoDB temporar, teste + build frontend, apoi build Docker și verificare HTTP a aplicației într-un container limitat la 512 MB RAM.
- `Dockerfile` construiește Angular cu Node 24, include fișierele în JAR-ul Spring Boot și rulează cu Java 21. Aplicația și API-ul sunt servite de același serviciu, pe aceeași adresă. Containerul rulează fără privilegii root.
- `FrontendController` permite deschiderea directă și reîncărcarea rutelor Angular existente, inclusiv URL-urile meciurilor. La adăugarea unor rute noi în `app.routes.ts`, actualizați și aceste mapări și verificarea de deployment.
- Portul este `${PORT:8080}`: Render îl furnizează la pornire, iar local rămâne 8080.
- `.dockerignore` exclude secretele locale, Git, dependențele instalate și rezultatele build-urilor locale. `backend/.env` rămâne necomis și nu este copiat în imagine.
- `render.yaml` declară **un singur Web Service Free**, în Frankfurt, cu branch `main`, runtime Docker, health check `/api/health` și deploy automat numai după trecerea verificărilor CI.
- `tools/smoke_deployment.py` verifică health JSON, opt rute frontend, fișierele JavaScript/CSS și răspunsurile 404 pentru API/asset lipsă și `.env`. Nu solicită date sportive și nu consumă cota API-Sports.

CI nu folosește MongoDB Atlas sau cheia API a echipei. **Nu sunt necesare GitHub Secrets** pentru acest workflow. Docker nu este necesar pe laptop; este disponibil pe runner-ul GitHub și la Render.

## Ce trebuie făcut o singură dată în conturi

### 1. Integrați PR-ul după CI

Verificați pe PR cele trei joburi: `Backend tests`, `Frontend tests and build`, `Docker build and smoke test`. După integrare, verificați și rularea de pe `main`, în tab-ul Actions.

**Blocaj identificat la prima rulare (14.11.2026):** GitHub a refuzat pornirea joburilor din cauza blocării contului pentru o problemă de facturare. Nu a fost alocat un runner, iar build-ul Docker nu a rulat. Proprietarul repository-ului trebuie să verifice problema contului în GitHub Billing/Support, apoi să folosească **Actions → CI → Re-run all jobs**. Configurația CI folosește runner-e standard gratuite pentru acest repository public; modificarea YAML-ului sau cumpărarea unei instanțe Render nu rezolvă blocarea contului GitHub. Verificați că problema este rezolvată și rularea de pe `main` trece înainte de a activa primul deploy după CI.

Opțional, proprietarul repository-ului poate configura protecția branch-ului `main` astfel încât aceste verificări să fie obligatorii înaintea integrării. Configurarea necesită permisiuni de administrare.

### 2. Creați serviciul Render din Blueprint

1. Autentificați-vă în [Render](https://dashboard.render.com/) și conectați contul GitHub, acordând acces la `DoubleF9/sportpulse-mops`.
2. Alegeți **New → Blueprint**, selectați repository-ul și branch-ul `main`. Render va citi `render.yaml` din rădăcină.
3. Verificați că se creează un singur Web Service cu **Instance Type: Free**, în workspace-ul gratuit Hobby. Nu este necesară o bază de date Render sau un disc.
4. La solicitarea valorilor secrete, copiați local valorile din `backend/.env` pentru `MONGODB_URI` și `API_SPORTS_KEY`, fără ghilimele suplimentare. Nu le puneți în fișierele YAML, în PR sau în mesaje publice. Render păstrează valorile între deploy-uri.
5. Numele `sportpulse-mops` poate fi schimbat dacă nu este disponibil. URL-ul final este cel afișat de Render, nu un URL presupus din numele repository-ului.

Alternativ, pentru un serviciu deja creat manual, configurați aceleași opțiuni: Web Service, GitHub conectat, branch `main`, Docker, Root Directory necompletat, Dockerfile `./Dockerfile`, Docker Build Context `.`, Docker Command necompletat, Free, health check `/api/health`. Folosiți o singură metodă pentru a evita două servicii identice.

### 3. Permiteți accesul la MongoDB Atlas

1. În pagina serviciului Render: **Connect → Outbound**. Copiați toate intervalele IP/CIDR afișate.
2. În proiectul MongoDB Atlas: **Network Access / IP Access List**, adăugați acele intervale. Păstrați intrările existente necesare colegilor.
3. Dacă primul deploy a pornit înaintea configurării accesului, folosiți **Manual Deploy → Deploy latest commit** după salvarea setărilor.

IP-urile de ieșire sunt comune regiunii Render; nu sunt IP-uri dedicate. Folosiți intervalele afișate pentru serviciul vostru, nu exemple copiate din documentație.

### 4. Verificați CD și aplicația

- În setările serviciului, **Auto-Deploy: After CI Checks Pass** trebuie să fie activ; este deja declarat în Blueprint. Legătura GitHub este necesară pentru acest comportament.
- Deschideți `/api/health`: trebuie să răspundă cu `{"status":"UP"}`.
- Deschideți pagina principală și verificați meciurile pentru cele trei sporturi. Acest pas verifică și accesul la Atlas/API-Sports; health confirmă numai că serverul Java răspunde.
- Deschideți și reîncărcați `/standings` și un URL real `/matches/{sport}/{id}`.
- Opțional, dintr-un checkout local: `python tools/smoke_deployment.py https://ADRESA-AFISATA-DE-RENDER`. Acesta verifică pachetul și rutarea, fără apeluri către API-Sports.

După configurare, schimbările integrate în `main` sunt testate în GitHub și declanșează deploy-ul Render când verificările trec. Nu este necesar un deploy hook sau un token Render în GitHub.

## Cost și limite

Repository-ul este public, iar workflow-ul folosește runner-e GitHub standard Ubuntu. Acestea sunt gratuite pentru repository-uri publice; nu sunt folosite runner-e mari sau servicii suplimentare plătite.

Render oferă instanțe web Free, dar are limite lunare pentru ore, trafic și minute de build. Pentru a evita facturarea automată a depășirilor, păstrați configurația Free/Hobby și nu adăugați o metodă de plată. Fără metodă de plată, depășirea limitelor poate suspenda serviciul sau opri build-urile până la resetare. Dacă workspace-ul are deja o metodă de plată, verificați separat facturarea și limitele; simpla alegere a instanței Free nu garantează zero cost pentru toate depășirile.

Folosiți în continuare clusterul Atlas și planul API-Sports existente, fără upgrade-uri plătite. Aplicația publicată folosește aceeași cotă API-Sports ca rulările locale cu aceeași cheie. Restricțiile planului API asupra datelor disponibile rămân valabile.

După 15 minute fără trafic, Render Free oprește serviciul; o nouă accesare îl repornește, de obicei în aproximativ un minut. Înaintea prezentării, deschideți aplicația cu 5–10 minute înainte și verificați fluxul. Nu este configurat un serviciu care o menține permanent activă.

## Validare și jurnal AI

Validare locală: 67 teste backend și 58 teste frontend trecute, build de producție Angular și verificarea pachetului Spring Boot cu fișierele Angular incluse. Smoke test HTTP: health, opt rute frontend, JavaScript/CSS și răspunsuri 404. Chrome izolat pe JAR-ul de producție: program, pagină de meci și reîncărcare directă pentru toate cele trei sporturi, schimbarea sportului și aspect mobil. Blueprint-ul trece validarea cu schema JSON oficială Render. Testele noi verifică rutarea directă fără a intercepta API-ul sau fișierele lipsă. Avertizarea SCSS preexistentă pentru pagina principală rămâne.

Docker nu este instalat pe laptopul de lucru. Validarea imaginii Linux și rularea efectivă sub limita de 512 MB sunt făcute de jobul `Docker build and smoke test`; rezultatul trebuie verificat pe PR înaintea integrării. Validarea locală a JAR-ului și validarea Docker sunt verificări distincte. Configurarea contului Render, a secretelor și a accesului Atlas este efectuată de utilizator, iar verificarea aplicației publice se face după primul deploy.

La prima verificare, joburile GitHub au fost blocate înainte de execuție de problema de facturare a contului menționată mai sus. Imaginea Docker și limita de memorie nu sunt declarate validate până când workflow-ul nu rulează cu succes.

Instrument: OpenAI Codex. Solicitare: automatizarea CI/CD pentru o prezentare independentă de laptop, fără costuri pentru proiectul de facultate. Rezultat: workflow, imagine Docker, suport de rutare/port, Blueprint Render și pași pentru echipă. Nu au fost publicate secrete și nu a fost creat un serviciu plătit.

Surse oficiale, verificate la 14.11.2026: [Render Free](https://render.com/docs/free), [Blueprint](https://render.com/docs/blueprint-spec), [deploy după CI](https://render.com/docs/deploys), [IP-uri de ieșire](https://render.com/docs/outbound-ip-addresses), [facturare GitHub Actions](https://docs.github.com/en/billing/concepts/product-billing/github-actions).
