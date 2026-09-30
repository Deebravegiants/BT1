# [M] ALPINE-CVE-2020-0093

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2020-0093
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.8, Alpine:v3.9
CVSS: 5.0 (CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:H/I:N/A:N)
Published: 2020-05-14
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-0093
Type: osv

## Affected
- Alpine:v3.10: `libexif` — affected >=0 <0.6.22-r0
- Alpine:v3.11: `libexif` — affected >=0 <0.6.22-r0
- Alpine:v3.12: `libexif` — affected >=0 <0.6.22-r0
- Alpine:v3.8: `libexif` — affected >=0 <0.6.22-r0
- Alpine:v3.9: `libexif` — affected >=0 <0.6.22-r0

## Details
In exif_data_save_data_entry of exif-data.c, there is a possible out of bounds read due to a missing bounds check. This could lead to local information disclosure with no additional execution privileges needed. User interaction is needed for exploitation.Product: AndroidVersions: Android-8.0 Android-8.1 Android-9 Android-10Android ID: A-148705132

## References
- https://security.alpinelinux.org/vuln/CVE-2020-0093
