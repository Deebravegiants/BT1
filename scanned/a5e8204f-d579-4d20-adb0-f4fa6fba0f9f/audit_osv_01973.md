# [H] ALPINE-CVE-2020-35653

## Summary
Severity: High
Advisory: ALPINE-CVE-2020-35653
Ecosystem: Alpine:v3.14, Alpine:v3.15
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:H)
Published: 2021-01-12
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-35653
Type: osv

## Affected
- Alpine:v3.14: `py3-pillow` — affected >=0 <8.1.0-r0
- Alpine:v3.15: `py3-pillow` — affected >=0 <8.1.0-r0

## Details
In Pillow before 8.1.0, PcxDecode has a buffer over-read when decoding a crafted PCX file because the user-supplied stride value is trusted for buffer calculations.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-35653
