import argparse
import logging
import sys
from pathlib import Path
from typing import List, Optional

from modules.config import Settings, load_settings
from modules.ingest import Ingestor
from modules.parse_md import MarkdownParser
from modules.normalize import Normalizer
from modules.chunker import Chunker
from modules.metadata import MetadataEnricher
from modules.export import Exporter


# Base do projeto (resolve sempre a partir deste arquivo)
PROJECT_ROOT = Path(__file__).resolve().parent


def resolve_path(path: Path) -> Path:
    """Converte caminhos relativos em absolutos, baseando-se no diretório do projeto."""
    return path if path.is_absolute() else PROJECT_ROOT / path


def configure_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )


def run_pipeline(
    inputs: List[Path],
    settings: Settings,
    output_dir: Path,
    processed_dir: Path,
) -> Path:
    ingestor = Ingestor(preferred_encodings=settings.ingestion.preferred_encodings)
    parser = MarkdownParser()
    normalizer = Normalizer(
        remove_headers_footers=settings.normalize.remove_headers_footers,
        deduplicate=settings.normalize.deduplicate,
        collapse_whitespace=settings.normalize.collapse_whitespace,
        strip_metadata=settings.normalize.strip_metadata,
    )
    chunker = Chunker(
        target_tokens=settings.chunking.target_tokens,
        hard_max_tokens=settings.chunking.hard_max_tokens,
        overlap_tokens=settings.chunking.overlap_tokens,
        split_on_headings=settings.chunking.split_on_headings,
    )
    enricher = MetadataEnricher(default_tags=settings.metadata.default_tags)
    exporter = Exporter()

    records = []
    for p in inputs:
        p = resolve_path(p)
        if p.is_dir():
            files = sorted(p.rglob("*.md"))
        else:
            files = [p]
        for file in files:
            doc = ingestor.read(file)
            parsed = parser.parse(doc)
            normalized = normalizer.apply(parsed)
            chunks = chunker.split(normalized)
            enriched = [enricher.enrich(c, source_path=file) for c in chunks]
            records.extend(enriched)

    processed_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    dataset = exporter.export(
        records=records,
        output_dir=output_dir,
        basename="dataset",
        formats=settings.export.formats,
    )
    return dataset


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Conversor Markdown → Dataset para LLMs")
    parser.add_argument("-i", "--input", nargs="+", required=True, help="Arquivos ou diretórios de entrada (.md)")
    parser.add_argument("-c", "--config", type=Path, default=Path("config/settings.yaml"), help="Arquivo YAML de configuração")
    parser.add_argument("-o", "--output-dir", type=Path, default=Path("data/output"), help="Diretório de saída dos datasets")
    parser.add_argument("-p", "--processed-dir", type=Path, default=Path("data/processed"), help="Diretório para artefatos intermediários")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"], help="Nível de log")
    return parser.parse_args(argv)


def collect_inputs(items: List[str]) -> List[Path]:
    result: List[Path] = []
    for item in items:
        p = resolve_path(Path(item))
        if p.is_dir():
            result.extend(sorted(p.rglob("*.md")))
        elif p.is_file() and p.suffix.lower() == ".md":
            result.append(p)
    return result


if __name__ == "__main__":
    args = parse_args()
    configure_logging(args.log_level)
    try:
        settings = load_settings(resolve_path(args.config))
        inputs = collect_inputs(args.input)
        if not inputs:
            logging.error("Nenhum arquivo .md encontrado.")
            sys.exit(2)
        output = run_pipeline(
            inputs=inputs,
            settings=settings,
            output_dir=resolve_path(args.output_dir),
            processed_dir=resolve_path(args.processed_dir),
        )
        logging.info(f"Dataset gerado em: {output}")
    except Exception as exc:
        logging.exception("Falha na execução: %s", exc)
        sys.exit(1)
