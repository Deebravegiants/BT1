# [M] Improper random number generation in github.com/coredns/coredns

## Summary
Severity: Medium
Advisory: GHSA-gv9j-4w24-q7vx
CWE: CWE-330
Ecosystem: Go
Published: 2022-03-01
Source: https://github.com/advisories/GHSA-gv9j-4w24-q7vx
Type: github-advisory

## Affected
- Go: `github.com/coredns/coredns` — affected >=0 <1.6.6

## Details
### Impact

CoreDNS before 1.6.6 (using go DNS package < 1.1.25) improperly generates random numbers because math/rand is used. The TXID becomes predictable, leading to response forgeries.

### Patches
The problem has been fixed in 1.6.6+.

### References
- [CVE-2019-19794](https://nvd.nist.gov/vuln/detail/CVE-2019-19794)

### For more information
Please consult [our security guide](https://github.com/coredns/coredns/blob/master/.github/SECURITY.md) for more information regarding our security process.

## References
- https://github.com/coredns/coredns/security/advisories/GHSA-gv9j-4w24-q7vx
- github.com/coredns/coredns
