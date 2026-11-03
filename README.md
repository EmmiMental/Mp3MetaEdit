Mp3MetaEdit

A lightweight, local-first Python utility featuring a graphical user interface (GUI) built with tkinter and Pillow. Designed to inspect, parse, and edit basic ID3 tags and extract embedded album artwork directly from binary MP3 streams without external system dependencies.

This is a project to practice python and figure out file parsing, I had the help of some local AI models for planning and debugging. I will continue to add features for now, I hope someone get’s some use out of it, however unlikely that may be ;)


Features
ID3v2 Header & Frame Parsing: Reads ID3v2 headers (v2.3/v2.4), computes synchsafe integer tag sizes, and dynamically extracts metadata frames (TIT2 for Title, TPE1 for Artist, TALB for Album, and TYER/TDRC for Year).
Embedded Cover Art Extraction (APIC): Scans binary frame payloads for standard JPEG (\xff\xd8) and PNG magic bytes, slicing out the raw image data to render album art dynamically in the UI.
ID3v1 Fallback & Editing: Reads and writes classic fixed-width 128-byte ID3v1 tags at the end of the file stream.
Cross-Platform GUI: Clean, native-feeling desktop interface utilizing Tkinter and ttk styling.


Tech Stack
Language: Python 3.x
GUI: tkinter, ttk
Image Processing: Pillow (PIL)
Binary Handling: Built-in struct, io.BytesIO, and direct binary file streaming (rb, r+b).


Installation & Setup
Clone the repository:

git clone https://github.com/EmmiMental/Mp3MetaEdit.git
cd Mp3MetaEdit

Create and activate a virtual environment:

python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

Install dependencies:

pip install Pillow


Usage
Run the main application script from your active virtual environment:

python Mp3MetaEdit.py

Click Browse MP3... to select any local .mp3 file.
View detected ID3v2 version specs, metadata fields, and embedded cover art.
Modify text fields and save ID3v1 tags directly back to the file stream.


Project Status
Developed as a "clean-room" sandbox project to master binary file stream manipulation (f.seek, byte offsets, synchsafe integer bit-shifting) in preparation for legacy file format reverse-engineering.
