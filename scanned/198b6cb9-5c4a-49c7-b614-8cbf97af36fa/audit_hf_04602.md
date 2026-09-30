# [M] M-35 | VotingPool Incompatible With Non-Standard Tokens

## Summary
Severity: Medium
Contest weight: 0.0562
Dataset id: 22207
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
If the underlying token of a pod is a Fee-on-Transfer token, the accounting when staking in VotingPool would be inaccurate. The balance of tokens after fees should be accounted for instead. Multi-asset pods are also incompatible as _calculateCbrWithDen assumes _asset[0] is the only token in the pod.

## Recommendation
As Peapods is expected to be permissionless and work with all types of tokens, handle such non-standard tokens accordingly.
