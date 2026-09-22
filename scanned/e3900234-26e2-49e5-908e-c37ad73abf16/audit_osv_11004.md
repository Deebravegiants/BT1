# [H] CVE-2017-5601

## Summary
Severity: High
Advisory: CVE-2017-5601
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-01-27
Source: https://osv.dev/vulnerability/CVE-2017-5601
Type: osv

## Details
An error in the lha_read_file_header_1() function (archive_read_support_format_lha.c) in libarchive 3.2.2 allows remote attackers to trigger an out-of-bounds read memory access and subsequently cause a crash via a specially crafted archive.

## References
- http://www.securitytracker.com/id/1037974
- https://lists.debian.org/debian-lts-announce/2018/11/msg00037.html
- https://secunia.com/secunia_research/2017-3/
- http://www.securityfocus.com/bid/95837
- https://github.com/libarchive/libarchive/commit/98dcbbf0bf4854bf987557e55e55fff7abbf3ea9
