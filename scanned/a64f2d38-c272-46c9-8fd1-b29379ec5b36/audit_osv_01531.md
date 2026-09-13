# [M] ALPINE-CVE-2019-19221

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2019-19221
Ecosystem: Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-11-21
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-19221
Type: osv

## Affected
- Alpine:v3.13: `libarchive` — affected >=0 <3.4.2-r0
- Alpine:v3.14: `libarchive` — affected >=0 <3.4.2-r0
- Alpine:v3.15: `libarchive` — affected >=0 <3.4.2-r0
- Alpine:v3.16: `libarchive` — affected >=0 <3.4.2-r0
- Alpine:v3.17: `libarchive` — affected >=0 <3.4.2-r0
- Alpine:v3.18: `libarchive` — affected >=0 <3.4.2-r0
- Alpine:v3.19: `libarchive` — affected >=0 <3.4.2-r0
- Alpine:v3.20: `libarchive` — affected >=0 <3.4.2-r0
- Alpine:v3.21: `libarchive` — affected >=0 <3.4.2-r0
- Alpine:v3.22: `libarchive` — affected >=0 <3.4.2-r0
- Alpine:v3.23: `libarchive` — affected >=0 <3.4.2-r0
- Alpine:v3.24: `libarchive` — affected >=0 <3.4.2-r0

## Details
In Libarchive 3.4.0, archive_wstring_append_from_mbs in archive_string.c has an out-of-bounds read because of an incorrect mbrtowc or mbtowc call. For example, bsdtar crashes via a crafted archive.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-19221
