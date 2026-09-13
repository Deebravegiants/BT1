# [M] Reading malicious EXR files can cause out-of-bounds writes

## Summary
Severity: Medium
Advisory: JLSEC-2026-806
Ecosystem: Julia
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-07-29
Source: https://osv.dev/vulnerability/JLSEC-2026-806
Type: osv

## Affected
- Julia: `OpenEXR_jll` — affected >=3.4.4+0 <3.4.12+0

## Details
OpenEXR provides the specification and reference implementation of the EXR file format, an image storage format for the motion picture industry. Versions 3.4.0 through 3.4.9 have a signed integer overflow vulnerability in OpenEXR's HTJ2K (High-Throughput JPEG 2000) decompression path. The `ht_undo_impl()` function in `src/lib/OpenEXRCore/internal_ht.cpp` accumulates a bytes-per-line value (`bpl`) using a 32-bit signed integer with no overflow guard. A crafted EXR file with 16,385 FLOAT channels at the HTJ2K maximum width of 32,767 causes `bpl` to overflow `INT_MAX`, producing undefined behavior confirmed by UBSan. On an
allocator-permissive host where the required ~64 GB allocation succeeds, the wrapped negative `bpl` value would subsequently be used as a per-scanline pointer advance, which would produce a heap out-of-bounds write. On a memory-constrained host, the allocation fails before `ht_undo_impl()` is entered. This is the second distinct integer overflow in `ht_undo_impl()`. CVE-2026-34545 addressed a different overflow in the same function — the `int16_t p` pixel-loop counter at line ~302 that overflows when iterating over channels whose `width` exceeds 32,767. The CVE-2026-34545 fix did not touch the `int bpl` accumulator at line 211, which is the subject of this advisory. The `bpl` accumulator was also not addressed by any of the 8 advisories in the 2026-04-05 v3.4.9 release batch. This finding is structurally identical to CVE-2026-34588 (PIZ `wcount*nx` overflow in `internal_piz.c`) and should be remediated with the same pattern. The CVE-2026-34588 fix did not touch `internal_ht.cpp`. Version 3.4.10 contains a remediation that addresses the vulnerability in `internal_ht.cpp`.

## References
- https://github.com/AcademySoftwareFoundation/openexr/releases/tag/v3.4.10
- https://github.com/AcademySoftwareFoundation/openexr/security/advisories/GHSA-r3mr-mx8q-jcw5
