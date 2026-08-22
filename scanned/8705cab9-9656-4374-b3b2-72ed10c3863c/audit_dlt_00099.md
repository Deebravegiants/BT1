# [H] ASA-2024-011: Vote Extensions: Panic when receiving a Pre-commit with an invalid data

## Summary
Severity: High
Chain: Cosmos
Component: cometbft/cometbft
CWE: Improper Validation of Array Index
Published: 2024-11-06
Source: https://github.com/cometbft/cometbft/security/advisories/GHSA-p7mv-53f2-4cwj
Type: github-advisory

## Details
Name: ASA-2024-011: Vote Extensions: Panic when receiving a Pre-commit with an invalid data
Component: CometBFT
Criticality: High (Considerable Impact, and Possible Likelihood per [ACMv1.2](https://github.com/interchainio/security/blob/main/resources/CLASSIFICATION_MATRIX.md))
Affected versions: `>= 0.38.x`, unreleased `v1.x` and `main` development branches
Affected users: Chain Builders + Maintainers, Validators

### Impact

A CometBFT node running in a network with [vote extensions][abci-spec] enabled could produce an invalid `Vote` message and send it to its peers. The invalid field of the `Vote` message is the `ValidatorIndex`, which identifies the sender in the `ValidatorSet` running that height of consensus. This field is ordinarily verified in the processing of `Vote` messages, but it turns out that in the case of a `Vote` message of type `Precommit` and for a non-`nil` `BlockID`, [a logic was introduced](https://github.com/cometbft/cometbft/blame/46621a87064b2ae235e122e66d9b22417b3aa35e/internal/consensus/state.go#L2357-L2364) before this ordinary verification to handle the attached vote extension. This introduced logic (not present in releases prior to `0.38.x`) does not double-check the validity of the `ValidatorIndex` field. The result is a panic in the execution of the node receiving and processing such message.

#### Impact Qualification
This condition requires the introduction of malicious code in the full node sending this `Vote` message to its peers. Namely, nodes running upstream code cannot produce invalid `Vote` messages, with non-existing `ValidatorIndex`. Moreover, networks utilizing default behavior, where vote extensions are not enabled, are not affected by this issue.

### Patches

The new CometBFT release [`v0.38.15`][v0.38.15] fixes this issue.

Unreleased code in the `main` and `v1.x` branches, and experimental code in the `v0.38-experimental` and `v1.x-experimental` branches are patched as well.

### Workarounds

When the consensus code panics after receiving an invalid `Vote` message, the operator can identify the peer from which that message was received. This may require increasing the logging level of the `consensus` module. This peer can then be subsequently banned at the p2p layer as a temporary mitigation.  

### References

- [ABCI spec][abci-spec], in particular the operation of vote extensions
- [Patched v0.38 release][v0.38.15]

[abci-spec]: https://docs.cometbft.com/v0.38/spec/abci/abci++_basic_concepts
[v0.38.15]: https://github.com/cometbft/cometbft/releases/tag/v0.38.15

### Timeline

* October 21, 2024, 3:26pm PST: Issue reported to the Cosmos Bug Bounty program
* October 21, 2024, 3:41pm PST: Issue triaged by Amulet on-call, and distributed to Core team
* October 29, 2024, 11:35pm PST: Core team completes validation of issue
* October 30, 2024, 3:33am PST: Core team completes patch for issue
* October 30, 2024, 5:09am PST: Amulet creates coordination plan; schedule for distribution

_Trimmed to 38 lines — full report: https://github.com/cometbft/cometbft/security/advisories/GHSA-p7mv-53f2-4cwj_
