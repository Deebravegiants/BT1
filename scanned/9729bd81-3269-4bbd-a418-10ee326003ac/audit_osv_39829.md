# [M] Frappe: Lack of Permissions in restore/bulk_restore

## Summary
Severity: Medium
Advisory: CVE-2026-47765
Aliases: GHSA-cjjx-3v2x-37mf
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:L/SC:N/SI:N/SA:N)
Published: 2026-08-06
Source: https://osv.dev/vulnerability/CVE-2026-47765
Type: osv

## Details
Frappe is a full-stack web application framework. Prior to 15.110.0 and 16.20.0, the restore and bulk_restore endpoints do not apply the appropriate document permission checks, allowing an authenticated user to restore deleted documents without the required authorization. This issue is fixed in versions 15.110.0 and 16.20.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/47xxx/CVE-2026-47765.json
- https://github.com/frappe/frappe/security/advisories/GHSA-cjjx-3v2x-37mf
- https://nvd.nist.gov/vuln/detail/CVE-2026-47765
- https://github.com/frappe/frappe/commit/caa95f64f96ccf62f9f9fdfc03274527105cb44e
- https://github.com/frappe/frappe/commit/d5c5499c95953b0bb28f7b4907add01663bb8ca0
