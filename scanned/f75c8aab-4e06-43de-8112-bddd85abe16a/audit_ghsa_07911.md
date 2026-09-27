# [H] Go Ethereum affected by DoS via malicious p2p message

## Summary
Severity: High
Advisory: GHSA-2gjw-fg97-vg3r
CVE: CVE-2026-26314
CWE: CWE-20
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-02-18
Source: https://github.com/advisories/GHSA-2gjw-fg97-vg3r
Type: github-advisory

## Affected
- Go: `github.com/ethereum/go-ethereum` — affected >=0 <1.16.9

## Details
### Impact

A vulnerable node can be forced to shutdown/crash using a specially crafted message.
More details to be released later.

### Patches

The problem is resolved in the v1.16.9 and v1.17.0 releases of Geth.

### Credit

This issue was reported to the Ethereum Foundation Bug Bounty Program by Waleed Ahmed from vulsight.com

## References
- https://github.com/ethereum/go-ethereum/security/advisories/GHSA-2gjw-fg97-vg3r
- https://nvd.nist.gov/vuln/detail/CVE-2026-26314
- https://github.com/ethereum/go-ethereum/commit/895a8597cb16c02203e38707ed2d1da5c500fe60
- https://github.com/ethereum/go-ethereum
- https://github.com/ethereum/go-ethereum/releases/tag/v1.16.9
- https://pkg.go.dev/vuln/GO-2026-4507
