# Knowledge Graph + RAG Hybrid

Pattern pratico per ridurre le allucinazioni multi-hop combinando Grafi della Conoscenza e RAG. Migliora la qualità delle risposte del modello su query complesse enterprise.

## Descrizione

Il progetto implementa un knowledge graph (KG) in formato TTL che rappresenta entità aziendali (prodotti, clienti, progetti, relazioni) e una pipeline RAG ibrida che:
- interroga il KG per recuperare contesto strutturato rilevante rispetto a una query in linguaggio naturale
- formatta i risultati in un prompt ottimizzato per il modello Qwen3.6-35B
- fornisce istruzioni per eseguire l'inferenza manualmente quando le GPU sono disponibili

L'approccio riduce le allucinazioni fornendo al LLM fatti verificati dal KG prima della generazione.

## Architettura

- `schema/knowledge_graph.ttl` – ontologia e dati di esempio del knowledge graph
- `scripts/ingest_kg.py` – script per caricare/aggiornare il KG (attualmente legge il file TTL e lo rende disponibile per query SPARQL semplici)
- `scripts/rag_hybrid.py` – pipeline RAG ibrida: esegue una query di testo sul KG, estrae nodi e relazioni pertinenti, costruisce un prompt per il LLM
- `src/` – eventuale codice sorgente aggiuntivo (moduli di utilità)
- `data/` – directory per dati di input/output (es. risultati di ingestione, cache)

Il flusso tipico:
1. Ingestione del KG (popolamento iniziale o aggiornamento)
2. Query utente in linguaggio naturale
3. Recupero di sottografo rilevante tramite pattern di matching semplici (basato su etichette e proprietà)
4. Costruzione di un prompt che include il contesto estratto
5. Output del prompt pronto per l'inferenza manuale su Qwen3.6-35B (Tesla P40)

## Installazione

1. Clonare il repository
2. (Facoltativo) Creare un ambiente virtuale Python e attivarlo
3. Installare le dipendenze:
   ```bash
   pip install --user -r requirements.txt
   ```
   Se non esiste un `requirements.txt`, le dipendenze principali sono:
   - `rdflib` per il parsing e la query del knowledge graph
   - eventuali altri pacchetti indicati negli script
4. Verificare che gli script siano eseguibili:
   ```bash
   chmod +x scripts/*.py
   ```

## Uso

### Ingestione del knowledge graph
```bash
python3 scripts/ingest_kg.py
```
Lo script legge `schema/knowledge_graph.ttl` e prepara il KG per le query successive (al momento mantiene il grafico in memoria).

### Avvio della pipeline RAG ibrida
```bash
python3 scripts/rag_hybrid.py "La tua domanda qui"
```
Lo script:
- esegue una ricerca di testo leggera sul KG (matching su label e proprietà)
- restituisce un prompt formattato che include il contesto recuperato
- stampa le istruzioni per eseguire l'inferenza manualmente con Qwen3.6-35B sulla Tesla P40

### Esempio di utilizzo
```bash
python3 scripts/rag_hybrid.py "Qual è il budget del progetto Sistema CRM?"
```
Output atteso: un prompt che contiene le informazioni sul progetto Sistema CRM estratte dal KG, seguito da indicazioni su come passare quel prompt al modello LLM.

## Stato

✅ Fase 1/5 — Inizializzazione progetto: completata (2026-06-11)
✅ Fase 2/5 — Definizione schema KG: completata (2026-06-11)
✅ Fase 3/5 — Script di ingestione dati: completata (2026-06-11)
✅ Fase 4/5 — Pipeline RAG ibrida (senza esecuzione GPU): completata (2026-06-11)
✅ COMPLETATO — 2026-06-11: progetto finito, documentazione aggiornata, pronto per uso futuro con GPU.

## Licenza

Questo progetto è rilasciato sotto licenza MIT - vedi file LICENSE per dettagli.