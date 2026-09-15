# [M] ALPINE-CVE-2020-35655

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2020-35655
Ecosystem: Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:L)
Published: 2021-01-12
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-35655
Type: osv

## Affected
- Alpine:v3.12: `py3-pillow` — affected >=0 <7.1.2-r1
- Alpine:v3.13: `py3-pillow` — affected >=0 <7.2.0-r1
- Alpine:v3.14: `py3-pillow` — affected >=0 <8.1.0-r0
- Alpine:v3.15: `py3-pillow` — affected >=0 <8.1.0-r0

## Details
In Pillow before 8.1.0, SGIRleDecode has a 4-byte buffer over-read when decoding crafted SGI RLE image files because offsets and length tables are mishandled.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-35655
