import argparse
from pathlib import Path
import shutil


DOUBLE_EXTENSIONS = (".tar.gz",".tar.bz2",".tar.xz")


def create_file_name(dest_dir , file , reserved):
    counter = 1
    name = file.name
    last_two = "".join(file.suffixes[-2:])

    if last_two.lower() in DOUBLE_EXTENSIONS :
        extension = last_two
        base = file.name[:-len(extension)]
    else:
        extension = file.suffix
        base = file.stem

    while (dest_dir/name).exists() or (dest_dir/name) in reserved:
        name = f"{base}_{counter}{extension}"
        counter += 1
        
    return name



extension_map = {
    ".png": "Images", ".jpg": "Images", ".jpeg": "Images", ".gif": "Images",
    ".bmp": "Images", ".svg": "Images", ".webp": "Images",

    ".pdf": "Documents", ".txt": "Documents", ".docx": "Documents",
    ".doc": "Documents", ".odt": "Documents", ".rtf": "Documents", ".md": "Documents",

    ".mp4": "Videos", ".mkv": "Videos", ".mov": "Videos", ".avi": "Videos",

    ".mp3": "Audio", ".wav": "Audio", ".flac": "Audio", ".aac": "Audio", ".m4a": "Audio",

    ".zip": "Archives", ".tar": "Archives", ".gz": "Archives", ".rar": "Archives", ".7z": "Archives", ".bz2": "Archives", ".xz": "Archives",

    ".py": "Code", ".cpp": "Code", ".c": "Code", ".java": "Code",
    ".js": "Code", ".html": "Code", ".css": "Code", ".json": "Code",

    ".exe": "Installers", ".msi": "Installers", ".apk": "Installers", ".dmg": "Installers",
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p','--path' , type=Path , default= Path.home() / "Downloads" )
    parser.add_argument('-r' , '--recursive' , action='store_true' ,help ='Also organize the files in the sub-folders')
    parser.add_argument('-t' , '--test' ,action='store_true' ,help ='A test so you can see what happens without moving anything')
    parser.add_argument('-m' , '--remove-empty' , action='store_true' ,help = 'Remove the sub-folders left empty after their files were moved, used with -r')
    args = parser.parse_args()

    path = args.path

    folder_names = set(extension_map.values()) | {"Others"}
    if not path.exists():
        print("The path that you entered is not found !")
        return
    elif not path.is_dir():
        print("The path that you entered needs to be a directory !")
        return
    

    file_path = path.rglob("*") if args.recursive else path.iterdir()

    if not args.recursive and args.remove_empty:
        print("the --remove-empty (-m) needs --recursive (-r)")

    parent_folders = set()
    script_path = Path(__file__).resolve()
    reserved_names = set()
    would_be_gone = set()

    for file in list(file_path):
        if file.is_file():
            relative_parts = file.relative_to(path).parts
            if relative_parts[0] in folder_names:
                continue
            elif any(part.startswith(".") for part in relative_parts):
                continue
            elif file.resolve() == script_path:
                continue
            try:
                destination  = extension_map.get(file.suffix.lower() ,"Others")
                new_name = create_file_name(path / destination , file , reserved_names)
                if args.test:
                    print(f"Would move {file} to {path / destination / new_name}")
                    would_be_gone.add(file)
                    reserved_names.add(path / destination / new_name)
                else:
                    (path / destination).mkdir(parents=True , exist_ok = True)    
                    shutil.move(file ,(path / destination / new_name))
                if file.parent != path:
                    parent_folders.add(file.parent)
     
            except PermissionError:
                print(f"You don't have the permission to move {file.name}")
            except OSError as er:
                print(f"Couldn't move {file.name} : {er}")

    if  args.recursive and args.remove_empty :
        folders_to_check = set()
        
        for p in parent_folders:
            current = p
            while  current != path :
                folders_to_check.add(current)
                current = current.parent

        ordered_folders = sorted(folders_to_check ,key =lambda folder: len(folder.parts), reverse=True)
        counter = 0
        
        for folder in ordered_folders:
            try:
                if args.test:
                    if all(item in would_be_gone for item in folder.iterdir()):
                        print(f"Would remove {folder}")
                        would_be_gone.add(folder)
                        counter += 1
                    else:
                        print(f"Would keep {folder} (not empty)")
                else:
                    if any(folder.iterdir()):
                        print(f"Kept {folder} (not empty)")
                    else:
                        folder.rmdir()
                        counter += 1
            except PermissionError:
                print(f"You don't have the permission to remove {folder}")
            except OSError as er:
                print(er)

        folder_message = "folder" if counter == 1 else "folders"
        if args.test :
            print(f"Total: would remove {counter} empty {folder_message}")
        else:
            print(f"Total: removed {counter} empty {folder_message}")
        
        

if __name__ =="__main__":
    main()
