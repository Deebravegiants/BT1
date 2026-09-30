# [M] M-02 | Outdated Anchor Tick Used In canBump

## Summary
Severity: Medium
Contest weight: 0.0840
Dataset id: 2212
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The canBump function uses an outdated anchorTick which has not been updated to reflect the current price which the protocol is rebalancing for. As a result the capacity calculations for the Anchor range are not accurate to what the capacity will actually be after the rebalance. This will often result in bumping when bumps should not occur, which will often prevent a rebalance from occurring since the final capacity invariant cannot be held. Or, more rarely, not allowing bumps to occur when they ought to be.

## Recommendation
Consider updating the anchorTick to the latest that will be used in the rebalance.
