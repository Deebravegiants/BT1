# [M] If a lendingPool is added to the network while already late

## Summary
Severity: Medium
Contest weight: 0.1554
Dataset id: 19919
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
If a lending pool is added to a protection pool, the defaultStateManager sets the currentState to late without setting the late timestamp. This can enable anyone in the network to be able to call the _assessState once more and mark the pool as default.
defaultStateManager uses _assessState function to transfer between states.
However, in case an underlying pool is called by _assessState for the first time when it is added to the protocol. The _assessState function sets the currentState to late without updating the lateTimestamp which will remain zero. The attacker can exploit this to move the pool to the default state where it locks the lending pool and renders it unusable.
While it is checked that when pools are added to the ReferenceLendingPool inside _addReferenceLendingPool that the pools should be in Active state, if in the time between the addition of a pool and the first time call of _assessState the pool goes from Active to Late, this attack can be performed by the attacker.
DefaultStateManager.sol#L370-L375
An attacker can render an underlying lending pool unusable.

## Recommendation
The _assessState should handle the initial setting of the state separately.
