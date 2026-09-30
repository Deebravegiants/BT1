# [M] Minder GetRepositoryByName data leak

## Summary
Severity: Medium
Advisory: GHSA-ggp5-28x4-xcj9
CVE: CVE-2024-31455
CWE: CWE-200
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-04-09
Source: https://github.com/advisories/GHSA-ggp5-28x4-xcj9
Type: github-advisory

## Affected
- Go: `github.com/stacklok/minder` — affected >=0.0.39 <0.0.40

## Details
### Impact
A recent refactoring added the ability to get GitHub repositories registered to a project without specifying a specific provider.  Unfortunately, the SQL query for doing so was missing parenthesis, and would select a random repository.

### Patches
Patched in #2941

### Workarounds
Revert prior to `5c381cf`, or roll forward past `2eb94e7`

### References
N/A

## References
- https://github.com/stacklok/minder/security/advisories/GHSA-ggp5-28x4-xcj9
- https://nvd.nist.gov/vuln/detail/CVE-2024-31455
- https://github.com/stacklok/minder/pull/2941
- https://github.com/stacklok/minder/commit/11b6573ad62cfdd783a8bb52f3fce461466037f4
- https://github.com/stacklok/minder/commit/5c381cfbf3e4b7ce040ed8511a1fae1a78a0014b
- https://github.com/stacklok/minder
