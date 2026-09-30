# [C] ALPINE-CVE-2020-15900

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2020-15900
Ecosystem: Alpine:v3.11, Alpine:v3.12
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-07-28
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-15900
Type: osv

## Affected
- Alpine:v3.11: `ghostscript` — affected >=0 <9.50-r1
- Alpine:v3.12: `ghostscript` — affected >=0 <9.52-r1

## Details
A memory corruption issue was found in Artifex Ghostscript 9.50 and 9.52. Use of a non-standard PostScript operator can allow overriding of file access controls. The 'rsearch' calculation for the 'post' size resulted in a size that was too large, and could underflow to max uint32_t. This was fixed in commit 5d499272b95a6b890a1397e11d20937de000d31b.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-15900
