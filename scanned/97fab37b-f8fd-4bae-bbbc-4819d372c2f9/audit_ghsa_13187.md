# [M] Contao Cross-site Scripting vulnerabililty

## Summary
Severity: Medium
Advisory: GHSA-mpg7-2rx9-h5qp
CVE: CVE-2018-5478
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-09-21
Source: https://github.com/advisories/GHSA-mpg7-2rx9-h5qp
Type: github-advisory

## Affected
- Packagist: `contao/core` — affected >=3.0.0 <3.5.32

## Details
Contao 3.x before 3.5.32 allows Cross-site Scripting (XSS) via the unsubscribe module in the frontend newsletter extension.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-5478
- https://github.com/contao/core/commit/3123d6527ae6c46087b0ad8061eb8651cb645b8d
- https://contao.org/en/news/contao-3_5_32.html
- https://github.com/FriendsOfPHP/security-advisories/blob/master/contao/core/CVE-2018-5478.yaml
- https://github.com/contao/core
- https://security.snyk.io/vuln/SNYK-PHP-CONTAOCORE-70397
