# [M] Frappe HR: Permission Bypass in HRMS Leave Details API

## Summary
Severity: Medium
Advisory: CVE-2026-45081
Aliases: GHSA-9jpf-5vrm-hpcj
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-05-27
Source: https://osv.dev/vulnerability/CVE-2026-45081
Type: osv

## Details
Frappe HR is an open-source human resources management solution (HRMS). Prior to 16.5.0, authenticated employees could access other employees’ leave details due to improper authorization checks. This vulnerability is fixed in 16.5.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45081.json
- https://github.com/frappe/hrms/security/advisories/GHSA-9jpf-5vrm-hpcj
- https://nvd.nist.gov/vuln/detail/CVE-2026-45081
