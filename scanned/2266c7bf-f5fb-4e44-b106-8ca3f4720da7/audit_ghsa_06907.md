# [M] netfoil has a domain name filter bypass via multiple questions

## Summary
Severity: Medium
Advisory: GHSA-59qp-cfj3-rp64
CWE: CWE-436, CWE-693
Ecosystem: Go
CVSS: CVSS:4.0/AV:L/AC:L/AT:P/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-07
Source: https://github.com/advisories/GHSA-59qp-cfj3-rp64
Type: github-advisory

## Affected
- Go: `github.com/tinfoil-factory/netfoil` — affected >=0 <0.3.0

## Details
### Summary
Potential bypass of domain name filter by crafting a DNS request with multiple questions, with the first question being legitimate.

### Impact
Depends on a local attackers ability to craft multiple questions and the remote DoH server supporting them.

## References
- https://github.com/tinfoil-factory/netfoil/security/advisories/GHSA-59qp-cfj3-rp64
- https://github.com/tinfoil-factory/netfoil
