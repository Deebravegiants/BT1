# [H] ALPINE-CVE-2017-5601

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-5601
Ecosystem: Alpine:v3.4, Alpine:v3.5
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-01-27
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-5601
Type: osv

## Affected
- Alpine:v3.4: `libarchive` — affected >=0 <3.2.2-r0
- Alpine:v3.5: `libarchive` — affected >=0 <3.2.2-r1

## Details
An error in the lha_read_file_header_1() function (archive_read_support_format_lha.c) in libarchive 3.2.2 allows remote attackers to trigger an out-of-bounds read memory access and subsequently cause a crash via a specially crafted archive.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-5601
