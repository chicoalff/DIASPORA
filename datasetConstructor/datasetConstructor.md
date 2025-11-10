 Act as an expert Python developer and help to design and create code blocks / modules as per the user specification.

 
## OBJETIVO DO SISTEMA

O objetivo é desenvolver uma aplicação em Python que converta arquivos Markdown (.md) em datasets estruturados para uso em LLMs e IA, realizando parsing, limpeza, normalização, e exportação em formatos padronizados como JSONL, prontos para serem utilizadoz como base de conhecimento e/ou fonte de dados para o treinamento e fine-tuning de modelos de LLM e de Inteligência Artificial conversacional.

### Requisitos

1. Ingestão de arquivos Markdown (.md): leitura individual ou em lote, com suporte a diferentes codificações.
2. Parsing estrutural: identificação e extração de títulos, subtítulos, listas, tabelas, blocos de código, citações e links.
3. Normalização de texto: remoção de ruídos, caracteres inválidos, duplicidades e metadados desnecessários.
4. Fragmentação (chunking): divisão inteligente do conteúdo em blocos semânticos com tamanho configurável.
5. Geração de metadados: criação automática de atributos como fonte, idioma, data, seção, tags e identificadores únicos.
6. Exportação padronizada: geração de datasets em formatos JSONL, CSV ou parquet, compatíveis com LLMs.

### Estrutura do projeto

```
diaspora/
│
├── main.py                      # CLI simples: processa .md (arquivo único ou lote)
├── config/
│   └── settings.yaml            # Parâmetros: encodings, tamanho de chunk, formatos de saída
│
├── modules/
│   ├── ingest.py                # Leitura de .md (único/lote), detecção de encoding
│   ├── parse_md.py              # Parsing estrutural: títulos, listas, tabelas, code, citações, links
│   ├── normalize.py             # Limpeza: ruídos, caracteres inválidos, deduplicação, metadados supérfluos
│   ├── chunker.py               # Fragmentação semântica com tamanho configurável e heurísticas
│   ├── metadata.py              # Geração de metadados (fonte, idioma, data, seção, tags, UUID)
│   └── export.py                # Exportação para JSONL, CSV, Parquet
│
├── data/
│   ├── input/                   # Arquivos .md de entrada
│   ├── processed/               # Conteúdo normalizado e chunkado
│   └── output/                  # Datasets finais (JSONL/CSV/Parquet)
│
├── tests/
│   ├── test_parse_md.py
│   ├── test_normalize.py
│   ├── test_chunker.py
│   └── test_export.py
│
├── requirements.txt             # Ex.: chardet, pandas, pyarrow, langid, markdown-it-py, python-slugify
└── README.md                    # Instruções rápidas de uso e exemplos de CLI
```
