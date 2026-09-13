# [H] ALPINE-CVE-2019-19911

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-19911
Ecosystem: Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-01-05
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-19911
Type: osv

## Affected
- Alpine:v3.12: `py3-pillow` — affected >=0 <6.2.2-r0
- Alpine:v3.13: `py3-pillow` — affected >=0 <6.2.2-r0
- Alpine:v3.14: `py3-pillow` — affected >=0 <6.2.2-r0
- Alpine:v3.15: `py3-pillow` — affected >=0 <6.2.2-r0

## Details
There is a DoS vulnerability in Pillow before 6.2.2 caused by FpxImagePlugin.py calling the range function on an unvalidated 32-bit integer if the number of bands is large. On Windows running 32-bit Python, this results in an OverflowError or MemoryError due to the 2 GB limit. However, on Linux running 64-bit Python this results in the process being terminated by the OOM killer.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-19911
