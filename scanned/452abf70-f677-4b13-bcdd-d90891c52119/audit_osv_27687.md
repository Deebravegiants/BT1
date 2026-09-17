# [H] Frappe SQL Injection from reporting logic

## Summary
Severity: High
Advisory: CVE-2024-24813
Aliases: GHSA-fxfv-7gwx-54jh
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-03-20
Source: https://osv.dev/vulnerability/CVE-2024-24813
Type: osv

## Details
Frappe is a full-stack web application framework. Prior to versions 14.64.0 and 15.0.0, SQL injection from a particular whitelisted method can result in access to data which the user doesn't have permission to access. Versions 14.64.0 and 15.0.0 contain a patch for this issue. No known workarounds are available.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/24xxx/CVE-2024-24813.json
- https://github.com/frappe/frappe/security/advisories/GHSA-fxfv-7gwx-54jh
- https://nvd.nist.gov/vuln/detail/CVE-2024-24813
