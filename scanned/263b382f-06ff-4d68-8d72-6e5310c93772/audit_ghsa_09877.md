# [M] gitverify has improper tag signature verification

## Summary
Severity: Medium
Advisory: GHSA-h829-5cg7-6hff
CWE: CWE-347
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-24
Source: https://github.com/advisories/GHSA-h829-5cg7-6hff
Type: github-advisory

## Affected
- Go: `github.com/supply-chain-tools/gitverify` — affected >=0 <0.0.0-20260421124901-c2c60da05d5c

## Details
gitverify is still a prototype.

### Impact
The bug is related to `requireSignedTags` which is on by default: an unsigned annotated tag would pass the verification. The commit pointed to by the tag would still have to be signed by a maintainer or a contributor.

### Patches
Since the initial commit, fixed in c2c60da05d5c73621d0ce7ea02770bacd79ec8b1 (no semantic versions yet).

### Workarounds
No

## References
- https://github.com/supply-chain-tools/gitverify/security/advisories/GHSA-h829-5cg7-6hff
- https://github.com/supply-chain-tools/gitverify/commit/c2c60da05d5c73621d0ce7ea02770bacd79ec8b1
- https://github.com/supply-chain-tools/gitverify
