# [C] C-03 | borrowedVGas Is Set To 0 Before Subtraction

## Summary
Severity: Critical
Contest weight: 0.0831
Dataset id: 22061
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In closePositionPosition, the vGasAmount should be set to collectedAmount0 - position.borrowVGas. However, position.borrowedVGas is set to 0 before the subtraction. This means that the user's vGas amount is overestimated and allows them to drain the protocol.

## Recommendation
Reset position.borrowedVGas after rather than before the subtraction.
