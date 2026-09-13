# [M] Frappe HR has Improper Access Control on Files

## Summary
Severity: Medium
Advisory: CVE-2026-40889
Aliases: GHSA-6cg5-4q6m-vrgm
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-04-21
Source: https://osv.dev/vulnerability/CVE-2026-40889
Type: osv

## Details
Frappe HR is an open-source human resources management solution (HRMS). Prior to versions 15.58.2 and 16.4.2, authenticated users can access unauthorized files by exploiting certain api endpoint. Versions 15.58.2 and 16.4.2 contain a patch. No known workarounds are available.

## References
- https://github.com/frappe/hrms/releases/tag/v15.58.2
- https://github.com/frappe/hrms/releases/tag/v16.4.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40889.json
- https://github.com/frappe/hrms/security/advisories/GHSA-6cg5-4q6m-vrgm
- https://nvd.nist.gov/vuln/detail/CVE-2026-40889
