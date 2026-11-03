from dataclasses import dataclass
from pathlib import Path


@dataclass
class MP3MetadataInfo:
  file_name: str
  file_size: int
  has_id3v1: bool
  title: str | None = None
  artist: str | None = None
  album: str | None = None
  year: str | None = None
  comment: str | None = None
  genre_id: int | None = None


import struct
from pathlib import Path
def parse_mp3_id3v2(file_path: str | Path) -> dict:
    path = Path(file_path)
    with open(path, 'rb') as f:
        header = f.read(10)

        if header[:3] != b'ID3':
            raise ValueError("Not an ID3v2 tag or not an MP3 file")

        version_major = header[3] >> 4
        version_minor = header[3] & 0x0F

        size = 0
        for i in range(4, 8):
            size = (size << 7) | (header[i] & 0x7F)

        return {
            'version_major': version_major,
            'version_minor': version_minor,
            'header_size': size + 10
        }

def read_id3v1_tags(file_path: str | Path) -> dict | None:
    path = Path(file_path)
    with open(path, 'rb') as f:
        f.seek(-128, 2)
        tag = f.read(128)

        if tag[:3] == b'TAG':
            title = tag[3:33].decode('latin1').strip()
            artist = tag[33:63].decode('latin1').strip()
            album = tag[63:93].decode('latin1').strip()
            year = tag[93:97].decode('latin1').strip()
            comment = tag[97:127].decode('latin1').strip()
            genre = tag[127]

            return {
                'title': title,
                'artist': artist,
                'album': album,
                'year': year,
                'comment': comment,
                'genre': genre
            }
        else:
            return None

def parse_mp3_id3v1(filepath: str | Path) -> MP3MetadataInfo:
    path = Path(filepath)
    file_size = path.stat().st_size

    if file_size < 128:
        raise ValueError("File is too small to contain an ID3v1 tag.")

    id3v1_tags = read_id3v1_tags(path)
    return MP3MetadataInfo(
          file_name=path.name,
          file_size=file_size,
        has_id3v1=id3v1_tags is not None,
        title=id3v1_tags['title'] if id3v1_tags else None,
        artist=id3v1_tags['artist'] if id3v1_tags else None,
        album=id3v1_tags['album'] if id3v1_tags else None,
        year=id3v1_tags['year'] if id3v1_tags else None,
        comment=id3v1_tags['comment'] if id3v1_tags else None,
        genre_id=id3v1_tags['genre'] if id3v1_tags else None,
      )

# Existing code remains unchanged


if __name__ == "__main__":
  # Change this to the path of one of your tagged MP3 files
  test_file = "/home/emmz/Documents/python projects/Mp3MetaEdit/rengades.mp3"

  try:
    info = parse_mp3_id3v1(test_file)
    print("Successfully read MP3 file:")
    for key, value in info.__dict__.items():
      print(f"  {key}: {value}")
  except FileNotFoundError:
    print(
        f"'{test_file}' not found. Place a tagged .mp3 file in this folder and update 'test_file'!"
    )
