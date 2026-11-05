from io import BytesIO
from pathlib import Path
import os
import shutil
import tempfile
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk


class AdvancedMP3EditorApp:

  def __init__(self, root):
    self.root = root
    self.root.title("Mp3MetaEdit - Advanced ID3v1 & v2 Editor")
    self.root.geometry("1400x850")
    self.root.resizable(True, True)

    self.current_file_path: Path | None = None
    self.current_image = None
    self.current_image_bytes = None

    # Tag configuration mapping for ID3v2 frames
    self.tag_mapping = [
        ("Title", "TIT2"),
        ("Artist", "TPE1"),
        ("Album", "TALB"),
        ("Album Artist", "TPE2"),
        ("Composer", "TCOM"),
        ("Genre", "TCON"),
        ("Year", "TYER"),
        ("Track", "TRCK"),
        ("Disc", "TPOS"),
        ("BPM", "TBPM"),
        ("Comment", "COMM"),
        ("Copyright", "TCOP"),
        ("Encoded By", "TENC"),
        ("Software", "TSSE"),
    ]

    self.create_widgets()

  def create_widgets(self):
    # Main Layout
    main_frame = ttk.Frame(self.root, padding=20)
    main_frame.pack(fill="both", expand=True)

    # File Selection
    file_frame = ttk.Frame(main_frame)
    file_frame.pack(fill="x", pady=(0, 15))

    self.file_entry = ttk.Entry(file_frame, width=80)
    self.file_entry.pack(side="left", padx=(0, 10), fill="x", expand=True)

    browse_btn = ttk.Button(
        file_frame, text="Browse MP3...", command=self.browse_file
    )
    browse_btn.pack(side="left")

    # Content Split
    content_frame = ttk.Frame(main_frame)
    content_frame.pack(fill="both", expand=True, pady=10)

    # Left: Metadata Form with Scrolling
    form_outer = ttk.LabelFrame(content_frame, text=" Metadata Editor ", padding=5)
    form_outer.pack(side="left", fill="both", expand=True, padx=(0, 15))

    canvas = tk.Canvas(form_outer, borderwidth=0, highlightthickness=0)
    scrollbar_v = ttk.Scrollbar(form_outer, orient="vertical", command=canvas.yview)
    self.scrollable_form = ttk.Frame(canvas, padding=10)

    self.scrollable_form.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=self.scrollable_form, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar_v.set)
    
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar_v.pack(side="right", fill="y")

    self.entries = {}
    for i, (lbl_text, tag_id) in enumerate(self.tag_mapping):
      ttk.Label(self.scrollable_form, text=f"{lbl_text}:").grid(
          row=i, column=0, sticky="e", pady=8
      )
      ent = ttk.Entry(self.scrollable_form, width=100)
      ent.grid(row=i, column=1, sticky="ew", pady=8, padx=10)
      self.scrollable_form.grid_columnconfigure(1, weight=1)
      self.entries[tag_id] = ent

    # Info Text Area
    self.info_box = tk.Text(
        self.scrollable_form, height=6, width=80, wrap="word", bg="#f9f9f9", font=("Arial", 9)
    )
    self.info_box.grid(row=len(self.tag_mapping), column=0, columnspan=2, pady=15, sticky="nsew")

    # Right: Cover Art Display Frame
    art_frame = ttk.LabelFrame(
        content_frame, text=" Embedded Cover Art ", padding=10
    )
    art_frame.pack(side="right", fill="both", padx=(5, 0))

    self.art_label = ttk.Label(
        art_frame,
        text="No Cover Art\nFound",
        anchor="center",
        justify="center",
        width=22,
    )
    self.art_label.pack(fill="both", expand=True, padx=10, pady=10)

    # NEW: Button to change/load new album art
    change_art_btn = ttk.Button(
        art_frame, text="Change Art...", command=self.change_cover_art
    )
    change_art_btn.pack(fill="x", pady=(5, 0))

    # Save Buttons at the bottom
    button_frame = ttk.Frame(main_frame)
    button_frame.pack(pady=10)

    save_v2_btn = ttk.Button(
        button_frame, text="Save ID3v2 (Extended)", command=self.trigger_save_v2
    )
    save_v2_btn.pack(side="left", padx=10)

    save_v1_btn = ttk.Button(
        button_frame, text="Save ID3v1 (Legacy)", command=self.trigger_save_v1
    )
    save_v1_btn.pack(side="left", padx=10)

  def parse_id3v1(self, path: Path):
    """Reads 128-byte ID3v1 tag from the end of the file."""
    metadata = {}
    try:
      with open(path, "rb") as f:
        f.seek(0, os.SEEK_END)
        size = f.tell()
        if size < 128: return metadata
        f.seek(-128, os.SEEK_END)
        tag = f.read(128)
        if tag[:3] == b"TAG":
          metadata["found"] = True
          metadata["TIT2"] = tag[3:33].decode("latin-1", "ignore").strip("\x00 ")
          metadata["TPE1"] = tag[33:63].decode("latin-1", "ignore").strip("\x00 ")
          metadata["TALB"] = tag[63:93].decode("latin-1", "ignore").strip("\x00 ")
          metadata["TYER"] = tag[93:97].decode("latin-1", "ignore").strip("\x00 ")
          metadata["COMM"] = tag[97:127].decode("latin-1", "ignore").strip("\x00 ")
    except Exception: pass
    return metadata

  def parse_mp3_file(self, path: Path):
    """Generalized parser for text frames and APIC."""
    metadata = {}
    image_bytes = None

    with open(path, "rb") as f:
      header = f.read(10)
      if header[:3] == b"ID3":
        ver_major = header[3]
        ver_minor = header[4]
        metadata["v2_version"] = f"2.{ver_major}.{ver_minor}"

        tag_size = 0
        for i in range(6, 10):
          tag_size = (tag_size << 7) | (header[i] & 0x7F)
        metadata["v2_size"] = tag_size

        tag_data = f.read(tag_size)
        offset = 0
        while offset < len(tag_data) - 10:
          frame_id_bytes = tag_data[offset : offset + 4]
          frame_id = frame_id_bytes.decode(errors="ignore")
          if frame_id_bytes == b"\x00\x00\x00\x00" or not frame_id.isalnum():
            break

          frame_size = int.from_bytes(tag_data[offset + 4 : offset + 8], "big")
          if frame_size <= 0 or offset + 10 + frame_size > len(tag_data):
            break

          frame_content = tag_data[offset + 10 : offset + 10 + frame_size]

          if frame_id.startswith("T") or frame_id == "COMM":
            try:
              encoding = frame_content[0]
              start_idx = 4 if frame_id == "COMM" else 1
              raw_text = frame_content[start_idx:]
              
              decodings = {0: "latin-1", 1: "utf-16", 2: "utf-16", 3: "utf-8"}
              text_val = raw_text.decode(decodings.get(encoding, "latin-1"), errors="ignore")
              metadata[frame_id] = text_val.strip("\x00 \ufeff")
            except: pass
          elif frame_id == "APIC":
            try:
              jpeg_idx = frame_content.find(b"\xff\xd8")
              png_idx = frame_content.find(b"\x89PNG\r\n\x1a\n")
              start_idx = jpeg_idx if jpeg_idx != -1 else png_idx
              if start_idx != -1:
                image_bytes = frame_content[start_idx:]
            except: pass

          offset += 10 + frame_size

    return metadata, image_bytes

  def change_cover_art(self):
    """Opens a file dialog to select a new image, caches its bytes, and updates the UI preview."""
    if not self.current_file_path:
      messagebox.showwarning("Warning", "Please load an MP3 file first!")
      return

    img_path = filedialog.askopenfilename(
        title="Select Cover Art Image",
        filetypes=[
            ("Image Files", "*.jpg *.jpeg *.png"),
            ("All Files", "*.*"),
        ],
    )
    if not img_path:
      return

    try:
      # Read the new image file as raw binary bytes
      with open(img_path, "rb") as img_file:
        new_img_bytes = img_file.read()

      # Validate that Pillow can open it successfully before caching
      Image.open(BytesIO(new_img_bytes))

      # Cache the new bytes and update the UI thumbnail
      self.current_image_bytes = new_img_bytes
      self.display_cover_art(new_img_bytes)
      
      messagebox.showinfo(
          "Success", "Cover art staged! Click 'Save Tags' to write it to the file."
      )

    except Exception as e:
      messagebox.showerror("Error", f"Invalid or unreadable image file: {e}")
  
  
  def browse_file(self):
    file_path = filedialog.askopenfilename(
        title="Select MP3 File", filetypes=[("MP3 Files", "*.mp3")]
    )
    if not file_path:
      return

    self.current_file_path = Path(file_path)
    self.file_entry.delete(0, tk.END)
    self.file_entry.insert(0, str(self.current_file_path))

    try:
      v2_data, img_bytes = self.parse_mp3_file(self.current_file_path)
      v1_data = self.parse_id3v1(self.current_file_path)
      self.current_image_bytes = img_bytes

      for _, tag_id in self.tag_mapping:
        self.entries[tag_id].delete(0, tk.END)
        val = v2_data.get(tag_id) or v1_data.get(tag_id) or ""
        self.entries[tag_id].insert(0, val)

      self.info_box.delete("1.0", tk.END)
      v2_info = f"ID3v2: {v2_data.get('v2_version', 'Not found')}"
      if v2_data.get('v2_size'): v2_info += f" ({v2_data['v2_size']} bytes)"
      
      v1_info = "ID3v1: Found" if v1_data.get("found") else "ID3v1: Not found"
      self.info_box.insert(tk.END, f"{v2_info}\n{v1_info}\n")

      if img_bytes:
        self.display_cover_art(img_bytes)
      else:
        self.art_label.config(image="", text="No Cover Art\nFound")
        self.current_image = None

    except Exception as e:
      messagebox.showerror("Error", f"Failed to parse MP3: {e}")

  def display_cover_art(self, img_bytes: bytes):
    try:
      img = Image.open(BytesIO(img_bytes))
      img.thumbnail((350, 350))
      self.current_image = ImageTk.PhotoImage(img)
      self.art_label.config(image=self.current_image, text="")
    except Exception as e:
      self.art_label.config(image="", text=f"Could not load art:\n{e}")

  def save_id3v2_and_audio(self, filepath: Path):
    """Atomic Temp-File Rewrite preserving audio sync."""
    filepath = Path(filepath)
    audio_data_offset = 10
    original_audio_bytes = b""

    with open(filepath, "rb") as f:
      header = f.read(10)
      if header[:3] == b"ID3":
        tag_size = 0
        for i in range(6, 10):
          tag_size = (tag_size << 7) | (header[i] & 0x7F)
        audio_data_offset = 10 + tag_size
      
      f.seek(audio_data_offset)
      original_audio_bytes = f.read()

    original_audio_bytes = original_audio_bytes.lstrip(b'\x00')

    new_frames = bytearray()
    def create_text_frame(frame_id: bytes, text: str):
      if not text: return b""
      encoded_text = text.encode("utf-16")
      content = b"\x01" + encoded_text
      return frame_id + len(content).to_bytes(4, "big") + b"\x00\x00" + content

    for tag_id, entry in self.entries.items():
        val = entry.get()
        if val:
            new_frames.extend(create_text_frame(tag_id.encode(), val))

    if self.current_image_bytes:
      mime_type = b"image/jpeg" if self.current_image_bytes[:2] == b"\xff\xd8" else b"image/png"
      apic_content = b"\x01" + mime_type + b"\x00\x03\x00" + self.current_image_bytes
      apic_frame = b"APIC" + len(apic_content).to_bytes(4, "big") + b"\x00\x00" + apic_content
      new_frames.extend(apic_frame)

    new_tag_size = len(new_frames)
    synchsafe_size = bytearray([
        (new_tag_size >> 21) & 0x7F,
        (new_tag_size >> 14) & 0x7F,
        (new_tag_size >> 7) & 0x7F,
        new_tag_size & 0x7F
    ])
    new_header = bytearray(b"ID3\x03\x00\x00") + synchsafe_size

    dir_name = filepath.parent
    temp_fd, temp_path = tempfile.mkstemp(dir=dir_name, suffix=".tmp")
    try:
      with os.fdopen(temp_fd, "wb") as temp_file:
        temp_file.write(new_header)
        temp_file.write(new_frames)
        temp_file.write(original_audio_bytes)
      os.replace(temp_path, filepath)
    except Exception as e:
      if os.path.exists(temp_path): os.remove(temp_path)
      raise e

  def save_id3v1(self, filepath: Path):
    """Writes or appends the 128-byte ID3v1 block."""
    tag = bytearray(b"TAG")
    def encode_v1(key, length):
        return self.entries[key].get().encode("latin-1", "ignore")[:length].ljust(length, b"\x00")
    
    tag += encode_v1("TIT2", 30)
    tag += encode_v1("TPE1", 30)
    tag += encode_v1("TALB", 30)
    tag += encode_v1("TYER", 4)
    tag += encode_v1("COMM", 30)
    tag += b"\x00" # Genre

    with open(filepath, "r+b") as f:
      f.seek(0, os.SEEK_END)
      size = f.tell()
      if size >= 128:
        f.seek(-128, os.SEEK_END)
        if f.read(3) == b"TAG":
          f.seek(-128, os.SEEK_END)
        else:
          f.seek(0, os.SEEK_END)
      f.write(tag)

  def trigger_save_v2(self):
    if not self.current_file_path:
      messagebox.showwarning("Warning", "Please load an MP3 file first!")
      return
    try:
      self.save_id3v2_and_audio(self.current_file_path)
      messagebox.showinfo("Success", "ID3v2 tags updated successfully!")
      self.browse_file()
    except Exception as e:
      messagebox.showerror("Error", f"Failed to rewrite MP3 tags: {e}")

  def trigger_save_v1(self):
    if not self.current_file_path:
      messagebox.showwarning("Warning", "Please load an MP3 file first!")
      return
    try:
      self.save_id3v1(self.current_file_path)
      messagebox.showinfo("Success", "ID3v1 (Legacy) tags updated!")
      self.browse_file()
    except Exception as e:
      messagebox.showerror("Error", f"Failed to save ID3v1: {e}")


if __name__ == "__main__":
  root = tk.Tk()
  app = AdvancedMP3EditorApp(root)
  root.mainloop()