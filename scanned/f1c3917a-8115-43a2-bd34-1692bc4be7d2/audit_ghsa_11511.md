# [H] @google/clasp vulnerable to unsafe path traversal cloning or pulling a malicious script

## Summary
Severity: High
Advisory: GHSA-hqjg-pww4-pcgq
CVE: CVE-2026-4092
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-13
Source: https://github.com/advisories/GHSA-hqjg-pww4-pcgq
Type: github-advisory

## Affected
- npm: `@google/clasp` — affected >=0 <3.2.0

## Details
### Impact
Allows an attacker to perform a "Path Traversal" attack to modify files outside the projects directory, potentially allowing for running attacker code on the developer's machine.

### Patches
Fixed in version 3.2.0

### Workarounds
* Only clone or pull scripts from trusted sources
* Review the output of the `pull` and `clone` commands to verify only expected project files are modified

## References
- https://github.com/google/clasp/security/advisories/GHSA-hqjg-pww4-pcgq
- https://nvd.nist.gov/vuln/detail/CVE-2026-4092
- https://github.com/google/clasp/pull/1109
- https://github.com/google/clasp/commit/ba6bd666fe74de54950122b5d92ecf1dcc02a9d3
- https://github.com/google/clasp
- https://github.com/google/clasp/releases/tag/v3.2.0
