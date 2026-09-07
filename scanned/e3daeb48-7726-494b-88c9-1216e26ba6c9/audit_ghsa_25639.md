# [C] Remote code injection in dompdf/dompdf

## Summary
Severity: Critical
Advisory: GHSA-x752-qjv4-c4hc
CVE: CVE-2022-28368
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-04-04
Source: https://github.com/advisories/GHSA-x752-qjv4-c4hc
Type: github-advisory

## Affected
- Packagist: `dompdf/dompdf` — affected >=0 <1.2.1

## Details
Dompdf is an HTML to PDF converter. Dompdf before 1.2.1 allows remote code execution via a .php file in the src:url field of an @font-face Cascading Style Sheets (CSS) statement (within an HTML input file).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-28368
- https://github.com/dompdf/dompdf/issues/2598
- https://github.com/dompdf/dompdf/pull/2808
- https://github.com/dompdf/dompdf/commit/4c70e1025bcd9b7694b95dd552499bd83cd6141d
- https://github.com/FriendsOfPHP/security-advisories/blob/master/dompdf/dompdf/CVE-2022-28368.yaml
- https://github.com/advisories/GHSA-x752-qjv4-c4hc
- https://github.com/dompdf/dompdf
- https://github.com/snyk-labs/php-goof
- https://packagist.org/packages/dompdf/dompdf#v1.2.1
- https://snyk.io/blog/security-alert-php-pdf-library-dompdf-rce
- http://packetstormsecurity.com/files/171738/Dompdf-1.2.1-Remote-Code-Execution.html
