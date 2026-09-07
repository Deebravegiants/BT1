# [H] netfoil: Incorrect block responses could lead to localhost traffic

## Summary
Severity: High
Advisory: GHSA-xvg2-cgv6-6h7v
CWE: CWE-693
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:A/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-29
Source: https://github.com/advisories/GHSA-xvg2-cgv6-6h7v
Type: github-advisory

## Affected
- Go: `github.com/tinfoil-factory/netfoil` — affected >=0 <0.4.0

## Details
### Summary
`0.0.0.0` was used instead of NXDOMAIN for block responses. On Linux, which is the target platform for netfoil, the `0.0.0.0` is sent to localhost rather than just dropped.

### Impact
Unintended traffic could be sent to localhost. Impact depends on running services and firewall rules.

## References
- https://github.com/tinfoil-factory/netfoil/security/advisories/GHSA-xvg2-cgv6-6h7v
- https://github.com/tinfoil-factory/netfoil/pull/33
- https://github.com/tinfoil-factory/netfoil/commit/891d3513c77999a9deef9f23506807d9653ee448
- https://github.com/tinfoil-factory/netfoil
- https://github.com/tinfoil-factory/netfoil/releases/tag/v0.4.0
