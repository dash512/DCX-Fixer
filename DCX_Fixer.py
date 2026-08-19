import sys
from pathlib import Path

ASSERTED_BYTES = {
    # Constant Header Field (what is it?)
    0x08: b'\x00\x00\x00\x18',

    # Offset to DCP? (see 0x24)
    0x0C: b'\x00\x00\x00\x24',

    # Magic
    0x18: b'DCS\0', # always seems to begin with L?
    0x24: b'DCP\0',

    # DCP Header Size
    0x2C: b'\x00\x00\x00\x20', 

    # Padding ?
    0x31: b'\x00\x00\x00', # 0x31 - 0x33, individually asserted
    0x34: b'\x00\x00\x00\x00', # -> 0x37
    #<unk38>
    0x39: b'\x00\x00\x00', # 0x39 - 0x3B, individually asserted
    0x3C: b'\x00\x00\x00\x00', # -> 0x3f

    # Flags?
    0x40: b'\x00\x01\x01\x00',

    # Magic
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
    print(f"{'Offset':<10} | {'Value':<20} | {'Status':<10}\n", "-"*65)

    changed: bool = False
    for offset, value in byte_map.items():
        status = "Okay"

        existing_value = read(file_stream, offset, len(value))

        if existing_value != value:
            write(file_stream, offset, value)
            changed = True
            status = f"Patched -> {value}"

        print(f"{offset:#010x} | {existing_value!s:<20} | {status!s:<10}")
        
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
        input()
    except Exception as e:
        print(f"Error processing '{file_path}': {e}")
        input()

def main():
    if len(sys.argv) < 2:
        if getattr(sys, "frozen", False):
            print(f"Usage: .\\{Path(sys.argv[0]).name} <file_path(s)>")
            input()
        else:
            print(f"Usage: python {Path(sys.argv[0]).name} <file_path(s)>")
            input()
        sys.exit(1)

    for arg in sys.argv[1:]:
        file_path = Path(arg)
        patch_file(file_path)

if __name__ == "__main__":
    main()
    input()

# python -m PyInstaller DCX_Fixer.py --onefile