# [M] Improper ECIES Public Key Validation in RLPx Handshake

## Summary
Severity: Medium
Chain: Ethereum
Component: ethereum/go-ethereum
CVE: CVE-2026-26315
Published: 2026-02-17
Source: https://github.com/ethereum/go-ethereum/security/advisories/GHSA-m6j8-rg6r-7mv8
Type: github-advisory

## Details
### Impact

Through a flaw in the ECIES cryptography implementation, an attacker may be able to extract bits of the p2p node key.

### Patches

The issue is resolved in the v1.16.9 and v1.17.0 releases of Geth. We recommend rotating the node key after applying the upgrade, which can be done by removing the file `<datadir>/geth/nodekey` before starting Geth.

### Credit

The issue was reported as a public pull request to go-ethereum by @fengjian.
