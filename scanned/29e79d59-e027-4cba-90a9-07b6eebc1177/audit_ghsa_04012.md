# [H] Authentication Bypass by Spoofing in express-cart

## Summary
Severity: High
Advisory: GHSA-wj36-v8j4-pc7c
CVE: CVE-2018-16483
CWE: CWE-290
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2019-02-07
Source: https://github.com/advisories/GHSA-wj36-v8j4-pc7c
Type: github-advisory

## Affected
- npm: `express-cart` — affected >=0 <1.1.6

## Details
A deficiency in the access control in module express-cart <=1.1.5 allows unprivileged users to add new users to the application as administrators.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-16483
- https://hackerone.com/reports/343626
- https://github.com/advisories/GHSA-wj36-v8j4-pc7c
