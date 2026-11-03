# MP3 Metadata & Cover Art Inspector

A lightweight, local-first Python utility featuring a graphical user interface (GUI) built with `tkinter` and `Pillow`. Designed to inspect, parse, and edit basic ID3 tags and extract embedded album artwork directly from binary MP3 streams without external system dependencies.

**NOTE:** This project was developed to practice binary file parsing and stream manipulation in Python with the assistance of local AI models.

---

## Features

| Feature | Description |
| :---- | :---- |
| **ID3v2 Parsing** | Reads ID3v2 headers (v2.3/v2.4), computes synchsafe integer tag sizes, and dynamically extracts text frames (`TIT2`, `TPE1`, `TALB`, `TYER`). |
| **Cover Art Extraction** | Scans binary frame payloads for standard JPEG (`\xff\xd8`) and PNG magic bytes to render album art dynamically in the UI. |
| **ID3v1 Support** | Reads and writes classic fixed-width 128-byte ID3v1 tags at the end of the file stream. |
| **Cross-Platform GUI** | Clean, native desktop interface utilizing Tkinter and `ttk` styling. |

---

## Tech Stack

- **Language:** Python 3.x  
- **GUI Framework:** `tkinter`, `ttk`  
- **Image Processing:** `Pillow` (PIL)  
- **Binary Handling:** Built-in `struct`, `io.BytesIO`, and direct binary file streaming (`rb`, `r+b`).

---

## Installation & Setup

1. **Clone the repository:**

```sh
git clone https://github.com/EmmiMental/Mp3MetaEdit.git
cd Mp3MetaEdit
```

2. **Create and activate a virtual environment:**

```sh
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

3. **Install dependencies:**

```sh
pip install Pillow
```

---

## Usage

Run the main application script from your active virtual environment:

```sh
python Mp3MetaEdit.py
```

1. Click **Browse MP3...** to select any local `.mp3` file.  
2. View detected ID3v2 version specs, metadata fields, and embedded cover art.  
3. Modify text fields and save ID3v1 tags directly back to the file stream.

---

## Project Status

Developed as a "clean-room" sandbox project to master binary file stream manipulation (`f.seek`, byte offsets, synchsafe integer bit-shifting) in preparation for legacy file format reverse-engineering.

---

## License

Distributed under the MIT License. See `LICENSE` for more information.