# [H] ALPINE-CVE-2020-13113

## Summary
Severity: High
Advisory: ALPINE-CVE-2020-13113
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.8, Alpine:v3.9
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:H)
Published: 2020-05-21
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-13113
Type: osv

## Affected
- Alpine:v3.10: `libexif` — affected >=0 <0.6.22-r0
- Alpine:v3.11: `libexif` — affected >=0 <0.6.22-r0
- Alpine:v3.12: `libexif` — affected >=0 <0.6.22-r0
- Alpine:v3.8: `libexif` — affected >=0 <0.6.22-r0
- Alpine:v3.9: `libexif` — affected >=0 <0.6.22-r0

## Details
An issue was discovered in libexif before 0.6.22. Use of uninitialized memory in EXIF Makernote handling could lead to crashes and potential use-after-free conditions.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-13113
