# [C] Use-after-free in lzma.LZMADecompressor, bz2.BZ2Decompressor, and gzip.GzipFile after re-use under memory pressure

## Summary
Severity: Critical
Advisory: BIT-libpython-2026-6100
Aliases: BIT-python-2026-6100, BIT-python-min-2026-6100, CVE-2026-6100, PSF-0000-CVE-2026-6100, PSF-2026-18
Ecosystem: Bitnami
Published: 2026-07-06
Source: https://osv.dev/vulnerability/BIT-libpython-2026-6100
Type: osv

## Affected
- Bitnami: `libpython` — affected >=3.14.0 <3.14.5

## Details
Use-after-free (UAF) was possible in the `lzma.LZMADecompressor`, `bz2.BZ2Decompressor`, and `gzip.GzipFile` when a memory allocation fails with a `MemoryError` and the decompression instance is re-used. This scenario can be triggered if the process is under memory pressure. The fix cleans up the dangling pointer in this specific error condition.

The vulnerability is only present if the program re-uses decompressor instances across multiple decompression calls even after a `MemoryError` is raised during decompression. Using the helper functions to one-shot decompress data such as `lzma.decompress()`, `bz2.decompress()`, `gzip.decompress()`, and `zlib.decompress()` are not affected as a new decompressor instance is used per call. If the decompressor instance is not re-used after an error condition, this usage is similarly not vulnerable.

## References
- http://www.openwall.com/lists/oss-security/2026/04/13/10
- https://access.redhat.com/errata/RHSA-2026:10117
- https://access.redhat.com/errata/RHSA-2026:10140
- https://access.redhat.com/errata/RHSA-2026:10141
- https://access.redhat.com/errata/RHSA-2026:10711
- https://access.redhat.com/errata/RHSA-2026:10745
- https://access.redhat.com/errata/RHSA-2026:10774
- https://access.redhat.com/errata/RHSA-2026:10949
- https://access.redhat.com/errata/RHSA-2026:10950
- https://access.redhat.com/errata/RHSA-2026:11062
- https://access.redhat.com/errata/RHSA-2026:11077
- https://access.redhat.com/errata/RHSA-2026:11768
- https://access.redhat.com/errata/RHSA-2026:13692
- https://access.redhat.com/errata/RHSA-2026:13812
- https://access.redhat.com/errata/RHSA-2026:14652
- https://access.redhat.com/errata/RHSA-2026:14653
- https://access.redhat.com/errata/RHSA-2026:14656
- https://access.redhat.com/errata/RHSA-2026:16699
- https://access.redhat.com/errata/RHSA-2026:17525
- https://access.redhat.com/errata/RHSA-2026:17619
