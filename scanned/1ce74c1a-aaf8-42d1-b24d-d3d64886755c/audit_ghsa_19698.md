# [H] Frappe vulnerable to information disclosure leading to account takeover

## Summary
Severity: High
Advisory: GHSA-qrv3-jc3h-f3m6
CVE: CVE-2025-30214
CWE: CWE-200
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2025-03-25
Source: https://github.com/advisories/GHSA-qrv3-jc3h-f3m6
Type: github-advisory

## Affected
- PyPI: `frappe` — affected >=0 <14.89.0
- PyPI: `frappe` — affected >=15.0.0 <15.51.0

## Details
### Impact
Making crafted requests could lead to information disclosure that could further lead to account takeover.

### Workarounds
There's no workaround to fix this without upgrading.

### Credits
Thanks to Thanh of Calif.io for reporting the issue

## References
- https://github.com/frappe/frappe/security/advisories/GHSA-qrv3-jc3h-f3m6
- https://nvd.nist.gov/vuln/detail/CVE-2025-30214
- https://github.com/frappe/frappe
