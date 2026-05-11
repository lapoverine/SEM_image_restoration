import cv2
import numpy as np
from pathlib import Path

def augment_image(img):
    results = {}
    results["orig"] = img
    results["rot90"] = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
    results["rot180"] = cv2.rotate(img, cv2.ROTATE_180)
    results["rot270"] = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
    results["flip"] = cv2.flip(img, 1)
    return results

input_dir = Path("path/to/your/source/folder")
output_dir = Path("path/to/save/results")

if not input_dir.exists():
    print(f"Папка не найдена: {input_dir}")
    exit()

output_dir.mkdir(exist_ok=True)

extensions = (".png", ".tif", ".tiff", ".jpg", ".jpeg")
images = [p for p in input_dir.rglob("*") if p.suffix.lower() in extensions]

print(f"Найдено изображений: {len(images)}")

total_saved = 0

for i, img_path in enumerate(images, 1):
    img = cv2.imread(str(img_path))
    if img is None:
        print(f"Не удалось прочитать: {img_path.name}")
        continue
    
    if len(img.shape) == 3:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    rel_path = img_path.relative_to(input_dir)
    name = img_path.stem
    
    augs = augment_image(img)
    
    for aug_name, aug_img in augs.items():
        out_path = output_dir / rel_path.parent / f"{name}_{aug_name}.png"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(str(out_path), aug_img)
        total_saved += 1
    
    if i % 50 == 0:
        print(f"Обработано {i}/{len(images)}")

print(f"  Исходных изображений: {len(images)}")
print(f"  Создано файлов: {total_saved}")
print(f"  Результат в: {output_dir}")