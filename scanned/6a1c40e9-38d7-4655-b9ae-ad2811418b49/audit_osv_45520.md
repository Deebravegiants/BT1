# [M] GNU gzip contains a global buffer overflow vulnerability in the LZH decompression logic caused by...

## Summary
Severity: Medium
Advisory: JLSEC-2026-1265
Ecosystem: Julia
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-08-12
Source: https://osv.dev/vulnerability/JLSEC-2026-1265
Type: osv

## Affected
- Julia: `Gzip_jll` — affected unspecified

## Details
GNU gzip contains a global buffer overflow vulnerability in the LZH decompression logic caused by improper reuse of shared global state between different decompression formats within a single execution. GNU gzip maintains a global array that is shared across the LZ77, LZW, and LZH decompression routines and is not reinitialized between files processed in the same invocation.
By decompressing a specially crafted LZW file followed by a specially crafted LZH file in a single gzip -d command, an attacker can poison the shared global state and subsequently trigger an out‑of‑bounds read in the LZH decoder. The LZH decompression logic follows stale values left in the shared array, causing reads past the end of the allocated global buffer.

This issue has been fixed in the commit 63dbf6b3b9e6e781df1a6a64e609b10e23969681

## References
- https://cert.pl/en/posts/2026/04/CVE-2026-41991
- https://cert.pl/en/posts/2026/04/CVE-2026-41991/
- https://cgit.git.savannah.gnu.org/cgit/gzip.git/commit/?id=63dbf6b3b9e6e781df1a6a64e609b10e23969681
- https://github.com/advisories/GHSA-qxh4-rprf-2mmj
- https://nvd.nist.gov/vuln/detail/CVE-2026-41992
- https://www.gnu.org/software/gzip
- https://www.gnu.org/software/gzip/
