# [M] checkpoint can be re-entered

## Summary
Severity: Medium
Contest weight: 0.1603
Dataset id: 7195
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Most public functions of Hyperdrive have reentrancy guards but the checkpoint function does not. It can change important contract state like reserves. This can interfere with other functions that don't expect state to change during a _deposit call. For example, the following call StEthHyperdrive.openShort -> _openShort -> _deposit performs a refund that happens in the middle of the openShort function. It then continues execution with the _applyShort function. One could re-enter checkpoint during _deposit to apply a checkpoint, changing the market state. This allows calculating a swap that would violate solvency requirements but can pass as solvency is only checked after _deposit. It is also possible that after the market state is updated in _applyCheckpoint there would be some excess idle to be distributed. If so the curve C is scaled down to C. But when we call _applyOpenShort the inputs are from the deltas calculated when we traded on C and not C which might push our point (z, , y) further to the right (not past the solvency or minimum line but more than the amount it should).

## Recommendation
All calls to _calculateOpenShort and _applyOpenShort should be atomic and the curve C should not change in between. Consider adding reentrancy guards to checkpoint.
