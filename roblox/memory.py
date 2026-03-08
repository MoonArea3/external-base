import ctypes
import ctypes.wintypes as wintypes
import struct
import sys

PROCESS_ALL_ACCESS = 0x1F0FFF
TH32CS_SNAPMODULE = 0x00000008
TH32CS_SNAPMODULE32 = 0x00000010
INVALID_HANDLE_VALUE = ctypes.c_void_p(-1).value

kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
user32 = ctypes.WinDLL("user32", use_last_error=True)

class MODULEENTRY32(ctypes.Structure):
    _fields_ = [
        ("dwSize", wintypes.DWORD),
        ("th32ModuleID", wintypes.DWORD),
        ("th32ProcessID", wintypes.DWORD),
        ("GlblcntUsage", wintypes.DWORD),
        ("ProccntUsage", wintypes.DWORD),
        ("modBaseAddr", ctypes.POINTER(ctypes.c_byte)),
        ("modBaseSize", wintypes.DWORD),
        ("hModule", wintypes.HMODULE),
        ("szModule", ctypes.c_char * 256),
        ("szExePath", ctypes.c_char * 260),
    ]

class Memory:
    def __init__(self, window_title: str):
        self.handle = None
        self.pid = None

        hwnd = user32.FindWindowW(None, window_title)
        if not hwnd:
            print("the window wasnt found")
            sys.exit(1)

        pid = wintypes.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        self.pid = pid.value

        if not self.pid:
            print("couldnt get pid")
            sys.exit(1)

        self.handle = kernel32.OpenProcess(PROCESS_ALL_ACCESS, False, self.pid)
        if not self.handle:
            print("the procss didnt let me open")
            sys.exit(1)

    def read(self, address: int, size: int) -> bytes:
        buffer = ctypes.create_string_buffer(size)
        bytes_read = ctypes.c_size_t()

        if not kernel32.ReadProcessMemory(
            self.handle,
            ctypes.c_void_p(address),
            buffer,
            size,
            ctypes.byref(bytes_read),
        ):
            
            #print("read failed bc ur noob")
            #sys.exit(1)
            0
        return buffer.raw[:bytes_read.value]

    def write(self, address: int, data: bytes) -> None:
        size = len(data)
        bytes_written = ctypes.c_size_t()

        if not kernel32.WriteProcessMemory(
            self.handle,
            ctypes.c_void_p(address),
            data,
            size,
            ctypes.byref(bytes_written),
        ):
            print("write failed")
            sys.exit(1)

    def read_ptr(self, address: int, offset: int = 0) -> int:
        buffer = self.read(address + offset, 8)
        return int.from_bytes(buffer, 'little', signed=True) if len(buffer) == 8 else 0
    
    def read_float(self, address: int) -> float | None:
        data = self.read(address, 4)
        try:
            return struct.unpack("f", data)[0]
        except: return 0.0
    def write_float(self, address: int, value: float) -> None:
        self.write(address, struct.pack("<f", value))

    def read_floats(self, address: int, amount: int):
        try:
            bulk = self.read(address, 4 * amount)
            floats = []
            for i in range(amount):
                part = bulk[i * 4:(i + 1) * 4]
                if len(part) == 4:
                    floats.append(struct.unpack("<f", part)[0])
                else:
                    floats.append(0.0)
            return floats
        except:
            return [0.0]

    def write_floats(self, address: int, values) -> None:
        packed = b''.join(struct.pack("<f", float(v)) for v in values)
        if packed:
            self.write(address, packed)

    def get_base(self, module_name = "RobloxPlayerBeta.exe") -> int:
        snapshot = kernel32.CreateToolhelp32Snapshot(
            TH32CS_SNAPMODULE | TH32CS_SNAPMODULE32,
            self.pid
        )

        if snapshot == INVALID_HANDLE_VALUE:
            print("snapshot failed")
            return 0

        module = MODULEENTRY32()
        module.dwSize = ctypes.sizeof(MODULEENTRY32)

        if not kernel32.Module32First(snapshot, ctypes.byref(module)):
            kernel32.CloseHandle(snapshot)
            print("Module32First failed")
            return 0

        while True:
            name = module.szModule.decode()

            if module_name is None or name.lower() == module_name.lower():
                base_addr = ctypes.addressof(module.modBaseAddr.contents)
                kernel32.CloseHandle(snapshot)
                return base_addr

            if not kernel32.Module32Next(snapshot, ctypes.byref(module)):
                break

        kernel32.CloseHandle(snapshot)
        return 0

    def read_string(self, address: int) -> str:
        if not address:
            return ""

        length = self.read_ptr(address + 0x18)
        if not length or length <= 0 or length > 1000:
            return ""

        if length >= 16:
            address = self.read_ptr(address)
            if not address:
                return ""

        raw = self.read(address, length)
        return raw.split(b"\x00", 1)[0].decode(errors="ignore")
    
    
    def write_int(self, address: int, value: int, size: int = 4):
        self.write(address, value.to_bytes(size, "little"))
        
    def write_string(self, address: int, value: str) -> bool:
        if not address:
            return False

        if value is None:
            value = ""
        value = value.replace("\x00", "")
        data = value.encode() + b"\x00"
        length = len(data) - 1  

        if length <= 0 or length > 1000:
            return False

        self.write_int(address + 0x18, length)

        if length >= 16:
            ptr = self.read_ptr(address)
            if not ptr:
                return False
            self.write(ptr, data)
        else:
            self.write(address, data)

        return True

    def close(self):
        if self.handle:
            kernel32.CloseHandle(self.handle)