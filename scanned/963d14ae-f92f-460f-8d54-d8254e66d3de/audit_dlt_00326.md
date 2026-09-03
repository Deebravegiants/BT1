# [M] ASA-2025-001: Malicious peer can disrupt node's ability to sync via blocksync

## Summary
Severity: Medium
Chain: Cosmos
Component: CometBFT
Source: https://github.com/cometbft/cometbft/security/advisories/GHSA-22qq-3xwm-r5x4
Type: cosmos-asa

## Details
Name: ASA-2025-001: Malicious peer can disrupt node's ability to sync via blocksync
Component: CometBFT
[OUTDATED] Criticality: Medium (Considerable Impact; Possible Likelihood per [ACMv1.2](https://github.com/interchainio/security/blob/main/resources/CLASSIFICATION_MATRIX.md))
**Update of Criticality on 2026-03-06**: We've made a mistake and over-rated the criticality of this bug in our initial triage. We have calibrated our vulnerability rating internally and updated the criticality of this bug to be Informational (Negligible Impact, Possible Likelihood)
Affected versions: <= v0.38.16, v1.0.0
Affected users: Validators, Full nodes

### Impact

A malicious peer may be able to interfere with a node's ability to sync blocks with peers via the blocksync mechanism. 

In the `blocksync` protocol peers send their `base` and `latest` heights when they connect to a new node (`A`), which is syncing to the tip of a network. `base` acts as a lower ground and informs `A` that the peer only has blocks starting from height `base`. `latest` height informs `A` about the latest block in a network. Normally, nodes would only report increasing heights:

```
B: {base: 100, latest: 1000}
B: {base: 100, latest: 1001}
B: {base: 100, latest: 1002}
...
```

If `B` fails to provide the latest block, `B` is removed and the `latest` height (target height) is recalculated based on other nodes `latest` heights.

The existing code hovewer doesn't check for the case where `B` first reports `latest` height `X` and immediately after height `Y`, where `X > Y`. For example:

```
B: {base: 100, latest: 2000}
B: {base: 100, latest: 1001}
B: {base: 100, latest: 1002}
...
```

`A` will be trying to catch up to 2000 indefinitely. Even if `B` disconnects, the `latest` height (target height) won't be recalculated because `A` "doesn't know where 2000" came from per see.

#### Impact Qualification

This condition requires the introduction of malicious code in the full node first reporting a non-existing `latest` height, then reporting lower `latest` height and nodes which are syncing using `blocksync` protocol.

### Patches

_Trimmed to 38 lines — full report: https://github.com/cometbft/cometbft/security/advisories/GHSA-22qq-3xwm-r5x4_
