# [H] CVE-2023-7101

## Summary
Severity: High
Advisory: CVE-2023-7101
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2023-12-24
Source: https://osv.dev/vulnerability/CVE-2023-7101
Type: osv

## Details
Spreadsheet::ParseExcel version 0.65 is a Perl module used for parsing Excel files. Spreadsheet::ParseExcel is vulnerable to an arbitrary code execution (ACE) vulnerability due to passing unvalidated input from a file into a string-type “eval”. Specifically, the issue stems from the evaluation of Number format strings (not to be confused with printf-style format strings) within the Excel parsing logic.

## References
- https://github.com/jmcnamara/spreadsheet-parseexcel/blob/c7298592e102a375d43150cd002feed806557c15/lib/Spreadsheet/ParseExcel/Utility.pm#L171
- https://https://metacpan.org/dist/Spreadsheet-ParseExcel
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2023-7101
- https://https://github.com/haile01/perl_spreadsheet_excel_rce_poc
- https://security.metacpan.org/2024/02/10/vulnerable-spreadsheet-parsing-modules.html
- https://github.com/mandiant/Vulnerability-Disclosures/blob/master/2023/MNDT-2023-0019.md
- https://https://www.cve.org/CVERecord?id=CVE-2023-7101
- https://https://github.com/jmcnamara/spreadsheet-parseexcel/commit/bd3159277e745468e2c553417b35d5d7dc7405bc
- http://www.openwall.com/lists/oss-security/2023/12/29/4
- https://lists.debian.org/debian-lts-announce/2023/12/msg00025.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/IFEHKULQRVXHIV7XXK2RGD4VQN6Y4CV5/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/M2FIWDHRYTAAQLGM6AFOZVM7AFZ4H2ZR/
