# [M] TastyIgniter Has an Incorrect Access Control Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-w5h7-mw56-4v7x
CVE: CVE-2024-44314
CWE: CWE-285
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2025-03-18
Source: https://github.com/advisories/GHSA-w5h7-mw56-4v7x
Type: github-advisory

## Affected
- Packagist: `tastyigniter/tastyigniter` — affected >=0 <4.0.0

## Details
TastyIgniter 3.7.6 contains an Incorrect Access Control vulnerability in the Orders Management System, allowing unauthorized users to update order statuses. The issue occurs in the index_onUpdateStatus() function within Orders.php, which fails to verify if the user has permission to modify an order's status. This flaw can be exploited remotely, leading to unauthorized order manipulation.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-44314
- https://github.com/tastyigniter/TastyIgniter
- https://github.com/tastyigniter/TastyIgniter/blob/3.x/app/admin/controllers/Orders.php
- https://medium.com/@cnetsec/cve-2024-44314-incorrect-access-control-in-function-updateorder-fc5f2b1b0467
