# [H] ASA-2025-002: Malicious peer can stall network by disseminating seemingly valid block parts

## Summary
Severity: High
Chain: Cosmos
Component: cometbft/cometbft
CWE: Improper Input Validation
Published: 2025-02-03
Source: https://github.com/cometbft/cometbft/security/advisories/GHSA-r3r4-g7hq-pq4f
Type: github-advisory

## Details
Name: ASA-2025-002: Malicious peer can stall network by disseminating seemingly valid block parts
Component: CometBFT
Criticality: High (Catastrophic Impact; Possible Likelihood per [ACMv1.2](https://github.com/interchainio/security/blob/main/resources/CLASSIFICATION_MATRIX.md))
Affected versions: <= v0.38.16, v1.0.0
Affected users: Validators, Full nodes, Users

### Description

A bug was identified in the CometBFT validation of block part indices and the corresponding proof part indices that can lead to incorrect processing and dissemination of invalid parts, which in turn could lead to a network halt. Additional validation was added to prevent this condition from happening.

### Patches

The new CometBFT releases [v1.0.1](https://github.com/cometbft/cometbft/releases/tag/v1.0.1) and [v0.38.17](https://github.com/cometbft/cometbft/releases/tag/v0.38.17) fix this issue.

Unreleased code in the main branch is patched as well.

### Workarounds

There are no known workarounds for this issue. If a node is producing these malicious proofs, the only mitigation is to upgrade CometBFT. After upgrading, the validators then will eventually conclude the correct value.

### Technical Deep-Dive

When the next proposer creates a block, it is split into many block parts (64kB each). Each block part is then disseminated via p2p layer in a gossip fashion. The block part contains the following fields:

```go
type Part struct {
	Index uint32            `json:"index"`
	Bytes cmtbytes.HexBytes `json:"bytes"`
	Proof merkle.Proof      `json:"proof"`
}
```

- `Index` - represents the index of a block part
- `Bytes` - the actual content
- `Proof` - Merkle proof, which allows the receiving node to quickly verify that a `Part` is indeed a piece of the proposed block.

The `Proof` contains the following fields:


_Trimmed to 38 lines — full report: https://github.com/cometbft/cometbft/security/advisories/GHSA-r3r4-g7hq-pq4f_
