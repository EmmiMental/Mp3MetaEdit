# Mp3MetaEdit

A lightweight, robust Python/Tkinter desktop utility designed for low-level binary MP3 metadata inspection, ID3v2 frame parsing, embedded cover art extraction, and safe file reconstruction.

Built from the ground up to master raw byte-stream manipulation and file structure integrity without relying on heavy external wrapper libraries for its core parsing engine.

---

## 🚀 Key Features

* **Dual-Version Support:** Directly reads and decodes both **ID3v1 (Legacy)** and **ID3v2 (Extended)** metadata formats.
* **Expanded Metadata Fields:** Supports a wide range of standard ID3 tags including Title, Artist, Album, Album Artist, Composer, Genre, Year, Track, Disc, BPM, Comment, Copyright, and more.
* **Scrollable Metadata Editor:** Features a larger, scrollable UI to accommodate many metadata fields without cluttering the interface.
* **Atomic Temp-File Rewrite:** Avoids dangerous in-place file corruption by constructing a clean output file from scratch—re-encoding headers and framing before performing an atomic OS-level file replacement (`os.replace`).
* **Embedded Cover Art (`APIC`) Handling:** Automatically scans for embedded JPEG/PNG image payloads within `APIC` frames, extracts them on the fly, and caches them to preserve album art during metadata updates. can change the embedded image and save it with the new image
* **UTF-16 Text Framing:** Safely encodes text frames using UTF-16 for broad compatibility across different operating systems and media players.
* **Audio Stream Synchronization:** Cleans leading null padding bytes during reconstruction to maintain pristine MPEG frame alignment, ensuring compatibility with professional audio tools like **Mixxx**.

---

## 🛠️ Tech Stack

* **Language:** Python 3.x  
* **GUI Framework:** `tkinter` (`ttk` themed widgets)  
* **Image Processing:** `Pillow` (PIL) for rendering embedded cover art thumbnails  
* **System Libraries:** `pathlib`, `os`, `tempfile`, `shutil`, `io`

---

## 📦 Installation & Usage

### 1. Install Python
If you don't have Python installed, download and install the latest version from [python.org](https://www.python.org/). Make sure to check the box that says **"Add Python to PATH"** during installation.

### 2. Set Up the Project
Open your terminal (or Command Prompt) in the project folder and follow these steps to create an isolated environment:

**On Windows:**
```sh
# Create a virtual environment
python -m venv venv

# Activate it
venv\Scripts\activate

# Install dependencies
pip install Pillow
```

**On macOS/Linux:**
```sh
# Create a virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies
pip install Pillow
```

### 3. Run the Application
With the virtual environment active, start the editor:

```sh
python Mp3MetaEdit.py
```

Click **Browse MP3...** to load a file. Inspect the ID3 version status and artwork, edit the expanded metadata fields, and use the **Save ID3v2** or **Save ID3v1** buttons to update the file.

---

## 🗺️ Roadmap & Future Features

- [x] **Expanded Metadata Fields:** Support for Genre, Track Number, BPM, and many more.
- [ ] **Dynamic Cover Art Swapping:** Enable loading and injecting new images into the `APIC` frame.
- [ ] **Batch Processing:** Expand the application to handle multi-file directory scans and bulk tag updates.
- [ ] **UI Modernization:** Implement a sleek custom theme or dark mode for a more polished desktop aesthetic.

---

## 📝 Disclosures

This project was developed with the assistance of AI tools including **Gemin** in the browser, **Qwen2.5-coder** (local), **Deepseek-r1** (local), and **Gemin 3 / 3.1 Flash** (API). These tools were used to plan and provide insights during the development process. While the final code and documentation are presented here, the contributions of these AI tools are acknowledged.