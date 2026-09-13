# [M] ALPINE-CVE-2017-14166

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2017-14166
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-09-06
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-14166
Type: osv

## Affected
- Alpine:v3.10: `libarchive` — affected >=0 <3.3.2-r1
- Alpine:v3.11: `libarchive` — affected >=0 <3.3.2-r1
- Alpine:v3.12: `libarchive` — affected >=0 <3.3.2-r1
- Alpine:v3.13: `libarchive` — affected >=0 <3.3.2-r1
- Alpine:v3.14: `libarchive` — affected >=0 <3.3.2-r1
- Alpine:v3.15: `libarchive` — affected >=0 <3.3.2-r1
- Alpine:v3.16: `libarchive` — affected >=0 <3.3.2-r1
- Alpine:v3.17: `libarchive` — affected >=0 <3.3.2-r1
- Alpine:v3.18: `libarchive` — affected >=0 <3.3.2-r1
- Alpine:v3.19: `libarchive` — affected >=0 <3.3.2-r1
- Alpine:v3.20: `libarchive` — affected >=0 <3.3.2-r1
- Alpine:v3.21: `libarchive` — affected >=0 <3.3.2-r1
- Alpine:v3.22: `libarchive` — affected >=0 <3.3.2-r1
- Alpine:v3.23: `libarchive` — affected >=0 <3.3.2-r1
- Alpine:v3.24: `libarchive` — affected >=0 <3.3.2-r1
- Alpine:v3.4: `libarchive` — affected >=0 <3.2.2-r1
- Alpine:v3.5: `libarchive` — affected >=0 <3.3.1-r2
- Alpine:v3.6: `libarchive` — affected >=0 <3.3.1-r2
- Alpine:v3.7: `libarchive` — affected >=0 <3.3.2-r1
- Alpine:v3.8: `libarchive` — affected >=0 <3.3.2-r1
- Alpine:v3.9: `libarchive` — affected >=0 <3.3.2-r1

## Details
libarchive 3.3.2 allows remote attackers to cause a denial of service (xml_data heap-based buffer over-read and application crash) via a crafted xar archive, related to the mishandling of empty strings in the atol8 function in archive_read_support_format_xar.c.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-14166
