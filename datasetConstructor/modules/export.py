from pathlib import Path
from typing import Iterable, List, Dict, Any
import json
import logging

import pandas as pd


class Exporter:
    def __init__(self) -> None:
        self.logger = logging.getLogger("export")

    def export(
        self,
        records: Iterable,
        output_dir: Path,
        basename: str,
        formats: List[str],
    ) -> Path:
        rows: List[Dict[str, Any]] = [r.to_dict() for r in records]
        df = pd.DataFrame(rows)
        main_path = None

        for fmt in set(f.lower() for f in formats):
            if fmt == "jsonl":
                path = output_dir / f"{basename}.jsonl"
                with path.open("w", encoding="utf-8") as f:
                    for row in rows:
                        f.write(json.dumps(row, ensure_ascii=False) + "\n")
                main_path = main_path or path
            elif fmt == "csv":
                path = output_dir / f"{basename}.csv"
                df.to_csv(path, index=False)
                main_path = main_path or path
            elif fmt == "parquet":
                path = output_dir / f"{basename}.parquet"
                df.to_parquet(path, index=False)
                main_path = main_path or path
            else:
                self.logger.warning("Formato não suportado: %s", fmt)

        if main_path is None:
            raise ValueError("Nenhum formato válido informado.")
        return main_path
