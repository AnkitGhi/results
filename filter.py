# python filter.py ./ExpertAnnotations.txt filtered_annotations.txt

import sys
from pathlib import Path

def filter_lines(src: Path, dst: Path) -> None:
    with src.open("r", encoding="utf-8") as fin, dst.open("w", encoding="utf-8") as fout:
        for line in fin:
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 2:
                fout.write(line)
                continue

            first  = parts[0].strip()
            second = parts[1].split("#", 1)[0].strip()

            if first != second:        # keep only non‑matching rows
                fout.write(line)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <input.txt> <output.txt>")
        sys.exit(1)

    in_file  = Path(sys.argv[1])
    out_file = Path(sys.argv[2])
    filter_lines(in_file, out_file)
    print(f"Filtered file written to {out_file}")
