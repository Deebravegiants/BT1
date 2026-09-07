# [M] Improper Authorization in dolibarr/dolibarr

## Summary
Severity: Medium
Advisory: GHSA-4xc7-x2jr-cr74
CVE: CVE-2022-0731
CWE: CWE-639, CWE-863
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-02-24
Source: https://github.com/advisories/GHSA-4xc7-x2jr-cr74
Type: github-advisory

## Affected
- Packagist: `dolibarr/dolibarr` — affected >=0 <16.0

## Details
Dolibarr allows improper access control issues in the userphoto modulepart. The impact could lead to data exposure as the attached files and documents may contain sensitive information of relevant parties such as contacts, suppliers, invoices, orders, stocks, agenda, accounting and more.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-0731
- https://github.com/dolibarr/dolibarr/commit/209ab708d4b65fbd88ba4340d60b7822cb72651a
- https://github.com/dolibarr/dolibarr
- https://huntr.dev/bounties/e242ab4e-fc70-4b2c-a42d-5b3ee4895de8
