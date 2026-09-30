# [M] Deadline check is not sufficient

## Summary
Severity: Medium
Contest weight: 0.5640
Dataset id: 2825
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The swapBalancer function calls the batchSwap method on the Balancer vault to perform swaps of
assets. The problem is that the passed deadline parameter is hardcoded to block.timestamp.
```solidity
int256[] memory assetDeltas =
IBalancerVault(swapHandlerAddresses.BalancerVault).batchSwap(
IBalancerVault.SwapKind.GIVEN_IN,
swaps,
assets,
funds,
limits,
block.timestamp // deadline
```
The deadline parameter enforces a time limit by which the transaction must be executed otherwise it will
revert. If we take a look at the batSwap source code, we can see the following validation:
```solidity
_require(block.timestamp <= deadline, Errors.SWAP_DEADLINE);
```
Now when the deadline is hardcoded as block.timestamp, the transaction will not revert because the
require statement will always be fulfilled by block.timestamp == block.timestamp.
If the provided transaction fee that is too low for miners to be interested in including the transaction in a
block, the transaction stays pending in the mempool for extended periods, which could be hours, days,
weeks, or even longer.
This could lead to users getting a worse price because a validator can just hold onto the transaction.

## Recommendation
Use a user-supplied deadline instead of block.timestamp.
