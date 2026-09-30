# [M] Frappe: Auth. bypass via update_page

## Summary
Severity: Medium
Advisory: CVE-2026-49394
Aliases: GHSA-r24j-xrj8-273q
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-10
Source: https://osv.dev/vulnerability/CVE-2026-49394
Type: osv

## Details
Frappe is a full-stack web application framework. Prior to 16.19.0, authorization bypass was possible via the update_page endpoint in Workspace because public workspaces did not receive the required Workspace Manager edit check. This issue is fixed in version 16.19.0.

## References
- https://github.com/frappe/frappe/releases/tag/v16.19.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/49xxx/CVE-2026-49394.json
- https://github.com/frappe/frappe/security/advisories/GHSA-r24j-xrj8-273q
- https://nvd.nist.gov/vuln/detail/CVE-2026-49394
- https://github.com/frappe/frappe/commit/2471d94c397dc23301b30ed3bb30353f53b33f2c
- https://github.com/frappe/frappe/commit/6eba29d7ae80cdb4d0b2a245a477b1d2312736ca
- https://github.com/frappe/frappe/pull/39508
- https://github.com/frappe/frappe/pull/39526
