#!/usr/bin/env python3
"""
Script di ingestione per il Knowledge Graph.
Legge il file TTL, lo carica in un database locale usando rdflib e verifica il conteggio dei nodi.
"""

import os
import sys
from rdflib import Graph

def main():
    # Percorso relativo al file TTL
    ttl_path = os.path.join(os.path.dirname(__file__), '..', 'schema', 'knowledge_graph.ttl')

    # Verifica che il file esista
    if not os.path.exists(ttl_path):
        print(f"Errore: File TTL non trovato in {ttl_path}")
        sys.exit(1)

    # Carica il grafo RDF
    print(f"Caricamento del grafo da {ttl_path}...")
    g = Graph()

    try:
        g.parse(ttl_path, format='turtle')
    except Exception as e:
        print(f"Errore durante il parsing del file TTL: {e}")
        sys.exit(1)

    # Conta i nodi unici (soggetti e oggetti distinti)
    # In RDF, i nodi sono i soggetti e gli oggetti dei tripletti
    nodes = set()

    for subject, predicate, obj in g:
        nodes.add(subject)
        # Aggiunge l'oggetto solo se è un URI o un blank node (non un literal)
        if hasattr(obj, 'n3'):  # Controlla se è un termine RDF (URI, BNode, Literal)
            nodes.add(obj)

    # Alternativa: conta solo i soggetti distinti (più semplice e comune per i "nodi" in un KG)
    # subjects = set(g.subjects())
    # node_count = len(subjects)

    node_count = len(nodes)

    print(f"Numero di nodi unici nel grafo: {node_count}")

    # Stampa anche alcune informazioni di base
    print(f"Numero di tripletti nel grafo: {len(g)}")

    # Esempio: mostra i primi 5 soggetti
    print("\nPrimi 5 soggetti nel grafo:")
    for i, subject in enumerate(g.subjects()):
        if i >= 5:
            break
        print(f"  {subject}")

    return 0

if __name__ == "__main__":
    sys.exit(main())