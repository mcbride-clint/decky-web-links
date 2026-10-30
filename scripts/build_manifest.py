import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.resolve()
PRESETS_DIR = REPO_ROOT / "presets"
DIST_DIR = REPO_ROOT / "dist"
MANIFEST_FILE = DIST_DIR / "manifest.json"

REQUIRED_FIELDS = ["id", "title", "category", "url", "recommended_browser", "launch_flags"]

def build_manifest():
    if not PRESETS_DIR.exists():
        print("Error: Presets directory not found")
        return

    presets = []
    errors = 0

    print("Scanning presets directory...")
    for preset_file in sorted(PRESETS_DIR.glob("*/preset.json")):
        try:
            with open(preset_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            missing = [field for field in REQUIRED_FIELDS if field not in data]
            if missing:
                print(f"Missing required fields: {missing}")
                errors += 1
                continue

            art_dir = preset_file.parent / "art"
            artwork_data = {}
            art_types = ["cover", "grid", "hero", "logo", "icon"]
            
            if art_dir.exists():
                for art_type in art_types:
                    for ext in [".png", ".jpg", ".jpeg"]:
                        candidate = art_dir / f"{art_type}{ext}"
                        if candidate.exists():
                            rel_path = candidate.relative_to(REPO_ROOT).as_posix()
                            artwork_data[art_type] = rel_path
                            break

            data["artwork"] = artwork_data
            presets.append(data)

        except Exception as e:
            print(f"Failed to parse {preset_file}: {e}")
            errors += 1

    DIST_DIR.mkdir(parents=True, exist_ok=True)

    manifest = {
        "version": "1.0.0",
        "total_presets": len(presets),
        "presets": presets
    }

    with open(MANIFEST_FILE, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print(f"Successfully compiled {len(presets)} preset(s)")

if __name__ == "__main__":
    build_manifest()
