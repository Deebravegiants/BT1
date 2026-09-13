# [H] Headplane: Path Traversal + RBAC Bypass in renameNode allows authenticated OIDC users to expire or rename any node/user

## Summary
Severity: High
Advisory: CVE-2026-46484
Aliases: GHSA-vgj6-hcf2-fqf6
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H)
Published: 2026-06-08
Source: https://osv.dev/vulnerability/CVE-2026-46484
Type: osv

## Details
Headplane is a feature-complete Web UI for Headscale. Prior to versions 0.6.3 and 0.7.0-beta.3, Headplane was vulnerable to a path traversal / authorization bypass in the Headscale API client used by node and user rename operations. This issue has been patched in versions 0.6.3 and 0.7.0-beta.3.

## References
- https://github.com/tale/headplane/releases/tag/v0.6.3
- https://github.com/tale/headplane/releases/tag/v0.7.0-beta.3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46484.json
- https://github.com/tale/headplane/security/advisories/GHSA-vgj6-hcf2-fqf6
- https://nvd.nist.gov/vuln/detail/CVE-2026-46484
