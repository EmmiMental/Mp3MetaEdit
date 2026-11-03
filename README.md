# Mp3MetaEdit

A lightweight, robust Python/Tkinter desktop utility designed for low-level binary MP3 metadata inspection, ID3v2 frame parsing, embedded cover art extraction, and safe file reconstruction.

Built from the ground up to master raw byte-stream manipulation and file structure integrity without relying on heavy external wrapper libraries for its core parsing engine.

---

## 🚀 Key Features

* **Low-Level Binary ID3v2 Parsing:** Directly reads and decodes binary ID3v2 headers, calculating bit-shifted **synchsafe integers** to determine exact tag sizes and frame offsets.  
* **Atomic Temp-File Rewrite (Method 1):** Avoids dangerous in-place file corruption by constructing a clean output file from scratch—re-encoding headers and framing before performing an atomic OS-level file replacement (`os.replace`).  
* **Embedded Cover Art (`APIC`) Handling:** Automatically scans for embedded JPEG/PNG image payloads within `APIC` frames, extracts them on the fly, and caches them to preserve album art during metadata updates.  
* **UTF-8 & Multi-Encoding Text Framing:** Safely decodes and encodes text frames (`TIT2` Title, `TPE1` Artist, `TALB` Album, `TYER`/`TDRC` Year) supporting Latin-1, UTF-16, and UTF-8 formats.  
* **Audio Stream Synchronization:** Cleans leading null padding bytes during reconstruction to maintain pristine MPEG frame alignment, ensuring compatibility with professional audio tools like **Mixxx**.

---

## 🛠️ Tech Stack

* **Language:** Python 3.x  
* **GUI Framework:** `tkinter` (`ttk` themed widgets)  
* **Image Processing:** `Pillow` (PIL) for rendering embedded cover art thumbnails  
* **System Libraries:** `pathlib`, `os`, `tempfile`, `shutil`, `io`

---

## 📦 Installation & Usage

1. Ensure you have Python 3 and Pillow installed:

```sh
pip install Pillow
```

2. Clone or download the repository, then run the script:

```sh
python mp3_meta_edit.py
```

3. Click **Browse MP3...** to load a file, inspect its ID3v2 version and embedded artwork, edit the text fields, and click **Save Tags** to execute an atomic binary rewrite.

---

## 🗺️ Roadmap & Future Features

- [ ] **Expanded Metadata Fields:** Add support for Genre, Track Number, and custom user frames.  
- [ ] **Dynamic Cover Art Swapping:** Enable loading and injecting new images into the `APIC` frame.  
- [ ] **Batch Processing:** Expand the application to handle multi-file directory scans and bulk tag updates.  
- [ ] **UI Modernization:** Implement a sleek custom theme or dark mode for a more polished desktop aesthetic.