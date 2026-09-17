# [C] ALPINE-CVE-2023-28879

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2023-28879
Ecosystem: Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-03-31
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-28879
Type: osv

## Affected
- Alpine:v3.14: `ghostscript` — affected >=0 <9.54.0-r2
- Alpine:v3.15: `ghostscript` — affected >=0 <9.55.0-r1
- Alpine:v3.16: `ghostscript` — affected >=0 <9.56.1-r1
- Alpine:v3.17: `ghostscript` — affected >=0 <10.0.0-r1

## Details
In Artifex Ghostscript through 10.01.0, there is a buffer overflow leading to potential corruption of data internal to the PostScript interpreter, in base/sbcp.c. This affects BCPEncode, BCPDecode, TBCPEncode, and TBCPDecode. If the write buffer is filled to one byte less than full, and one then tries to write an escaped character, two bytes are written.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-28879
