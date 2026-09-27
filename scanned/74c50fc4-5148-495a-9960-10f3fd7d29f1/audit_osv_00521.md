# [M] ALPINE-CVE-2017-14503

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2017-14503
Ecosystem: Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-09-17
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-14503
Type: osv

## Affected
- Alpine:v3.7: `libarchive` — affected >=0 <3.3.3-r0
- Alpine:v3.8: `libarchive` — affected >=0 <3.3.3-r0
- Alpine:v3.9: `libarchive` — affected >=0 <3.3.3-r0

## Details
libarchive 3.3.2 suffers from an out-of-bounds read within lha_read_data_none() in archive_read_support_format_lha.c when extracting a specially crafted lha archive, related to lha_crc16.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-14503
