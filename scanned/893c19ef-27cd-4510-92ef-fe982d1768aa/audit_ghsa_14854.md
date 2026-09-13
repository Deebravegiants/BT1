# [M] CometBFT is unstability during blocksync when syncing from malicious peer

## Summary
Severity: Medium
Advisory: GHSA-hg58-rf2h-6rr7
CWE: CWE-610
Ecosystem: Go
Published: 2024-06-28
Source: https://github.com/advisories/GHSA-hg58-rf2h-6rr7
Type: github-advisory

## Affected
- Go: `github.com/cometbft/cometbft` — affected >=0.37.0 <0.37.7
- Go: `github.com/cometbft/cometbft` — affected >=0.38.0 <0.38.8

## Details
**Name**: ASA-2024-008: Instability during blocksync when syncing from malicious peer
**Component**: CometBFT
**Criticality**: Medium ([ACMv1](https://github.com/interchainio/security/blob/main/resources/CLASSIFICATION_MATRIX.md): I:Moderate; L: Possible)
**Affected versions**: < v0.38.7 

# Summary

An issue was identified for nodes syncing on an existing network during blocksync in which a malicious peer could cause the syncing peer to panic, enter into a catastrophic invalid syncing state or get stuck in blocksync mode, never switching to consensus. It is recommended for all clients to adopt this patch so that blocksync functions as expected and is tolerant of malicious peers presenting invalid data in this situation. Nodes that are vulnerable to this state may experience a Denial of Service condition in which syncing will not work as expected when joining a network as a client.

# Recognition

This issue was reported to the Cosmos Bug Bounty Program on HackerOne on 5/01/24 by unknown_feature. If you believe you have found a bug in the Interchain Stack or would like to contribute to the program by reporting a bug, please see https://hackerone.com/cosmos.

If you have questions about Interchain security efforts, please reach out to our official communication channel at [security@interchain.io](mailto:security@interchain.io).

For more information about CometBFT, please see https://docs.cometbft.com/.

For more information about the Interchain Foundation’s engagement with Amulet, please see https://github.com/interchainio/security.

## References
- https://github.com/cometbft/cometbft/security/advisories/GHSA-hg58-rf2h-6rr7
- https://github.com/cometbft/cometbft/commit/07866e11139127e415bd0339ac377b6e6a845533
- https://github.com/cometbft/cometbft/commit/8ba2e4f52d5e626e019501ba6420cc86d5de7857
- https://github.com/cometbft/cometbft
