# [C] cheqd-node affected by Non-deterministic JSON Unmarshalling of IBC Acknowledgement

## Summary
Severity: Critical
Advisory: GHSA-33cr-m232-xqch
CWE: CWE-502
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-03-11
Source: https://github.com/advisories/GHSA-33cr-m232-xqch
Type: github-advisory

## Affected
- Go: `github.com/cheqd/cheqd-node` — affected >=0 <3.1.7

## Details
# Description

[An issue was discovered in IBC-Go's deserialization of acknowledgements](https://github.com/cosmos/ibc-go/security/advisories/GHSA-jg6f-48ff-5xrw) that results in non-deterministic behavior which can halt a chain. Any user that can open an IBC channel can introduce this state to the chain.

This an upstream dependency used in cheqd-node, rather than a custom module.

## Impact
Could result in a chain halt.

## Patches
Validators, full nodes, and IBC relayers should upgrade to **[cheqd-node v3.1.7](https://github.com/cheqd/cheqd-node/releases/tag/v3.1.7)**. This upgrade does not require a software upgrade proposal on-chain and is meant to be non state-breaking.

## References
See [ASA-2025-004: Non-deterministic JSON Unmarshalling of IBC Acknowledgement can result in a chain halt](https://github.com/cosmos/ibc-go/security/advisories/GHSA-jg6f-48ff-5xrw) upstream on IBC-Go.

## References
- https://github.com/cheqd/cheqd-node/security/advisories/GHSA-33cr-m232-xqch
- https://github.com/cosmos/ibc-go/security/advisories/GHSA-jg6f-48ff-5xrw
- https://github.com/cosmos/ibc-go/commit/59987d52d959dc5876ffd4f307c9b33a52a43748
- https://github.com/cheqd/cheqd-node
- https://pkg.go.dev/vuln/GO-2025-3514
