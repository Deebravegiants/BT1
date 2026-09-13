# [M] CVE-2024-23525

## Summary
Severity: Medium
Advisory: CVE-2024-23525
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2024-01-17
Source: https://osv.dev/vulnerability/CVE-2024-23525
Type: osv

## Details
The Spreadsheet::ParseXLSX package before 0.30 for Perl allows XXE attacks because it neglects to use the no_xxe option of XML::Twig.

## References
- https://gist.github.com/phvietan/d1c95a88ab6e17047b0248d6bf9eac4a
- https://metacpan.org/release/NUDDLEGG/Spreadsheet-ParseXLSX-0.30/changes
- https://security.metacpan.org/2024/02/10/vulnerable-spreadsheet-parsing-modules.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/23xxx/CVE-2024-23525.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-23525
- https://github.com/MichaelDaum/spreadsheet-parsexlsx/issues/10
- http://www.openwall.com/lists/oss-security/2024/01/18/4
- https://lists.debian.org/debian-lts-announce/2024/01/msg00018.html
