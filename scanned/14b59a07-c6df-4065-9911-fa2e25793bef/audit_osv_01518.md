# [H] ALPINE-CVE-2019-18408

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-18408
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-10-24
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-18408
Type: osv

## Affected
- Alpine:v3.10: `libarchive` — affected >=0 <3.3.3-r1
- Alpine:v3.11: `libarchive` — affected >=0 <3.4.0-r0
- Alpine:v3.12: `libarchive` — affected >=0 <3.4.0-r0
- Alpine:v3.13: `libarchive` — affected >=0 <3.4.0-r0
- Alpine:v3.14: `libarchive` — affected >=0 <3.4.0-r0
- Alpine:v3.15: `libarchive` — affected >=0 <3.4.0-r0
- Alpine:v3.16: `libarchive` — affected >=0 <3.4.0-r0
- Alpine:v3.17: `libarchive` — affected >=0 <3.4.0-r0
- Alpine:v3.18: `libarchive` — affected >=0 <3.4.0-r0
- Alpine:v3.19: `libarchive` — affected >=0 <3.4.0-r0
- Alpine:v3.20: `libarchive` — affected >=0 <3.4.0-r0
- Alpine:v3.21: `libarchive` — affected >=0 <3.4.0-r0
- Alpine:v3.22: `libarchive` — affected >=0 <3.4.0-r0
- Alpine:v3.23: `libarchive` — affected >=0 <3.4.0-r0
- Alpine:v3.24: `libarchive` — affected >=0 <3.4.0-r0
- Alpine:v3.7: `libarchive` — affected >=0 <3.3.3-r1
- Alpine:v3.8: `libarchive` — affected >=0 <3.3.3-r1
- Alpine:v3.9: `libarchive` — affected >=0 <3.3.3-r1

## Details
archive_read_format_rar_read_data in archive_read_support_format_rar.c in libarchive before 3.4.0 has a use-after-free in a certain ARCHIVE_FAILED situation, related to Ppmd7_DecodeSymbol.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-18408
