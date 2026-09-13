# [M] Frappe has Possibility of Remote Code Execution due to improper validation

## Summary
Severity: Medium
Advisory: GHSA-v342-4xr9-x3q3
CVE: CVE-2025-30213
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2025-03-25
Source: https://github.com/advisories/GHSA-v342-4xr9-x3q3
Type: github-advisory

## Affected
- PyPI: `frappe` — affected >=0 <14.91.0
- PyPI: `frappe` — affected >=15.0.0 <15.52.0

## Details
### Impact
A system user was able to create certain documents in a specific way that could lead to RCE.

### Workarounds
There's no workaround, an upgrade is required.

### Credits
Thanks to Thanh of Calif.io for reporting the issue

## References
- https://github.com/frappe/frappe/security/advisories/GHSA-v342-4xr9-x3q3
- https://nvd.nist.gov/vuln/detail/CVE-2025-30213
- https://github.com/frappe/frappe
