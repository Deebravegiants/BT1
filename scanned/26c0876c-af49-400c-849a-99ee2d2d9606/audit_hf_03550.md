# [M] LGR-5 | Potential For Trapped Deposits

## Summary
Severity: Medium
Contest weight: 0.0614
Dataset id: 19352
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the event that the accountDeposit function execution reverts, there is no recourse for the user to recover their deposit in the vault. The accountDeposit function may revert if the AccountDeposit data carries a brokerHash or tokenHash & srcChainId that does not agree with the configuration in the vaultManager contract.

## Recommendation
Consider implementing a method for the user to recover their funds in the event that the cross-chain deposit transaction cannot succeed even upon retry.
