import os
import sys
import requests
import time
import json  # Aggiunto per gestire il file di indice

def main():
    api_key = os.environ.get("PIXABAY_API_KEY")
    if not api_key:
        print("Errore: API Key non trovata.")
        sys.exit(1)

    try:
        page = int(os.environ.get("INPUT_PAGINA", 1))
        block_size = int(os.environ.get("INPUT_BLOCCO", 100))
    except ValueError:
        page = 1
        block_size = 100

    if block_size > 150:
        block_size = 150

    query = "gaming music"
    os.makedirs("downloads", exist_ok=True)

    url = f"https://freesound.org/apiv2/search/text/?query={query}&token={api_key}&fields=id,name,previews&page_size={block_size}&page={page}"

    print(f"=== ESECUZIONE MANUALE: BLOCCO SINGOLO ===")
    print(f"Richiesta -> Pagina Freesound: {page} | Grandezza blocco: {block_size} file")

    response = requests.get(url, timeout=15)
    if response.status_code != 200:
        print(f"Errore API Freesound: {response.status_code}")
        sys.exit(1)

    data = response.json()
    results = data.get("results", [])

    if not results:
        print(f"La pagina {page} è vuota. Non ci sono più brani per questa ricerca.")
        sys.exit(0)

    scaricati_in_questo_blocco = 0

    for item in results:
        audio_name = item.get("name", f"sound_{item['id']}").replace("/", "_").replace("\\", "_")
        download_url = item.get("previews", {}).get("preview-hq-mp3")

        if not download_url:
            continue

        file_path = os.path.join("downloads", f"{audio_name}.mp3")

        if os.path.exists(file_path):
            continue

        print(f"Download: {audio_name}...")
        try:
            res = requests.get(download_url, timeout=15)
            if res.status_code == 200:
                with open(file_path, "wb") as f:
                    f.write(res.content)
                scaricati_in_questo_blocco += 1
                time.sleep(0.3)
        except Exception as e:
            print(f"Errore sul file {audio_name}: {e}")

    print(f"\nBlocco terminato. Nuovi brani scaricati: {scaricati_in_questo_blocco}")

    # ==========================================
    # NUOVA PARTE: GENERAZIONE AUTOMATICA DEL JSON
    # ==========================================
    print("Aggiornamento dell'indice delle canzoni...")
    tutti_i_file = [f for f in os.listdir("downloads") if f.endswith(".mp3")]
    
    # Salva la lista completa in formato JSON
    with open("downloads/songs.json", "w", encoding="utf-8") as jf:
        json.dump(tutti_i_file, jf, ensure_ascii=False, indent=2)
    
    print(f"File 'downloads/songs.json' aggiornato con successo! Totale tracce indicizzate: {len(tutti_i_file)}")

if __name__ == "__main__":
    main()
