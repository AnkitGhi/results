
from __future__ import annotations
import json
from pathlib import Path

PAIRS_TXT   = "./filtered_annotations.txt"
TOKENS_TXT  = "/Users/ankitghimire/Downloads/Flickr8k_text/Flickr8k.token.txt"
OUTPUT_JSON = "output_with_captions.json"

# Optional base directories for absolute paths
# REF_DIR  = "drive/MyDrive/flickr"        # <base>_references.jpg
# PRED_DIR = "drive/MyDrive/flickr_pred"   # <caption>_predictions.jpg

def load_caption_map(token_path: str) -> dict[str, str]:
    mapping: dict[str, str] = {}
    with open(token_path, encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            cap_id, caption = line.rstrip("\n").split("\t", maxsplit=1)
            mapping[cap_id] = caption
    return mapping


def load_pairs(in_path: str, caption_map: dict[str, str]) -> list[dict]:
    records: list[dict] = []
    skipped_ids: list[str] = []
    missing_ids: list[str] = []

    def caption_or_placeholder(cid: str) -> str:
        if cid in caption_map:
            return caption_map[cid]
        missing_ids.append(cid)
        return "no_caption_id"

    with open(in_path, encoding="utf-8") as f:
        for ln, raw in enumerate(f, start=1):
            parts = raw.rstrip("\n").split("\t")

            # Expect exactly 5 columns: base, caption_id, r1, r2, r3
            if len(parts) < 5 or not parts[1].strip():
                skipped_ids.append(parts[0].strip())
                continue

            base_img, caption_id = parts[0].strip(), parts[1].strip()
            ratings = list(map(int, parts[2:5]))
            avg_rating = sum(ratings) / len(ratings)
            
            base_stem = base_img.split(".jpg")[0]
            caption_stem = caption_id.split(".jpg")[0]
            reference_id = f"{base_img}#0"

            records.append(
                {
                    "base_image": base_img,
                    "caption_id": caption_id,
                    "prediction_caption_image": f"{caption_stem}_predictions.jpg",
                    "reference_caption_image": f"{base_stem}_references.jpg",
                    "prediction_caption": caption_or_placeholder(caption_id),
                    "reference_caption_id": caption_or_placeholder(reference_id),
                    "set_of_ratings": ratings,
                    "average_rating": avg_rating,
                }
            )
            if ln <= 3:
                print(f"[line {ln}] {base_img}  →  ratings={ratings}  avg={avg_rating:.2f}")

    if skipped_ids:
        print("\n[skipped rows with blank caption‑id]")
        for img in skipped_ids:
            print(f"  • {img}")
    if missing_ids:
        print("\n[caption‑ids not found in token file]")
        for cid in sorted(set(missing_ids)):
            print(f"  • {cid}")

    return records

def main():
    caption_map = load_caption_map(TOKENS_TXT)
    records     = load_pairs(PAIRS_TXT, caption_map)

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)

    size = Path(OUTPUT_JSON).stat().st_size
    print(f"\n Wrote {OUTPUT_JSON} — {len(records)} records, {size:,} bytes")

if __name__ == "__main__":
    main()
