🌐 Aplicație de Arhivare Web (Internet Archive Viewer)

Această aplicație Python permite crearea de "snapshot-uri" offline ale paginilor web sau ale unor domenii întregi, permițând vizualizarea ulterioară a conținutului exact așa cum arăta la momentul arhivării. Include un crawler pentru a descoperi pagini și un server web local pentru a naviga prin arhive.

✨ Funcționalități
Arhivare Pagină Unică: Salvează o pagină web specifică împreună cu toate resursele sale (imagini, fișiere CSS, JavaScript, documente).

Arhivare Domeniu Complet: Parcurge recursiv toate paginile accesibile dintr-un domeniu și le arhivează.

Gestionare Resurse: Descarcă și rescrie căile pentru toate resursele statice (.css, .js, .png, .jpg, .pdf etc.) pentru a asigura vizualizarea offline.

Link-uri Offline: Modifică link-urile interne din paginile arhivate pentru a puncta către versiunile locale, permițând navigarea offline.

Dicționar de Pagini de Încercat: Suportă un fișier de dicționar (urls_to_try.txt) pentru a include pagini specifice care ar putea să nu fie descoperite prin crawling-ul obișnuit.

Server Web Local: Un server Flask integrat pentru a naviga ușor prin arhivele create, cu o interfață utilizator modernă și o bară de căutare.

Suport Selenium: Poate utiliza Selenium (cu geckodriver pentru Firefox) pentru a arhiva site-uri cu conținut dinamic generat de JavaScript.

🚀 Cerințe (Prerequisites)
Python 3.x

Un browser web instalat (ex: Mozilla Firefox)

geckodriver (driverul Selenium pentru Firefox)

🚀 Utilizare
Pasul 1: Arhivarea unui Site Web
Deschideți un terminal în directorul rădăcină al proiectului.

Rulați scriptul main.py:

python main.py

Vi se va cere să introduceți URL-ul site-ului pe care doriți să-l arhivați (ex: https://www.davidyeiser.com/ sau http://quotes.toscrape.com/).

Notă despre USE_SELENIUM: În fișierul main.py, puteți seta USE_SELENIUM = True dacă site-ul pe care îl arhivați folosește JavaScript pentru a încărca conținut sau pentru navigare (majoritatea site-urilor moderne). Setați USE_SELENIUM = False pentru site-uri predominant statice, pentru o viteză mai mare de arhivare.

Pasul 2: Vizualizarea Arhivelor cu Serverul Local
După ce arhivarea este completă, deschideți un alt terminal în directorul rădăcină al proiectului.

Rulați scriptul server.py:

python server.py

Deschideți browser-ul web și accesați adresa afișată în consolă (de obicei http://127.0.0.1:5000).

Veți vedea o listă cu toate domeniile arhivate.

Navigați prin domenii, snapshot-uri și pagini.

Utilizați bara de căutare din navbar pentru a găsi rapid arhive.

📁 Structura Proiectului
main.py: Punctul de intrare al aplicației. Inițiază procesul de arhivare.

crawler.py: Implementează logica de crawling recursiv pentru a descoperi paginile dintr-un domeniu.

downloader.py: Se ocupă de descărcarea conținutului HTML și a resurselor (CSS, JS, imagini, PDF-uri) și de rescrierea link-urilor pentru vizualizare offline.

utils.py: Conține funcții utilitare pentru manipularea căilor, URL-urilor și generarea numelor de directoare.

server.py: Serverul web Flask care permite vizualizarea arhivelor în browser.

archive/: Directorul unde sunt salvate toate snapshot-urile. Structura este archive/domeniu/timestamp/nume_pagina/index.html și archive/domeniu/timestamp/nume_pagina/_resources/.

urls_to_try.txt: Fișier opțional cu căi URL suplimentare de încercat în timpul arhivării.

⚠️ Depanare și Note

Verificați dacă USE_SELENIUM = True este setat în main.py pentru site-uri dinamice.

Dacă un link este declanșat de JavaScript complex (nu un simplu <a> tag cu href), este posibil ca aplicația să nu poată replica perfect funcționalitatea offline. Aplicația rescrie atributele HTML, nu logica JavaScript internă.

Resurse lipsă (imagini, CSS, JS): Verificați output-ul consolei din main.py pentru mesaje [skip-resursă]. Asigurați-vă că acele resurse sunt accesibile public și că nu sunt blocate de serverul original.

Erori HTTP (40x, 50x): Site-urile pot bloca scraping-ul. Am adăugat anteturi User-Agent și Accept pentru a imita un browser, dar unele site-uri pot avea măsuri anti-bot mai avansate.
