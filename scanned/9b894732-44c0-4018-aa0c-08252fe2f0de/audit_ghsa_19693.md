# [M] Frappe has possibility of SQL injection due to improper validations

## Summary
Severity: Medium
Advisory: GHSA-3hj6-r5c9-q8f3
CVE: CVE-2025-30212
CWE: CWE-89
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2025-03-25
Source: https://github.com/advisories/GHSA-3hj6-r5c9-q8f3
Type: github-advisory

## Affected
- PyPI: `frappe` — affected >=0 <14.89.0
- PyPI: `frappe` — affected >=15.0.0 <15.51.0

## Details
### Impact
An SQL Injection vulnerability has been identified in Frappe Framework which could allow a malicious actor to access sensitive information.

### Workarounds
Upgrading is required, no other workaround is present.

### Credits

Thanks to Thanh of Calif.io for reporting the issue

## References
- https://github.com/frappe/frappe/security/advisories/GHSA-3hj6-r5c9-q8f3
- https://nvd.nist.gov/vuln/detail/CVE-2025-30212
- https://github.com/frappe/frappe/commit/27f13437db161a173137d91cd07d0f9287d7c556
- https://github.com/frappe/frappe/commit/2ebd88520ecfa9bb7d3392b7de8c8f94a86ec05c
- https://github.com/frappe/frappe
