# [M] Cross-site scripting (XSS)

## Summary
Severity: Medium
Advisory: GHSA-79hv-pfx6-hhpj
CVE: CVE-2021-28088
CWE: CWE-79
Ecosystem: Packagist
Published: 2021-03-12
Source: https://github.com/advisories/GHSA-79hv-pfx6-hhpj
Type: github-advisory

## Affected
- Packagist: `impresscms/impresscms` — affected >=0

## Details
Cross-site scripting (XSS) in modules/content/admin/content.php in ImpressCMS profile 1.4.2 allows remote attackers to inject arbitrary web script or HTML parameters through the "Display Name" field.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-28088
- https://hackerone.com/reports/1119296
- https://anotepad.com/note/read/s3kkk6h7
