# [M] CVE-2024-22368

## Summary
Severity: Medium
Advisory: CVE-2024-22368
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2024-01-09
Source: https://osv.dev/vulnerability/CVE-2024-22368
Type: osv

## Details
The Spreadsheet::ParseXLSX package before 0.28 for Perl can encounter an out-of-memory condition during parsing of a crafted XLSX document. This occurs because the memoize implementation does not have appropriate constraints on merged cells.

## References
- https://lists.debian.org/debian-lts-announce/2024/01/msg00018.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/WNJVC4C5C5V44DNOZ5BHVU53CDXPB2OJ/
- https://security.metacpan.org/2024/02/10/vulnerable-spreadsheet-parsing-modules.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/6R7NYWVVZYDZIQC5YEXNHZM6VEE26SJV/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/WNJVC4C5C5V44DNOZ5BHVU53CDXPB2OJ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6R7NYWVVZYDZIQC5YEXNHZM6VEE26SJV/
- https://metacpan.org/dist/Spreadsheet-ParseXLSX/changes
- http://www.openwall.com/lists/oss-security/2024/01/10/2
- https://github.com/haile01/perl_spreadsheet_excel_rce_poc/blob/main/parse_xlsx_bomb.md
