# File Organizer

A simple Python script that organizes files in a folder (e.g. your Downloads folder) into subfolders based on file type: Images, Documents, Videos, Audio, Archives, Code, Installers, and Others.

It has a dry-run mode that shows exactly what a real run would do, including renamed files and removed folders, so you can check before anything is touched.

## Requirements

- Python 3.8+
- No external dependencies. It uses only the standard library (`argparse`, `pathlib`, `shutil`).

## Usage

```bash
python FileOrgnizer.py [-p PATH] [-r] [-t] [-m]
```

> **Careful:** if you don't pass `-p`, the script organizes your real `~/Downloads` folder. Run it with `-t` first.

### Options

| Flag | Long form        | Description                                                                                  | Default              |
|------|------------------|----------------------------------------------------------------------------------------------|----------------------|
| `-p` | `--path`         | Folder to organize                                                                           | `~/Downloads`        |
| `-r` | `--recursive`    | Also organize files inside sub-folders, not just the top level                               | Off (top-level only) |
| `-t` | `--test`         | Dry run. Prints what would happen without changing anything                                  | Off                  |
| `-m` | `--remove-empty` | After moving, remove the sub-folders the script emptied. Requires `-r`                       | Off                  |

### Examples

Organize your Downloads folder (top-level files only):
```bash
python FileOrgnizer.py
```

Organize a specific folder, including its subfolders:
```bash
python FileOrgnizer.py -p ~/Desktop/Test -r
```

Organize a folder, including subfolders, and remove the subfolders that end up empty:
```bash
python FileOrgnizer.py -p ~/Desktop/Test -r -m
```

Preview what a run would do, without changing anything:
```bash
python FileOrgnizer.py -p ~/Downloads -r -m -t
```

### Sample output

Given this folder:

```
test/
├── x/
│   ├── y/
│   │   └── photo.jpg
│   └── z/
│       ├── song.mp3
│       └── .hidden
└── w/
    └── doc.pdf
```

`python FileOrgnizer.py -p test -r -m -t` prints:

```
Would move test/x/y/photo.jpg to test/Images/photo.jpg
Would move test/x/z/song.mp3 to test/Audio/song.mp3
Would move test/w/doc.pdf to test/Documents/doc.pdf
Would remove test/x/y
Would keep test/x/z (not empty)
Would keep test/x (not empty)
Would remove test/w
Total: would remove 2 empty folders
```

`x/z` is kept because it still contains the hidden file `.hidden`, and `x` is kept because `x/z` is still inside it. Folders at the same depth may be listed in a different order.

Running the same command without `-t` removes the same folders and reports the same total. The real run also prints one error line for each folder it could not remove, because the operating system refuses to delete a folder that is not empty:

```
[Errno 39] Directory not empty: 'test/x/z'
[Errno 39] Directory not empty: 'test/x'
Total: removed 2 empty folders
```

These lines are expected. They are the "Would keep" cases from the preview, and nothing is deleted or damaged. The exact wording of the error depends on your operating system.

## How it works

The script scans the target folder and sorts files into these categories based on extension:

| Category   | Extensions                                                            |
|------------|-----------------------------------------------------------------------|
| Images     | `.png`, `.jpg`, `.jpeg`, `.gif`, `.bmp`, `.svg`, `.webp`              |
| Documents  | `.pdf`, `.txt`, `.docx`, `.doc`, `.odt`, `.rtf`, `.md`                |
| Videos     | `.mp4`, `.mkv`, `.mov`, `.avi`                                        |
| Audio      | `.mp3`, `.wav`, `.flac`, `.aac`, `.m4a`                               |
| Archives   | `.zip`, `.tar`, `.gz`, `.rar`, `.7z`, `.bz2`, `.xz`                   |
| Code       | `.py`, `.cpp`, `.c`, `.java`, `.js`, `.html`, `.css`, `.json`         |
| Installers | `.exe`, `.msi`, `.apk`, `.dmg`                                        |
| Others     | anything not listed above                                             |

By default, only files directly inside the target folder are organized. Use `-r` to also walk into subfolders.

### Name collisions

If a file with the same name already exists in the destination folder, the script adds a counter instead of overwriting it (e.g. `photo_1.jpg`, `photo_2.jpg`). Double extensions are handled correctly: `archive.tar.gz` becomes `archive_1.tar.gz`, not `archive.tar_1.gz`. This works for `.tar.gz`, `.tar.bz2` and `.tar.xz`.

The dry run (`-t`) shows the same names the real run will use, even when several files with the same name are going to the same folder.

### Removing empty folders (`-m`)

With `-r -m`, the script removes sub-folders that it emptied by moving their files out, and then their parent folders if those are empty as well. A few rules keep this safe:

- It only removes **empty** folders. Files are never deleted.
- It only considers folders it actually took files from. Folders that were already empty before the run are left alone.
- A folder that still contains anything (for example a hidden file) is kept, and so are its parents. In a real run, the script tries to remove such a folder, the operating system refuses, and the script prints a "Directory not empty" message and continues. This is expected and harmless. The dry run shows these folders as "Would keep" instead.
- The target folder itself and the category folders are never removed.
- With `-t`, it prints which folders would be removed or kept, using the same rules as the real run.
- `-m` has no effect without `-r`, and the script prints a warning.

### Hidden files

The script skips any file or folder whose name starts with a dot (for example `.DS_Store`, `.gitignore` or everything inside `.git/`), so projects and system files are left untouched.

**Platform note:** this works for hidden files on Linux and macOS only. On Windows, hidden files are marked by a file attribute rather than a leading dot, so files like `desktop.ini` are **not** detected and may be moved. Files that start with a dot are still skipped on Windows. Always run with `-t` first on Windows.

### Other things the script skips

- Files already inside one of the category folders (so you can safely re-run the script on an already-organized folder).
- The script itself, if it is located inside the target folder.

## Notes

- Use `-t` first, especially the first time you use the script on a folder you care about.
- If a file can't be moved or a folder can't be removed (for example because of permissions), the script prints a message and carries on with the rest.

## Limitations

- Tested on Linux only.
- Windows hidden-file attributes are not handled.
- Categories are based on the file extension only, not on the file's content.
