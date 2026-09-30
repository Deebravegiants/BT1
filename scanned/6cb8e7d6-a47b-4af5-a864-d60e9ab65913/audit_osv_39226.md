# [M] OneDev: Path Traversal (read capability via Git LFS pointer resolution)

## Summary
Severity: Medium
Advisory: CVE-2026-44647
Aliases: GHSA-59wq-74xg-w85v
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-05-14
Source: https://osv.dev/vulnerability/CVE-2026-44647
Type: osv

## Details
OneDev is a Git server with CI/CD, kanban, and packages. Prior to 15.0.2, there is behavior that breaks the expected boundary between repository-controlled LFS metadata and server-local filesystem paths. A repository object can steer raw blob reads to arbitrary local files that the server account can access. User with push permission to any repository will be able to access any server files accessible by server process. This vulnerability is fixed in 15.0.2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44647.json
- https://github.com/theonedev/onedev/security/advisories/GHSA-59wq-74xg-w85v
- https://nvd.nist.gov/vuln/detail/CVE-2026-44647
