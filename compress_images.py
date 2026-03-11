"""
Compress all JPG/PNG images in the current directory.
Resizes images larger than 1920px wide and saves at quality 75.
Skips images already under 300KB.
"""
import os
import sys
# Force UTF-8 output to avoid encoding errors on Windows
sys.stdout.reconfigure(encoding='utf-8')
from PIL import Image

MAX_WIDTH = 1920
QUALITY = 75
SKIP_BELOW_KB = 300

folder = os.path.dirname(os.path.abspath(__file__))
extensions = ('.jpg', '.jpeg', '.png')

total_before = 0
total_after = 0
count = 0

for filename in os.listdir(folder):
    if not filename.lower().endswith(extensions):
        continue
    filepath = os.path.join(folder, filename)
    size_kb = os.path.getsize(filepath) / 1024
    total_before += size_kb

    if size_kb < SKIP_BELOW_KB:
        total_after += size_kb
        print(f"  SKIP  {filename} ({size_kb:.0f} KB) - already small")
        continue

    try:
        with Image.open(filepath) as img:
            # Convert RGBA/P to RGB for JPEG saving
            if img.mode in ('RGBA', 'P', 'LA'):
                img = img.convert('RGB')

            # Resize if wider than MAX_WIDTH
            if img.width > MAX_WIDTH:
                ratio = MAX_WIDTH / img.width
                new_size = (MAX_WIDTH, int(img.height * ratio))
                img = img.resize(new_size, Image.LANCZOS)

            # For PNG files, save as JPEG instead (much smaller)
            if filename.lower().endswith('.png'):
                new_filepath = filepath[:-4] + '.jpg'
                img.save(new_filepath, quality=QUALITY, optimize=True)
                # Remove original PNG
                os.remove(filepath)
                new_size_kb = os.path.getsize(new_filepath) / 1024
                total_after += new_size_kb
                saved = size_kb - new_size_kb
                print(f"  PNG->JPG {filename}: {size_kb:.0f} KB -> {new_size_kb:.0f} KB (saved {saved:.0f} KB)")
            else:
                img.save(filepath, quality=QUALITY, optimize=True)
                new_size_kb = os.path.getsize(filepath) / 1024
                total_after += new_size_kb
                saved = size_kb - new_size_kb
                print(f"  OK    {filename}: {size_kb:.0f} KB -> {new_size_kb:.0f} KB (saved {saved:.0f} KB)")
            count += 1
    except Exception as e:
        total_after += size_kb
        print(f"  ERROR {filename}: {e}")

print(f"\nDone. Compressed {count} images.")
print(f"Total before: {total_before/1024:.1f} MB")
print(f"Total after:  {total_after/1024:.1f} MB")
print(f"Space saved:  {(total_before-total_after)/1024:.1f} MB")
