# [M] OS Command injection in Bolt

## Summary
Severity: Medium
Advisory: GHSA-w8cj-mvf9-mpc9
CVE: CVE-2020-28925
CWE: CWE-78
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2021-05-06
Source: https://github.com/advisories/GHSA-w8cj-mvf9-mpc9
Type: github-advisory

## Affected
- Packagist: `bolt/bolt` — affected >=0 <3.7.2

## Details
Bolt before 3.7.2 does not restrict filter options in a Request in the Twig context, and is therefore inconsistent with the "How to Harden Your PHP for Better Security" guidance.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-28925
- https://github.com/bolt/bolt/commit/c0cd530e78c2a8c6d71ceb75b10c251b39fb923a
- https://github.com/bolt/bolt/compare/3.7.1...3.7.2
