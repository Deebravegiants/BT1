# [M] ALPINE-CVE-2017-14501

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2017-14501
Ecosystem: Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-09-17
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-14501
Type: osv

## Affected
- Alpine:v3.7: `libarchive` — affected >=0 <3.3.3-r0
- Alpine:v3.8: `libarchive` — affected >=0 <3.3.3-r0
- Alpine:v3.9: `libarchive` — affected >=0 <3.3.3-r0

## Details
An out-of-bounds read flaw exists in parse_file_info in archive_read_support_format_iso9660.c in libarchive 3.3.2 when extracting a specially crafted iso9660 iso file, related to archive_read_format_iso9660_read_header.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-14501
