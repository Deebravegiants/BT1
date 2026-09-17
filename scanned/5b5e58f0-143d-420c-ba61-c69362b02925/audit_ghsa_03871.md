# [M] Authorization Bypass Through User-Controlled Key in Bagisto

## Summary
Severity: Medium
Advisory: GHSA-pwrf-q7h8-jjr7
CVE: CVE-2019-16403
CWE: CWE-639
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2019-11-08
Source: https://github.com/advisories/GHSA-pwrf-q7h8-jjr7
Type: github-advisory

## Affected
- Packagist: `bagisto/bagisto` — affected >=0 <0.1.5

## Details
In Webkul Bagisto before 0.1.5, the functionalities for customers to change their own values (such as address, review, orders, etc.) can also be manipulated by other customers.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-16403
- https://github.com/bagisto/bagisto/issues/749
