# [H] ALPINE-CVE-2026-41992

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-41992
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-06-29
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-41992
Type: osv

## Affected
- Alpine:v3.21: `gzip` — affected >=0 <1.13-r1
- Alpine:v3.22: `gzip` — affected >=0 <1.14-r2
- Alpine:v3.23: `gzip` — affected >=0 <1.14-r3
- Alpine:v3.24: `gzip` — affected >=0 <1.14-r3

## Details
GNU gzip contains a global buffer overflow vulnerability in the LZH decompression logic caused by improper reuse of shared global state between different decompression formats within a single execution. GNU gzip maintains a global array that is shared across the LZ77, LZW, and LZH decompression routines and is not reinitialized between files processed in the same invocation.
By decompressing a specially crafted LZW file followed by a specially crafted LZH file in a single gzip -d command, an attacker can poison the shared global state and subsequently trigger an out‑of‑bounds read in the LZH decoder. The LZH decompression logic follows stale values left in the shared array, causing reads past the end of the allocated global buffer.

This issue has been fixed in commits 63dbf6b3b9e6e781df1a6a64e609b10e23969681 and e7378c2d421be6a286922374425680bbe9ad8b7d.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-41992
