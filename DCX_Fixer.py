import sys
from pathlib import Path

ASSERTED_BYTES = {
    0x17: b'LDCS\0',
    0x24: b'DCP\0',
    0x33: b'\x00', # unk33
    0x40: b'\x00\x01\x01\x00',
    0x44: b'DCA\0'
}

def read(f, offset, length):
    f.seek(offset)
    return f.read(length)

def write(f, offset, value):
    f.seek(offset)
    f.write(value)

def ensure_bytes(file_stream, byte_map: dict) -> bool:
    """Takes a file stream and ensures byte structures at offsets specified in byte_map. Returns True if any actions were taken"""
    changed: bool = False
    for offset, value in byte_map.items():
        existing_value = read(file_stream, offset, len(value))
        if existing_value == value:
            print(f"{value} found at offset {offset}, skipping.")
            continue

        print(f"Patching {value} at offset {offset}.")
        write(file_stream, offset, value)
        changed = True
    return changed

def patch_file(file_path: Path) -> None:
    if not file_path.is_file():
        print(f"Error: '{file_path}' does not exist or is not a file.")
        return

    try:
        with open(file_path, "r+b") as f:
            if read(f, 0x0, 3) != b'DCX':
                print("File is not a DCX, skipping.")
                return
            
            _type = read(f, 0x28, 4).decode("utf-8")
            endian = 'big' if bool.from_bytes(read(f, 0x09, 1)) else 'little'
            compression = ord(read(f, 0x30, 1))
            
            print(f"\n\nAttempting to patch file:\nPath: {file_path}\nDCX Type: {_type}\nCompression Level: {compression}\nEndianness: {endian}\n")

            if ensure_bytes(f, ASSERTED_BYTES):
                f.flush()
                print("\nFile fixed!")

            else:
                print("\nFile was already valid, no actions taken!")

    except PermissionError:
        print(f"Error: Permission denied. Could not access '{file_path}'.")
    except Exception as e:
        print(f"Error processing '{file_path}': {e}")

def main():
    if len(sys.argv) < 2:
        if getattr(sys, "frozen", False):
            print(f"Usage: .\\{Path(sys.argv[0]).name} <file_path(s)>")
        else:
            print(f"Usage: python {Path(sys.argv[0]).name} <file_path(s)>")
        sys.exit(1)

    for arg in sys.argv[1:]:
        file_path = Path(arg)
        patch_file(file_path)

if __name__ == "__main__":
    main()

# python -m PyInstaller DCX_Fixer.py --onefile --noconsole