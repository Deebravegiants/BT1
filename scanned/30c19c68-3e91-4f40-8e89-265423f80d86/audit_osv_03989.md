# [M] ALPINE-CVE-2026-9669

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-9669
Ecosystem: Alpine:v3.24
CVSS: 6.0 (CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-06-08
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-9669
Type: osv

## Affected
- Alpine:v3.24: `python3` — affected >=0 <3.14.7-r0

## Details
bz2.BZ2Decompressor objects could be reused after a decompression error. If an application caught the resulting OSError and retried with the same decompressor, crafted input could cause the decompressor to resume from an invalid internal state and perform out-of-bounds writes to a stack buffer. This could crash the process when processing untrusted data.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-9669
