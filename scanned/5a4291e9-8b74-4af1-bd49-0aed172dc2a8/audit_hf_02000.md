# [H] H-3 Possible ddos of an expiration time

## Summary
Severity: High
Contest weight: 0.1116
Dataset id: 11273
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The addEth function can be called by anyone with 1 wei for any client which will lead to an increased expiration for the client P2pOrgUnlimitedEthDepositor.sol#L88. This can be used by a malicious user to postpone the refund call by the client. Also, expiration can be reset after the reject P2pOrgUnlimitedEthDepositor.sol#L113.

## Recommendation
We recommend reconsidering access rights for the addEth function and allowing it to be called only by the client. Also, we recommend blocking new deposits after the reject call.
