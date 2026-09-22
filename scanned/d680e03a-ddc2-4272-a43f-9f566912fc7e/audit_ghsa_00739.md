# [H] Command injection in mversion

## Summary
Severity: High
Advisory: GHSA-qjg4-w4c6-f6c6
CVE: CVE-2020-4059
CWE: CWE-77
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2020-06-18
Source: https://github.com/advisories/GHSA-qjg4-w4c6-f6c6
Type: github-advisory

## Affected
- npm: `mversion` — affected >=0 <2.0.0

## Details
### Impact
This issue may lead to remote code execution if a client of the library calls the vulnerable method with untrusted input.

### Patches
Patched by version 2.0.0. Previous releases are deprecated in npm.

### Workarounds
Make sure to escape git commit messages when using the commitMessage option for the update function.

## References
- https://github.com/mikaelbr/mversion/security/advisories/GHSA-qjg4-w4c6-f6c6
- https://nvd.nist.gov/vuln/detail/CVE-2020-4059
- https://github.com/mikaelbr/mversion/commit/6c76c9efd27c7ff5a5c6f187e8b7a435c4722338
