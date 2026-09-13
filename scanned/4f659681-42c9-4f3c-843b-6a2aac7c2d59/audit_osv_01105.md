# [H] ALPINE-CVE-2018-20030

## Summary
Severity: High
Advisory: ALPINE-CVE-2018-20030
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.8, Alpine:v3.9
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-02-20
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-20030
Type: osv

## Affected
- Alpine:v3.10: `libexif` — affected >=0 <0.6.22-r0
- Alpine:v3.11: `libexif` — affected >=0 <0.6.22-r0
- Alpine:v3.12: `libexif` — affected >=0 <0.6.22-r0
- Alpine:v3.8: `libexif` — affected >=0 <0.6.22-r0
- Alpine:v3.9: `libexif` — affected >=0 <0.6.22-r0

## Details
An error when processing the EXIF_IFD_INTEROPERABILITY and EXIF_IFD_EXIF tags within libexif version 0.6.21 can be exploited to exhaust available CPU resources.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-20030
