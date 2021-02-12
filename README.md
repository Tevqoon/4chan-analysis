# Besedni zaklad na spletnem portalu 4chan


Analiziral bom različne "boarde" in objave na le-teh ter sestavil slovar besed glede na njihovo uporabljenost.
Omejil se bom na tiste, kategorizirane z "Interests", "Creative", pa tudi "Random" in "Politically incorrect".

Ogleda strani zaradi mentalnega zdravja bralca ne priporočam.
[4chan] https://4chan.org

Zajel bom le tekstovne podatke, naredil model besednjaka glede na board, 
ter poskušal ugotoviti register celotne strani ter posameznih boardov.
Z danimi podatki bom analiziral specifično stopnjo vulgarnosti in podobnih
osebnostnih lastnosti, ki se zarodijo v popolnoma anonimnih situacijah.
Podatke bom primerjal z vsakdanjim registrom angleškega govora.

### Delovne hipoteze:
* /b/ in /pol/ sta slabša v vseh metrikah kot ostali boardi
* Vsi boardi so slabši od vsakdanjega registra
* Hujše objave so popularnejše
* Obstaja vsaj en board ki ni usrana luknja

## Navodila za zajem podatkov:

Zagnati je treba *scrapery.py*. Le-ta ima znotraj kode opcije **DOWNLOAD**, **REDOWNLOAD** in **RESTITCH**.
Če je prva True, program dejansko nalaga datoteke. Druga kontrolira, ali program skuša ponovno vzeti in zamenjati
že naložene - če je False, kot je by default, podatke, iz danega boarda, ki so že naloženi, pusti pri miru. Zadnja
pa kontrolira, ali program ponovno shrani končno datoteko *total_dataset.csv*, ki vsebuje vse objave v eni tabeli.
Če uporabnik doda ali odstrani kakšen board iz seznama *boards*, se bo ta po potrebi ali snel iz 4chana ali se 
izbrisal iz *total_dataset*.

## Podatki:

Podatki so sneti iz spletnega portala 4chan, prek njegovega json API-ja. Te sprocesiramo v podatkovni okvir,
jim ekstrahiramo želene atribute ter jih spravimo v skupno datoteko *total_dataset.csv*.

Zajeti atributi so:
+ no - število objave
+ resto - id starša objave
+ now - datum in čas objave
+ com - vsebina objave
+ replies - število odgovorov na objavo
+ board - board, iz katerega je objava

## Analiza:

Narejena analiza je večinoma tekstovna prek konstrukcije in primerjave frekvenčnih leksikonov. Tih vulgarnost je
ocenjena v raznih situacijah in pod različnimi pogoji. Narejena je v Jupyter-ju v datoteki *analysisery.ipynb*.
Poleg postavljenih hipotez postavimo osnovni klasifikator teksta ali korpusa glede na podobnost besednjaka le-tega
in različnih boardov. Tako lahko za dovolj veliko količino teksta napovemo, iz katerega boarda je, ali kateremu
bi realistično pripadal.