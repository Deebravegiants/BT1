# [H] x402 SDK Security Advisory

## Summary
Severity: High
Advisory: GHSA-qr2g-p6q7-w82m
Ecosystem: Go, PyPI, npm
Published: 2026-03-07
Source: https://github.com/advisories/GHSA-qr2g-p6q7-w82m
Type: github-advisory

## Affected
- npm: `@x402/svm` — affected >=0 <2.6.0
- PyPI: `x402` — affected >=0 <2.3.0
- Go: `github.com/coinbase/x402/go` — affected >=0 <2.5.0

## Details
### Impact

A security vulnerability exists in outdated versions of the x402 SDK.

This vulnerability does not affect users' private keys, smart contracts, or funds.

The issue impacts resource servers accepting payments on Solana when the facilitator is running a vulnerable version of the x402 SDK.

### Who Should Take Action

Facilitators that process payments on Solana must upgrade the x402 SDK to the patched versions listed below.

Clients are not required to upgrade.

Resource servers are not required to upgrade unless they operate their own facilitator (self-facilitate).

### Patches

Please update to the following package versions:
* Npm: @x402/svm >= 2.6.0
* Pypi: x402 >= 2.3.0
* Go: x402 >= 2.5.0

## References
- https://github.com/coinbase/x402/security/advisories/GHSA-qr2g-p6q7-w82m
- https://github.com/x402-foundation/x402/security/advisories/GHSA-qr2g-p6q7-w82m
- https://github.com/coinbase/x402
