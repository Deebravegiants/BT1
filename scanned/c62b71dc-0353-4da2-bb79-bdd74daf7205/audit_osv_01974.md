# [H] ALPINE-CVE-2020-35654

## Summary
Severity: High
Advisory: ALPINE-CVE-2020-35654
Ecosystem: Alpine:v3.14, Alpine:v3.15
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-01-12
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-35654
Type: osv

## Affected
- Alpine:v3.14: `py3-pillow` — affected >=0 <8.1.0-r0
- Alpine:v3.15: `py3-pillow` — affected >=0 <8.1.0-r0

## Details
In Pillow before 8.1.0, TiffDecode has a heap-based buffer overflow when decoding crafted YCbCr files because of certain interpretation conflicts with LibTIFF in RGBA mode.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-35654
