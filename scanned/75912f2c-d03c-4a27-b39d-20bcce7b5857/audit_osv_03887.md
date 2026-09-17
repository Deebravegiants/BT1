# [H] ALPINE-CVE-2026-6100

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-6100
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23
CVSS: 7.5 (CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-04-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-6100
Type: osv

## Affected
- Alpine:v3.21: `python3` — affected >=0 <3.12.14-r0
- Alpine:v3.22: `python3` — affected >=0 <3.12.14-r0
- Alpine:v3.23: `python3` — affected >=0 <3.12.14-r0

## Details
Use-after-free (UAF) was possible in the `lzma.LZMADecompressor`, `bz2.BZ2Decompressor`, and `gzip.GzipFile` when a memory allocation fails with a `MemoryError` and the decompression instance is re-used. This scenario can be triggered if the process is under memory pressure. The fix cleans up the dangling pointer in this specific error condition.

The vulnerability is only present if the program re-uses decompressor instances across multiple decompression calls even after a `MemoryError` is raised during decompression. Using the helper functions to one-shot decompress data such as `lzma.decompress()`, `bz2.decompress()`, `gzip.decompress()`, and `zlib.decompress()` are not affected as a new decompressor instance is used per call. If the decompressor instance is not re-used after an error condition, this usage is similarly not vulnerable.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-6100
