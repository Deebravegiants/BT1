# [M] pnpm has Windows-specific tarball Path Traversal

## Summary
Severity: Medium
Advisory: CVE-2026-23889
Aliases: GHSA-6x96-7vc8-cm3p
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N)
Published: 2026-01-26
Source: https://osv.dev/vulnerability/CVE-2026-23889
Type: osv

## Details
pnpm is a package manager. Prior to version 10.28.1, a path traversal vulnerability in pnpm's tarball extraction allows malicious packages to write files outside the package directory on Windows. The path normalization only checks for `./` but not `.\`. On Windows, backslashes are directory separators, enabling path traversal. This vulnerability is Windows-only. This issue impacts Windows pnpm users and Windows CI/CD pipelines (GitHub Actions Windows runners, Azure DevOps). It can lead to overwriting `.npmrc`, build configs, or other files. Version 10.28.1 contains a patch.

## References
- https://github.com/pnpm/pnpm/releases/tag/v10.28.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23889.json
- https://github.com/pnpm/pnpm/security/advisories/GHSA-6x96-7vc8-cm3p
- https://nvd.nist.gov/vuln/detail/CVE-2026-23889
- https://github.com/pnpm/pnpm/commit/6ca07ffbe6fc0e8b8cdc968f228903ba0886f7c0
