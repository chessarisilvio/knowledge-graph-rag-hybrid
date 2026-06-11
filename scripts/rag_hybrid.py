#!/usr/bin/env python3
"""
Pipeline RAG ibrida per Knowledge Graph.
- Interroga il KG per recuperare nodi rilevanti rispetto a una query.
- Formatta i risultati in un prompt per Qwen3.6-35B.
- Fornisce istruzioni per lanciare l'inferenza manualmente quando le GPU sono libere.
"""

import os
import sys
from rdflib import Graph, URIRef, Literal
from rdflib.namespace import RDF, RDFS

def load_knowledge_graph():
    """Carica il grafo della conoscenza dal file TTL."""
    # Percorso relativo allo script
    ttl_path = os.path.join(os.path.dirname(__file__), '..', 'schema', 'knowledge_graph.ttl')

    if not os.path.exists(ttl_path):
        print(f"Errore: File TTL non trovato in {ttl_path}")
        sys.exit(1)

    g = Graph()
    try:
        g.parse(ttl_path, format='turtle')
    except Exception as e:
        print(f"Errore durante il parsing del file TTL: {e}")
        sys.exit(1)

    return g

def query_knowledge_graph(graph, query_string):
    """
    Esegue una ricerca basata su parole chiave nel KG.
    Estrae parole chiave dalla query (escludendo stopword comuni) e cerca nei valori literal
    e nelle etichette RDFS.label dei soggetti.
    Restituisce un elenco di tripletti (soggetto, predicato, oggetto) che corrispondono.
    """
    # Definisci alcune stopword italiane/inglesi da escludere
    stopwords = set([
        "il", "lo", "la", "i", "gli", "le", "un", "uno", "una", "di", "a", "da", "in", "con", "su", "per", "tra", "fra",
        "e", "o", "ma", "che", "chi", "cui", "qual", "quale", "quali", "quanto", "quanta", "quanti", "quante",
        "è", "sono", "sei", "siamo", "siete", "was", "were", "is", "are", "am", "be", "been", "being",
        "to", "of", "in", "for", "on", "with", "at", "by", "from", "up", "about", "into", "over", "after",
        "il", "lo", "la", "i", "gli", "le", "un", "uno", "una", "del", "dello", "della", "dei", "degli", "delle",
        "al", "allo", "alla", "ai", "agli", "alle", "dal", "dallo", "dalla", "dai", "dagli", "dalle",
        "nel", "nello", "nella", "nei", "negli", "nelle", "col", "collo", "colla", "coli", "colgli", "colle",
        "sul", "sullo", "sulla", "sui", "sugli", "sulle"
    ])

    # Estrai parole chiave: splitta per non-alfanumerico, converte in lowercase, rimuovi stopword e parole troppo corte
    import re
    words = re.findall(r'\b\w+\b', query_string.lower())
    keywords = [w for w in words if w not in stopwords and len(w) > 2]

    # Se non ci sono keyword significative, usa l'intera query come fallback
    if not keywords:
        keywords = [query_string.lower()]

    results = []
    seen = set()  # Per evitare duplicati

    for subject, predicate, obj in graph:
        match = False
        # Controlla se l'oggetto è un literal e contiene qualsiasi keyword
        if isinstance(obj, Literal):
            obj_str = str(obj).lower()
            if any(keyword in obj_str for keyword in keywords):
                match = True
        # Controlla anche l'etichetta RDFS.label del soggetto
        elif isinstance(subject, URIRef):
            for label in graph.objects(subject, RDFS.label):
                if isinstance(label, Literal):
                    label_str = str(label).lower()
                    if any(keyword in label_str for keyword in keywords):
                        match = True
                        break
        # Inoltre, controlla se il predicato è rilevante (opzionale)
        # Per ora, saltiamo il controllo sul predicato

        if match:
            # Crea una tupla hashable per evitare duplicati
            key = (str(subject), str(predicate), str(obj))
            if key not in seen:
                seen.add(key)
                results.append((subject, predicate, obj))

    return results

def format_prompt(query, kg_results):
    """
    Formatta i risultati del KG in un prompt per il LLM.
    """
    if not kg_results:
        kg_context = "Non sono state trovate informazioni rilevanti nel knowledge graph."
    else:
        kg_context_lines = []
        for subject, predicate, obj in kg_results:
            # Formatta la tripletta in modo leggibile
            pred_label = str(predicate).split('#')[-1] if '#' in str(predicate) else str(predicate).split('/')[-1]
            kg_context_lines.append(f"- {pred_label}: {obj}")
        kg_context = "Informazioni rilevanti dal knowledge graph:\n" + "\n".join(kg_context_lines)

    prompt = f"""Sei un assistente esperto di analisi aziendale. Utilizza le seguenti informazioni estratte dal knowledge graph per rispondere alla domanda dell'utente.

{kg_context}

Domanda: {query}

Risposta:"""
    return prompt

def main():
    if len(sys.argv) < 2:
        print("Utilizzo: python3 rag_hybrid.py \"<query>\"")
        print("Esempio: python3 rag_hybrid.py \"Qual è il budget del progetto Sistema CRM?\"")
        sys.exit(1)

    query = sys.argv[1]

    print("Caricamento del knowledge graph...")
    graph = load_knowledge_graph()
    print(f"Knowledge graph caricato: {len(graph)} tripletti.")

    print(f"\nEsecuzione della query: '{query}'")
    results = query_knowledge_graph(graph, query)

    print(f"\nTrovati {len(results)} risultati rilevanti.")

    prompt = format_prompt(query, results)

    print("\n" + "="*60)
    print("PROMPT PER LLM (Qwen3.6-35B):")
    print("="*60)
    print(prompt)
    print("="*60)

    print("\nISTRUZIONI PER L'INFERENZA MANUALE:")
    print("1. Assicurati che le GPU siano libere (controlla l'utilizzo con `nvidia-smi`).")
    print("2. Avvia il server di inferenza per Qwen3.6-35B sulla Tesla P40 (CUDA1).")
    print("   Esempio di comando (da adattare al tuo setup):")
    print("   ./llama-server -m /path/to/Qwen3.6-35B-A3B-IQ4_XS.gguf --port 8090 --host 0.0.0.0 --ctx_size 131072")
    print("3. Invia una richiesta POST al server con il prompt sopra.")
    print("   Esempio con curl:")
    print('   curl -X POST http://localhost:8090/completion -H "Content-Type: application/json" -d \\')
    print('   "{ \"prompt\": \"<INCOLLA_IL_PROMPT_SOPRA>\", \"temperature\": 0.7, \"max_tokens\": 512 }"')
    print("\nNota: Sostituisci <INCOLLA_IL_PROMPT_SOPRA> con il prompt effettivamente stampato sopra.")
    print("      Assicurati di escapare correttamente le doppie quote e i caratteri speciali nel prompt.")

if __name__ == "__main__":
    main()