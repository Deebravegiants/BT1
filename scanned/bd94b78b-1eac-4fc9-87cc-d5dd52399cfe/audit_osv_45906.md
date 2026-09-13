# [M] JLSEC-2026-462

## Summary
Severity: Medium
Advisory: JLSEC-2026-462
Ecosystem: Julia
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-05-07
Source: https://osv.dev/vulnerability/JLSEC-2026-462
Type: osv

## Affected
- Julia: `XZ_jll` — affected >=0 <5.8.3+0

## Details
XZ Utils provide a general-purpose data-compression library plus command-line tools. Prior to version 5.8.3, if `lzma_index_decoder()` was used to decode an Index that contained no Records, the resulting `lzma_index` was left in a state where where a subsequent `lzma_index_append()` would allocate too little memory, and a buffer overflow would occur. This issue has been patched in version 5.8.3.

## References
- http://www.openwall.com/lists/oss-security/2026/03/31/13
- https://github.com/tukaani-project/xz/commit/c8c22869e780ff57c96b46939c3d79ff99395f87
- https://github.com/tukaani-project/xz/releases/tag/v5.8.3
- https://github.com/tukaani-project/xz/security/advisories/GHSA-x872-m794-cxhv
