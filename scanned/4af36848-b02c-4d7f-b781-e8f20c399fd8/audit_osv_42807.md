# [M] Infracost: Arbitrary file read via config-template readFile symlink traversal

## Summary
Severity: Medium
Advisory: CVE-2026-71493
Aliases: GHSA-mmg6-4qmv-6pc8, GO-2026-6439
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:A/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-21
Source: https://osv.dev/vulnerability/CVE-2026-71493
Type: osv

## Details
Infracost provides cloud cost intelligence for engineers, AI coding agents, and CI/CD. Prior to 0.10.45, the readFile, pathExists, isDir, and matchPaths template functions in internal/config/template/parser.go use a lexical filepath.Rel check and a leaf-only os.Lstat check that do not resolve an intermediate directory symlink. A repository can contain a path such as evil/file where evil points outside the checkout, causing os.ReadFile and related operations to follow the symlink and read runner-accessible files. The resulting content is rendered into generated configuration and can be surfaced through the Infracost dashboard or pull request comment, with greater impact in workflows that provide repository secrets. This issue is fixed in version 0.10.45.

## References
- https://github.com/infracost/infracost/releases/tag/v0.10.45
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/71xxx/CVE-2026-71493.json
- https://github.com/infracost/infracost/security/advisories/GHSA-mmg6-4qmv-6pc8
- https://nvd.nist.gov/vuln/detail/CVE-2026-71493
- https://github.com/infracost/infracost/commit/4d39331afc0e27752d16d9d91c34583e5e8487fb
- https://github.com/infracost/infracost/pull/3586
