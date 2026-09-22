# [M] OpenProject: Shares API Information Disclosure

## Summary
Severity: Medium
Advisory: CVE-2026-44735
Aliases: GHSA-cfg3-f34w-9xx5
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-06-26
Source: https://osv.dev/vulnerability/CVE-2026-44735
Type: osv

## Details
OpenProject is open-source, web-based project management software. Prior to 17.3.2 and 17.4.0, the GET /api/v3/shares endpoint returns share details for ALL work packages in a project to any user with the view_shared_work_packages permission. The authorization check operates at the project level only — it does not verify the requesting user can actually view each individual shared work package. This allows a regular project member to discover work package IDs and subjects (including confidential titles), which users have been granted shared access, what role level was assigned (Editor, Commenter, Viewer). This vulnerability is fixed in 17.3.2 and 17.4.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44735.json
- https://github.com/opf/openproject/security/advisories/GHSA-cfg3-f34w-9xx5
- https://nvd.nist.gov/vuln/detail/CVE-2026-44735
