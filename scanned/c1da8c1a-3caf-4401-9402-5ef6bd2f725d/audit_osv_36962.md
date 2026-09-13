# [H] ERP: Document access through endpoints due to missing validation

## Summary
Severity: High
Advisory: CVE-2026-27471
Aliases: GHSA-wpfx-jw7g-7f83
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-02-21
Source: https://osv.dev/vulnerability/CVE-2026-27471
Type: osv

## Details
ERP is a free and open source Enterprise Resource Planning tool. In versions up to 15.98.0 and 16.0.0-rc.1 and through 16.6.0, certain endpoints lacked access validation which allowed for unauthorized document access. This issue has been fixed in versions 15.98.1 and 16.6.1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/27xxx/CVE-2026-27471.json
- https://github.com/frappe/erpnext/security/advisories/GHSA-wpfx-jw7g-7f83
- https://nvd.nist.gov/vuln/detail/CVE-2026-27471
- https://github.com/frappe/erpnext/commit/78fc9424d9085c2eafe1211931e22d7044f85fc7
