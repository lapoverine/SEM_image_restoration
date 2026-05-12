import cv2
import argparse
import sys
from pathlib import Path


def process_folder(input_folder, output_folder, patch_size=256):
    input_path = Path(input_folder)
    output_path = Path(output_folder)
    
    if not input_path.exists():
        print(f"Ошибка: Входная папка не существует: {input_folder}")
        return False
    
    supported_formats = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif')
    
    image_files = []
    for ext in supported_formats:
        image_files.extend(input_path.rglob(f"*{ext}"))
        image_files.extend(input_path.rglob(f"*{ext.upper()}"))
    
    if not image_files:
        print(f"Не найдено изображений в папке: {input_folder}")
        return False
    
    print(f"Найдено {len(image_files)} изображений")
    print(f"Входная папка: {input_folder}")
    print(f"Выходная папка: {output_folder}")
    print(f"Размер патча: {patch_size}x{patch_size}")
    
    success_count = 0
    for i, img_path in enumerate(image_files, 1):
        rel_path = img_path.relative_to(input_path)
        
        parent_folders = list(rel_path.parent.parts) if rel_path.parent != Path('.') else []
        original_stem = img_path.stem
        
        if parent_folders:
            folders_name = '_'.join(parent_folders)
            new_filename = f"{folders_name}_{original_stem}"
        else:
            new_filename = original_stem
        
        out_subdir = output_path / rel_path.parent
        out_subdir.mkdir(parents=True, exist_ok=True)
        
        original_name = img_path.name
        img_path = img_path
        
        print(f"[{i}/{len(image_files)}] Обработка: {rel_path}")
        print(f"  Новое имя для патчей: {new_filename}")
        
        success = process_image_with_name(img_path, out_subdir, new_filename, patch_size)
        if success:
            success_count += 1
    
    print(f"Обработано: {success_count} из {len(image_files)}")
    return True

def process_image_with_name(img_path, out_dir, base_name, patch_size=256):
    img = cv2.imread(str(img_path))
    if img is None:
        print(f"Не удалось загрузить изображение: {img_path}")
        return False
    
    if len(img.shape) == 3:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    h, w = img.shape
    
    pad_h = (patch_size - h % patch_size) % patch_size
    pad_w = (patch_size - w % patch_size) % patch_size
    img = cv2.copyMakeBorder(img, 0, pad_h, 0, pad_w, cv2.BORDER_REFLECT)
    h, w = img.shape
    
    patch_count = 0
    for y in range(0, h, patch_size):
        for x in range(0, w, patch_size):
            patch = img[y:y+patch_size, x:x+patch_size]
            out_path = out_dir / f"{base_name}_{y}_{x}.png"
            cv2.imwrite(str(out_path), patch)
            patch_count += 1
    
    print(f"  Создано {patch_count} патчей из {img_path.name} -> {base_name}")
    return True

def main():
    parser = argparse.ArgumentParser(description='Нарезка изображений на патчи')
    parser.add_argument('input', help='Путь к входной папке с изображениями')
    parser.add_argument('-o', '--output', help='Путь к выходной папке (по умолчанию: patches)', 
                       default='patches')
    parser.add_argument('-s', '--size', type=int, default=256, 
                       help='Размер патча в пикселях (по умолчанию: 256)')
    
    args = parser.parse_args()
    
    if not Path(args.input).exists():
        print(f"Папка {args.input} не существует")
        sys.exit(1)
    
    process_folder(args.input, args.output, args.size)

if __name__ == "__main__":
    main()