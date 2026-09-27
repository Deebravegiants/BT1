# [H] ALPINE-CVE-2017-14502

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-14502
Ecosystem: Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-09-17
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-14502
Type: osv

## Affected
- Alpine:v3.7: `libarchive` — affected >=0 <3.3.3-r0
- Alpine:v3.8: `libarchive` — affected >=0 <3.3.3-r0
- Alpine:v3.9: `libarchive` — affected >=0 <3.3.3-r0

## Details
read_header in archive_read_support_format_rar.c in libarchive 3.3.2 suffers from an off-by-one error for UTF-16 names in RAR archives, leading to an out-of-bounds read in archive_read_format_rar_read_header.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-14502
