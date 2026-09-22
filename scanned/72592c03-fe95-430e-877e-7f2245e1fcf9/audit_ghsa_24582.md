# [H] DOMPDF Remote File Inclusion Vulnerability

## Summary
Severity: High
Advisory: GHSA-48r9-4v93-x4wh
CVE: CVE-2010-4879
CWE: CWE-94
Ecosystem: Packagist
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-48r9-4v93-x4wh
Type: github-advisory

## Affected
- Packagist: `dompdf/dompdf` — affected >=0.6 <0.6.1

## Details
PHP remote file inclusion vulnerability in dompdf.php in dompdf 0.6.0 beta1 allows remote attackers to execute arbitrary PHP code via a URL in the `input_file` parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2010-4879
- https://github.com/dompdf/dompdf/commit/23a693993299e669306929e3d49a4a1f7b3fb028
- https://github.com/FriendsOfPHP/security-advisories/blob/master/dompdf/dompdf/CVE-2010-4879.yaml
- https://github.com/dompdf/dompdf
- https://github.com/dompdf/dompdf/releases/tag/v0.6.2
- https://github.com/dompdf/dompdf/wiki/Securing-dompdf
- http://www.exploit-db.com/exploits/14851
