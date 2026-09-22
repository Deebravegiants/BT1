# [M] Netfoil has incorrect allowlist enforcement

## Summary
Severity: Medium
Advisory: GHSA-84g5-x8j3-7235
CWE: CWE-183, CWE-193
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-29
Source: https://github.com/advisories/GHSA-84g5-x8j3-7235
Type: github-advisory

## Affected
- Go: `github.com/tinfoil-factory/netfoil` — affected >=0 <0.2.1

## Details
### Summary
Rules could be bypassed by changing the first character: `example.com` could be be bypassed by e.g. `fxample.com`.

### Details
Off-by-one error in the suffixtrie implementation.

### Impact
The domain filter could be bypassed. Please note that DNS filtering alone is not enough to block malicious traffic.

## References
- https://github.com/tinfoil-factory/netfoil/security/advisories/GHSA-84g5-x8j3-7235
- https://github.com/tinfoil-factory/netfoil/commit/0ca054acf97b011e4fdd40392475c7786b975ec3
- https://github.com/tinfoil-factory/netfoil
- https://github.com/tinfoil-factory/netfoil/releases/tag/v0.2.1
