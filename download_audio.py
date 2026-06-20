import os
import sys
import requests
import time

def main():
    # Recupera la chiave dai Secrets di GitHub
    api_key = os.environ.get("PIXABAY_API_KEY")
    if not api_key:
        print("Errore: API Key non trovata nei segreti di ambiente.")
        sys.exit(1)

    query = "gaming music"
    
    # Configurazione limiti per evitare crash su GitHub Actions
    BATCH_SIZE = 200      # Quanti file scaricare al massimo in QUESTA esecuzione
    TARGET_TOTAL = 1500   # Obiettivo finale della repository
    
    # Crea la cartella di download se non esiste
    os.makedirs("downloads", exist_ok=True)
    
    # Conta quanti file sono già stati scaricati nelle sessioni precedenti
    already_downloaded = [f for f in os.listdir("downloads") if f.endswith(".mp3")]
    current_total_count = len(already_downloaded)
    
    print(f"File attualmente presenti nella repository: {current_total_count}/{TARGET_TOTAL}")
    
    if current_total_count >= TARGET_TOTAL:
        print("Obiettivo di 1500 file raggiunto! Interrompo il processo.")
        sys.exit(0)
        
    downloaded_in_this_session = 0
    page_size = 150
    
    # Partiamo dalla pagina 1 della ricerca
    url = f"https://freesound.org/apiv2/search/text/?query={query}&token={api_key}&fields=id,name,previews&page_size={page_size}"
    
    print(f"Avvio sessione di download incrementale (Max {BATCH_SIZE} file in questo turno)...")

    while url and downloaded_in_this_session < BATCH_SIZE and (current_total_count + downloaded_in_this_session) < TARGET_TOTAL:
        response = requests.get(url)
        
        if response.status_code != 200:
            print(f"Errore API Freesound: {response.status_code}")
            break
            
        data = response.json()
        results = data.get("results", [])
        
        if not results:
            print("Nessun altro risultato trovato su Freesound.")
            break

        for item in results:
            # Controlla se abbiamo raggiunto i limiti fissati per questa sessione o totali
            if downloaded_in_this_session >= BATCH_SIZE or (current_total_count + downloaded_in_this_session) >= TARGET_TOTAL:
                break
                
            audio_name = item.get("name", f"sound_{item['id']}").replace("/", "_").replace("\\", "_")
            download_url = item.get("previews", {}).get("preview-hq-mp3")
            
            if not download_url:
                continue
                
            file_path = os.path.join("downloads", f"{audio_name}.mp3")
            
            # SE IL FILE ESISTE GIÀ, LO SALTA SENZA SCARICARLO DI NUOVO
            if os.path.exists(file_path):
                continue
                
            global_index = current_total_count + downloaded_in_this_session + 1
            print(f"[{global_index}/{TARGET_TOTAL}] In download: {audio_name}...")
            
            try:
                audio_res = requests.get(download_url, timeout=15)
                if audio_res.status_code == 200:
                    with open(file_path, "wb") as f:
                        f.write(audio_res.content)
                    downloaded_in_this_session += 1
                    # Un piccolo delay per rispettare i server ed evitare blocchi ip
                    time.sleep(0.4) 
            except Exception as e:
                print(f"Errore durante il download di {audio_name}: {e}")
                continue
        
        # Passa alla pagina successiva dei risultati di Freesound
        url = data.get("next")
        if url and downloaded_in_this_session < BATCH_SIZE:
            print("Caricamento della pagina successiva di Freesound...")

    print(f"Sessione terminata! Scaricati {downloaded_in_this_session} nuovi file in questo turno.")
    print(f"Totale complessivo nella repository: {current_total_count + downloaded_in_this_session}/{TARGET_TOTAL}")

if __name__ == "__main__":
    main()
