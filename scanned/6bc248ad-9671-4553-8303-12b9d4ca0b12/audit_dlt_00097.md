# [H] ASA-2025-003: Invalid BitArray handling can lead to network halt

## Summary
Severity: High
Chain: Cosmos
Component: cometbft/cometbft
Published: 2025-10-14
Source: https://github.com/cometbft/cometbft/security/advisories/GHSA-hrhf-2vcr-ghch
Type: github-advisory

## Details
Name: ASA-2025-003: Invalid BitArray handling can lead to network halt
Criticality: High (Considerable Impact; Possible Likelihood per [ACMv1.2](https://github.com/interchainio/security/blob/main/resources/CLASSIFICATION_MATRIX.md))
Affected versions: `<= v0.38.18`, `<= v0.37.15`, and `main` development branches
Affected users: Validators, Full nodes, Users

### Description

A bug was discovered in CometBFT's handling of `BitArray`'s that have a mismatch between the `BitArray`'s expected number of `Elems` for the specified number of `Bits`. Additional validation was added to prevent processing `BitArray`'s in this invalid state, as well as guards to prevent panics on `BitArray` methods if one of these invalid states is processed.

### Impact
`BitArray`'s are present in a number of messages received from peers. When handling these messages, insufficient validation was applied to prevent processing messages the aforementioned invalid state. In the worst case, nodes will gossip messages to peers in an invalid state before processing them themselves, leading to a network halt (instead of only the node receiving the malicious message crashing). 

### Patches

The new CometBFT releases [v0.38.19](https://github.com/cometbft/cometbft/releases/tag/v0.38.19) and [v0.37.16](https://github.com/cometbft/cometbft/releases/tag/v0.37.16) fix this issue.

Unreleased code in the main branch is patched as well.

### Workarounds

If a node is able to identify a malicious peer sending these payloads, they can ban the ip address using common tools like `iptables`.

### Timeline

* October 3, 2025, 11:26am EST: Issue reported to Cosmos Labs via an external team (via their Bug Bounty Program).
* October 3, 2025, 11:59am EST: Issue triaged by core team and core team completes validation of issue.
* October 6, 2025, 11:14pm EST: Issue reported to the Cosmos Bug Bounty Program (by original white hat reporter).
* October 9, 2025, 11:15am EST: Pre-notification delivered.
* October 10, 2025, 11:37am EST: Core team completes patch for the issue.
* October 14, 2025, 11:00am EST: Patch made available.

This issue was reported by @whoismxuse to the Cosmos Bug Bounty Program on HackerOne on October 6, 2025. If you believe you have found a bug in the Cosmos Stack or would like to contribute to the program by reporting a bug, please see https://hackerone.com/cosmos.

If you have questions about Cosmos security efforts, please reach out to our official communication channel at [security@cosmoslabs.io](mailto:security@cosmoslabs.io).

A Github Security Advisory for this issue is available in the CometBFT [repository](https://github.com/cometbft/cometbft/security/advisories/GHSA-hrhf-2vcr-ghch). For more information about CometBFT, see https://docs.cometbft.com/.
