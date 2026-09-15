# [C] ALPINE-CVE-2021-25289

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2021-25289
Ecosystem: Alpine:v3.14, Alpine:v3.15
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-03-19
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-25289
Type: osv

## Affected
- Alpine:v3.14: `py3-pillow` — affected >=0 <8.1.2-r0
- Alpine:v3.15: `py3-pillow` — affected >=0 <8.1.2-r0

## Details
An issue was discovered in Pillow before 8.1.1. TiffDecode has a heap-based buffer overflow when decoding crafted YCbCr files because of certain interpretation conflicts with LibTIFF in RGBA mode. NOTE: this issue exists because of an incomplete fix for CVE-2020-35654.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-25289
