# [M] netfoil's optional seccomp sandboxing was not applied

## Summary
Severity: Medium
Advisory: GHSA-vjgj-42f6-7997
CWE: CWE-791
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-29
Source: https://github.com/advisories/GHSA-vjgj-42f6-7997
Type: github-advisory

## Affected
- Go: `github.com/tinfoil-factory/netfoil` — affected >=0 <0.2.1

## Details
### Summary
The optional flag `--filter-system-calls` was not applied even if specified.

### Details
This is a defense in depth feature to apply additional seccomp filters after the binary has started. The example config also sandboxes the binary with systemd.

### Impact
Reduced sandboxing of the netfoil binary.

## References
- https://github.com/tinfoil-factory/netfoil/security/advisories/GHSA-vjgj-42f6-7997
- https://github.com/tinfoil-factory/netfoil/commit/8c84f1b03adf1df5b4e6d07a49043d13dbbf9ee1
- https://github.com/tinfoil-factory/netfoil
- https://github.com/tinfoil-factory/netfoil/releases/tag/v0.2.1
