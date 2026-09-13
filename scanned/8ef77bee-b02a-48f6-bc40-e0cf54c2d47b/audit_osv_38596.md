# [M] Frappe HR vulnerable to Improper Access Control

## Summary
Severity: Medium
Advisory: CVE-2026-40888
Aliases: GHSA-4375-7rxj-9hfx
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-04-21
Source: https://osv.dev/vulnerability/CVE-2026-40888
Type: osv

## Details
Frappe HR is an open-source human resources management solution (HRMS). Prior to versions 15.58.1 and 16.4.1, an authenticated user with default role can access unauthorized information by exploiting certain api endpoint. Versions 15.58.1 and 16.4.1 contain a patch. No known workarounds are available.

## References
- https://github.com/frappe/hrms/releases/tag/v15.58.1
- https://github.com/frappe/hrms/releases/tag/v16.4.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40888.json
- https://github.com/frappe/hrms/security/advisories/GHSA-4375-7rxj-9hfx
- https://nvd.nist.gov/vuln/detail/CVE-2026-40888
