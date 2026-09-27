# [M] Go Ethereum Improperly Validates the ECIES Public Key in RLPx Handshake

## Summary
Severity: Medium
Advisory: GHSA-m6j8-rg6r-7mv8
CVE: CVE-2026-26315
CWE: CWE-203
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-02-18
Source: https://github.com/advisories/GHSA-m6j8-rg6r-7mv8
Type: github-advisory

## Affected
- Go: `github.com/ethereum/go-ethereum` — affected >=0 <1.16.9

## Details
### Impact

Through a flaw in the ECIES cryptography implementation, an attacker may be able to extract bits of the p2p node key.

### Patches

The issue is resolved in the v1.16.9 and v1.17.0 releases of Geth. We recommend rotating the node key after applying the upgrade, which can be done by removing the file `<datadir>/geth/nodekey` before starting Geth.

### Credit

The issue was reported as a public pull request to go-ethereum by @fengjian.

## References
- https://github.com/ethereum/go-ethereum/security/advisories/GHSA-m6j8-rg6r-7mv8
- https://nvd.nist.gov/vuln/detail/CVE-2026-26315
- https://github.com/ethereum/go-ethereum/pull/33669
- https://github.com/ethereum/go-ethereum/commit/46bee92f9e64c0a06a12586a5d21cffc49d1ba8e
- https://github.com/ethereum/go-ethereum
- https://github.com/ethereum/go-ethereum/releases/tag/v1.16.9
- https://pkg.go.dev/vuln/GO-2026-4511
