# [M] Ghost vulnerable to arbitrary file read via symlinks in content import

## Summary
Severity: Medium
Advisory: GHSA-9c9v-w225-v5rg
CVE: CVE-2023-40028
CWE: CWE-22, CWE-59
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-08-15
Source: https://github.com/advisories/GHSA-9c9v-w225-v5rg
Type: github-advisory

## Affected
- npm: `ghost` — affected >=0 <5.59.1

## Details
### Impact

A vulnerability in Ghost allows authenticated users to upload files which are symlinks. This can be exploited to perform an arbitrary file read of any file on the operating system.

Site administrators can check for exploitation of this issue by looking for unknown symlinks within Ghost's `content/` folder

### Vulnerable versions

This security vulnerability is present in Ghost ≤ v5.59.0.

### Patches

v5.59.1 contains a fix for this issue.

### For more information

If you have any questions or comments about this advisory:
* Email us at [security@ghost.org](mailto:security@ghost.org)

## References
- https://github.com/TryGhost/Ghost/security/advisories/GHSA-9c9v-w225-v5rg
- https://nvd.nist.gov/vuln/detail/CVE-2023-40028
- https://github.com/TryGhost/Ghost/commit/690fbf3f7302ff3f77159c0795928bdd20f41205
- https://github.com/TryGhost/Ghost
