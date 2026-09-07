# [M] Angular Redactor XSS Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-88fh-8979-q2rr
CVE: CVE-2018-13339
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-88fh-8979-q2rr
Type: github-advisory

## Affected
- npm: `angular-redactor` — affected >=0

## Details
Imperavi Redactor 3 in Angular Redactor 1.1.6, when HTML content mode is used, allows stored XSS, as demonstrated by an onerror attribute of an IMG element, a related issue to CVE-2018-7035.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-13339
- https://github.com/TylerGarlick/angular-redactor/issues/77
- https://github.com/gleez/cms/issues/796
- https://github.com/TylerGarlick/angular-redactor
