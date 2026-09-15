# [M] Tuist: IDOR in preview deletion API allows cross-tenant deletion of any preview by UUID

## Summary
Severity: Medium
Advisory: CVE-2026-44678
Aliases: GHSA-fqp5-hg46-cp2x
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-05-14
Source: https://osv.dev/vulnerability/CVE-2026-44678
Type: osv

## Details
Tuist is a virtual platform team for Swift app devs. In 1.180.8 and earlier, the DELETE /api/projects/{account_handle}/{project_handle}/previews/{preview_id} endpoint loads the preview by its UUID without verifying that the preview belongs to the project resolved from the URL path. The route's project-level authorization plug (AuthorizationPlug, :preview) authorizes the caller against the project encoded in account_handle/project_handle — which the attacker controls — and then the action deletes whichever preview's UUID is supplied. The check therefore guards the wrong project.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44678.json
- https://github.com/tuist/tuist/security/advisories/GHSA-fqp5-hg46-cp2x
- https://nvd.nist.gov/vuln/detail/CVE-2026-44678
