# [M] ASA-2024-009: State syncing validator from malicious node may lead to a chain split

## Summary
Severity: Medium
Chain: Cosmos
Component: cometbft/cometbft
Published: 2024-09-03
Source: https://github.com/cometbft/cometbft/security/advisories/GHSA-g5xx-c4hv-9ccc
Type: github-advisory

## Details
**Name**: ASA-2024-009: State syncing validator from malicious node may lead to a chain split
**Component**: CometBFT
**Criticality**: Medium ([ACMv1.2](https://github.com/interchainio/security/blob/main/resources/CLASSIFICATION_MATRIX.md): I:Moderate; L: Possible)
**Affected versions**: >= 0.34.0, <= 0.34.33, >=0.37.0, <= 0.37.10, >= 0.38.0, <= 0.38.11

### Summary

The state sync protocol retrieves a snapshot of the application and installs it in a fresh node. In order for this node to be ready to run consensus and block sync from the installed snapshot height, we also need to install a valid `State` in the node, which is the starting state from which it is able to validate new blocks and append them to the blockchain.

The `State` object used by state sync is computed using the light client protocol, which retrieves information about committed blocks from at least two RPC endpoints. The light client protocol performs several state validations and, in particular, compares the state provided by different RPC endpoints, looking for inconsistencies.

The `State` object contains, among other fields, a `Validators` field which stores the current validator set. A validator set is a list of validator addresses, public keys and associated voting powers, one per validator. It also stores, for historical reasons, the state of the proposer selection algorithm, in the form of the `ProposerPriority` field associated with each `Validator`.

While the light client is able to validate the `ValidatorSet` retrieved from RPC endpoints, this validation does not include the `ProposerPriority` field associated with each `Validator`. As a result, when state sync adopts RPC endpoints that, for unknown reasons, provide an invalid state of the proposer selection algorithm, the node will not be able to properly run the consensus protocol, as their local view of which validator is the proposer of a given round and height will disagree with the views of the correct validators. If an increasing number of validators state sync using RPC endpoints with invalid states, the network eventually halts.

### Patches

Release versions 0.34.34, 0.37.11, and 0.38.12 include a patch to address this issue.

In the patched versions, the light client protocol compares the `ProposerPriority` fields of the `ValidatorSet` instances retrieved from the RPC endpoints configured for state sync. If they differ, the computed `State` object is considered invalid and state sync will fail with an error.

### Workarounds

The issue is observed when validators run state sync using RPC nodes that are malicious or report invalid states for the proposer selection algorithm.

It is worth noting that non-malicious nodes running upstream software should never report an invalid state for the proposer selection algorithm. This situation may result from the adoption of nodes with customized code or which had their state, stored in local databases, manually updated.

When the network public's RPC endpoints have an invalid state for the proposer election algorithm, there, new validators should refrain from using state sync for bootstrapping or be sure that they configure for state sync RPC endpoints with a valid state of the proposer election algorithm.

A validator with an invalid state for the proposer selection algorithm will reject most of the proposed blocks and will have the network rejecting blocks it has proposed.  It is also possible to manually compare the state of the proposer election algorithm of nodes by comparing the outputs of the `/validators?height=_`  RPC endpoints. The outputs must fully match, including the ProposerPriority field associated with each validator. 


### References

* [State Sync documentation](https://docs.cometbft.com/v0.38/core/state-sync)

This issue was reported to the Cosmos Bug Bounty Program on HackerOne on 12/08/24. If you believe you have found a bug in the Interchain Stack or would like to contribute to the program by reporting a bug, please see [https://hackerone.com/cosmos](https://hackerone.com/cosmos).


_Trimmed to 38 lines — full report: https://github.com/cometbft/cometbft/security/advisories/GHSA-g5xx-c4hv-9ccc_
