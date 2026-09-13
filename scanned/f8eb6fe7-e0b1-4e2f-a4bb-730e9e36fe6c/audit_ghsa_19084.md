# [H] CometBFT allows a malicious peer to stall the network by disseminating seemingly valid block parts

## Summary
Severity: High
Advisory: GHSA-r3r4-g7hq-pq4f
CWE: CWE-345
Ecosystem: Go
Published: 2025-02-03
Source: https://github.com/advisories/GHSA-r3r4-g7hq-pq4f
Type: github-advisory

## Affected
- Go: `github.com/cometbft/cometbft` — affected >=1.0.0-alpha.1 <1.0.1
- Go: `github.com/cometbft/cometbft` — affected >=0 <0.38.17

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

```go
type Proof struct {
	Total    int64    `json:"total"`           // Total number of items.
	Index    int64    `json:"index"`           // Index of item to prove.
	LeafHash []byte   `json:"leaf_hash"`       // Hash of item value.
	Aunts    [][]byte `json:"aunts,omitempty"` // Hashes from leaf's sibling to a root's child.
}
```

Note that the total number of leaves in the Merkle tree equals the number of parts in the proposed block. Previously, CometBFT did not validate the `Index` field and specifically that `Part.Index` must be equal to `Part.Proof.Index`. This leads to a condition where, it is possible to use the proof from a different part and CometBFT accept it, even though the proof proves the different part is a piece of the proposed block and not the part that the peer actually sent to us.

This condition is problematic because: 

1. it would disseminate the invalid block part to its neighboring nodes (because it deemed it as correct)
2. it would mark the block part as received and ask the neighboring nodes not to relay it in the future, making it impossible to receive the correct block part.

To address this, CometBFT was patched to verify that `Part.Index` is equal to `Part.Proof.Index`, preventing the above condition.

### Timeline

* January 15, 2025, 12:12pm PST: Issue reported to the Cosmos Bug Bounty program
* January 15, 2025, 12:31pm PST: Issue triaged by Amulet on-call, and distributed to Core team
* January 27, 2025, 11:28pm PST: Core team completes validation of issue
* January 31, 2024, 2:15pm PST: Pre-notification delivered
* February 3rd, 2024, 9:00am UTC+4: Patch made available

This issue was reported by [unknown_feature](https://github.com/unknownfeature) to the Cosmos Bug Bounty Program on HackerOne on January 15, 2025. If you believe you have found a bug in the Interchain Stack or would like to contribute to the program by reporting a bug, please see https://hackerone.com/cosmos.

If you have questions about Interchain security efforts, please reach out to our official communication channel at [security@interchain.io](mailto:security@interchain.io). For more information about the Interchain Foundation’s engagement with Amulet, and to sign up for security notification emails, please see https://github.com/interchainio/security.  

A Github Security Advisory for this issue is available in the CometBFT [repository](https://github.com/cometbft/cometbft/security/advisories/GHSA-r3r4-g7hq-pq4f). For more information about CometBFT, see https://docs.cometbft.com/.

## References
- https://github.com/cometbft/cometbft/security/advisories/GHSA-r3r4-g7hq-pq4f
- https://github.com/cometbft/cometbft/commit/415c0da223bb7694608913f725fa45bd7a7a46bf
- https://github.com/cometbft/cometbft/commit/f943aabc7b9201ea1089ff3381479929435ce424
- https://github.com/cometbft/cometbft
- https://pkg.go.dev/vuln/GO-2025-3443
