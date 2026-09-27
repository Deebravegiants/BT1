# [M] Gitea runner registration-token GET endpoint performs a write under a read-only token scope

## Summary
Severity: Medium
Advisory: CVE-2026-24059
Aliases: GHSA-v43r-86x9-8523
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/CVE-2026-24059
Type: osv

## Details
The GET /api/v1/user/actions/runners/registration-token endpoint (and its owner- and repository-level equivalents) creates a new runner registration token if none exists, yet the API scope middleware classifies it as read-only because it is a GET request. A holder of a leaked read:user-scoped token can therefore mint a registration token and register a malicious Actions runner that executes workflow jobs with access to repository secrets and source code.

## References
- https://blog.gitea.com/release-of-1.25.5/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/24xxx/CVE-2026-24059.json
- https://github.com/go-gitea/gitea/releases/tag/v1.25.5
- https://github.com/go-gitea/gitea/security/advisories/GHSA-v43r-86x9-8523
- https://nvd.nist.gov/vuln/detail/CVE-2026-24059
- https://github.com/go-gitea/gitea/pull/36801
