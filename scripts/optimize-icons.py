"""
Resize + compress everything in public/icon/ into public/icon-web/
(the folder the site actually loads images from), mirroring the
same category subfolders and filenames.

Run this after adding or replacing any file in public/icon/:

    python scripts/optimize-icons.py

Requires: pip install pillow
"""
import os
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "public", "icon")
DST = os.path.join(ROOT, "public", "icon-web")
MAX_SIDE = 320  # px - plenty for how small these render in-game

def main():
    total_before = total_after = count = 0
    bad = []

    for root, dirs, files in os.walk(SRC):
        for f in files:
            if not f.lower().endswith(".png"):
                continue
            src_path = os.path.join(root, f)
            rel = os.path.relpath(src_path, SRC)
            dst_path = os.path.join(DST, rel)
            os.makedirs(os.path.dirname(dst_path), exist_ok=True)

            try:
                im = Image.open(src_path).convert("RGBA")
                w, h = im.size
                scale = MAX_SIDE / max(w, h)
                if scale < 1:
                    im = im.resize((round(w * scale), round(h * scale)), Image.LANCZOS)
                im.save(dst_path, "PNG", optimize=True)
            except Exception as e:
                bad.append((rel, str(e)))
                continue

            b, a = os.path.getsize(src_path), os.path.getsize(dst_path)
            total_before += b
            total_after += a
            count += 1
            print(f"{rel}: {b/1024:.0f}KB -> {a/1024:.0f}KB")

    print(f"\n{count} files OK")
    print(f"Total before: {total_before/1024/1024:.2f}MB")
    print(f"Total after:  {total_after/1024/1024:.2f}MB")
    if bad:
        print(f"\n{len(bad)} FAILED (corrupted/truncated source file) - regenerate these:")
        for rel, e in bad:
            print(f"  {rel}: {e}")

if __name__ == "__main__":
    main()
