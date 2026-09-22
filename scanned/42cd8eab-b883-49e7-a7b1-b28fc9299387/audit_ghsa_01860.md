# [M] YetiForceCRM is vulnerable to Business Logic Errors in the weight of a product

## Summary
Severity: Medium
Advisory: GHSA-cxg7-84wp-8pcq
CVE: CVE-2021-4117
CWE: CWE-20
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2021-12-16
Source: https://github.com/advisories/GHSA-cxg7-84wp-8pcq
Type: github-advisory

## Affected
- Packagist: `yetiforce/yetiforce-crm` — affected >=0

## Details
YetiForceCRM is vulnerable to Business Logic Errors in the Weight of a Product since that value can be a negative number.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-4117
- https://github.com/yetiforcecompany/yetiforcecrm/commit/8dccd93442725f245b4b71986bbe6f4f48639239
- https://github.com/yetiforcecompany/yetiforcecrm
- https://huntr.dev/bounties/0b81e572-bdc9-4caf-aa02-81f3c7ad7c0a
