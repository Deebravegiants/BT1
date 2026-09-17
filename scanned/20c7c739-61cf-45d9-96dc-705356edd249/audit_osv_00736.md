# [C] ALPINE-CVE-2017-7544

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2017-7544
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 9.1 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2017-09-21
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-7544
Type: osv

## Affected
- Alpine:v3.10: `libexif` — affected >=0 <0.6.21-r3
- Alpine:v3.11: `libexif` — affected >=0 <0.6.21-r3
- Alpine:v3.12: `libexif` — affected >=0 <0.6.21-r3
- Alpine:v3.5: `libexif` — affected >=0 <0.6.21-r2
- Alpine:v3.6: `libexif` — affected >=0 <0.6.21-r2
- Alpine:v3.7: `libexif` — affected >=0 <0.6.21-r2
- Alpine:v3.8: `libexif` — affected >=0 <0.6.21-r3
- Alpine:v3.9: `libexif` — affected >=0 <0.6.21-r3

## Details
libexif through 0.6.21 is vulnerable to out-of-bounds heap read vulnerability in exif_data_save_data_entry function in libexif/exif-data.c caused by improper length computation of the allocated data of an ExifMnote entry which can cause denial-of-service or possibly information disclosure.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-7544
