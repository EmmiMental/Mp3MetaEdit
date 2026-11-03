from io import BytesIO
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk


class AdvancedMP3EditorApp:

  def __init__(self, root):
    self.root = root
    self.root.title("Advanced MP3 Tag & Cover Art Inspector")
    self.root.geometry("600x550")
    self.root.resizable(False, False)

    self.current_file_path: Path | None = None
    self.current_image = None  # Reference to prevent garbage collection

    self.create_widgets()

  def create_widgets(self):
    # Main Layout
    main_frame = ttk.Frame(self.root, padding=15)
    main_frame.pack(fill="both", expand=True)

    # File Selection
    file_frame = ttk.Frame(main_frame)
    file_frame.pack(fill="x", pady=(0, 10))

    self.file_entry = ttk.Entry(file_frame, width=50)
    self.file_entry.pack(side="left", padx=(0, 5))

    browse_btn = ttk.Button(
        file_frame, text="Browse MP3...", command=self.browse_file
    )
    browse_btn.pack(side="left")

    # Content Split: Left side = Metadata, Right side = Cover Art
    content_frame = ttk.Frame(main_frame)
    content_frame.pack(fill="both", expand=True, pady=5)

    # Left: Metadata Form
    form_frame = ttk.LabelFrame(
        content_frame, text=" ID3v2 / ID3v1 Metadata ", padding=10
    )
    form_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

    fields = [
        ("Title:", "title"),
        ("Artist:", "artist"),
        ("Album:", "album"),
        ("Year:", "year"),
    ]

    self.entries = {}
    for i, (lbl_text, key) in enumerate(fields):
      ttk.Label(form_frame, text=lbl_text).grid(
          row=i, column=0, sticky="e", pady=5
      )
      ent = ttk.Entry(form_frame, width=25)
      ent.grid(row=i, column=1, sticky="w", pady=5, padx=5)
      self.entries[key] = ent

    # Info Text Area for tags / version info
    self.info_box = tk.Text(
        form_frame, height=8, width=28, wrap="word", bg="#f9f9f9"
    )
    self.info_box.grid(row=4, column=0, columnspan=2, pady=10, sticky="nsew")

    # Right: Cover Art Display
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
      metadata, img_bytes = self.parse_mp3_file(self.current_file_path)

      # Populate text fields
      for key in ["title", "artist", "album", "year"]:
        self.entries[key].delete(0, tk.END)
        self.entries[key].insert(0, metadata.get(key, ""))

      # Populate info box
      self.info_box.delete("1.0", tk.END)
      self.info_box.insert(
          tk.END,
          f"ID3v2 Ver: {metadata.get('v2_version', 'None')}\nTag Size:"
          f" {metadata.get('v2_size', 0)} bytes\n",
      )

      # Render cover art if present
      if img_bytes:
        self.display_cover_art(img_bytes)
      else:
        self.art_label.config(image="", text="No Cover Art\nFound")
        self.current_image = None

    except Exception as e:
      messagebox.showerror("Error", f"Failed to parse MP3: {e}")

  def parse_mp3_file(self, path: Path):
    """Parses ID3v2 header, extracts text frames and APIC image bytes."""
    metadata = {}
    image_bytes = None

    with open(path, "rb") as f:
      # Read ID3v2 Header (10 bytes)
      header = f.read(10)
      if header[:3] == b"ID3":
        ver_major = header[3]
        ver_minor = header[4]
        metadata["v2_version"] = f"2.{ver_major}.{ver_minor}"

        # Calculate synchsafe integer for size
        tag_size = 0
        for i in range(6, 10):
          tag_size = (tag_size << 7) | (header[i] & 0x7F)
        metadata["v2_size"] = tag_size

        # Read the entire ID3v2 tag chunk payload
        tag_data = f.read(tag_size)

        offset = 0
        while offset < len(tag_data) - 10:
          frame_id = tag_data[offset : offset + 4]
          if frame_id == b"\x00\x00\x00\x00" or not frame_id.isalnum():
            break  # Hit padding or invalid frame

          # Get frame size (big-endian)
          frame_size = int.from_bytes(tag_data[offset + 4 : offset + 8], "big")
          if frame_size <= 0 or offset + 10 + frame_size > len(tag_data):
            break

          frame_content = tag_data[offset + 10 : offset + 10 + frame_size]

          # Extract Text Frames
          if frame_id in [b"TIT2", b"TPE1", b"TALB", b"TYER", b"TDRC"]:
            try:
              encoding = frame_content[0]
              raw_text_bytes = frame_content[1:]

              # Determine codec based on ID3 encoding spec byte
              if encoding == 0:
                text_val = raw_text_bytes.decode("latin-1", errors="ignore")
              elif encoding in [1, 2]:
                text_val = raw_text_bytes.decode("utf-16", errors="ignore")
              elif encoding == 3:
                text_val = raw_text_bytes.decode("utf-8", errors="ignore")
              else:
                text_val = raw_text_bytes.decode("latin-1", errors="ignore")

              text_val = text_val.strip("\x00 \ufeff")

              if frame_id == b"TIT2":
                metadata["title"] = text_val
              elif frame_id == b"TPE1":
                metadata["artist"] = text_val
              elif frame_id == b"TALB":
                metadata["album"] = text_val
              elif frame_id in [b"TYER", b"TDRC"]:
                metadata["year"] = text_val[:4]
            except Exception:
              pass

          # Extract Attached Picture (APIC)
          elif frame_id == b"APIC":
            try:
              jpeg_idx = frame_content.find(b"\xff\xd8")
              png_idx = frame_content.find(b"\x89PNG\r\n\x1a\n")

              start_idx = -1
              if jpeg_idx != -1:
                start_idx = jpeg_idx
              elif png_idx != -1:
                start_idx = png_idx

              if start_idx != -1:
                image_bytes = frame_content[start_idx:]
            except Exception:
              pass

          offset += 10 + frame_size

    return metadata, image_bytes

  def display_cover_art(self, img_bytes: bytes):
    try:
      img = Image.open(BytesIO(img_bytes))
      img.thumbnail((160, 160))

      self.current_image = ImageTk.PhotoImage(img)
      self.art_label.config(image=self.current_image, text="")
    except Exception as e:
      self.art_label.config(image="", text=f"Could not load art:\n{e}")


if __name__ == "__main__":
  root = tk.Tk()
  app = AdvancedMP3EditorApp(root)
  root.mainloop()