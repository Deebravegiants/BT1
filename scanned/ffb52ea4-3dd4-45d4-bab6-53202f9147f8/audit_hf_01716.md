# [M] M-5 Prohibit _recoverer from being a EOA

## Summary
Severity: Medium
Contest weight: 0.0472
Dataset id: 9357
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
• KintoWallet.sol#L93  
In the current architecture it is not allowed to call KintoWallet directly. Thus, the startRecovery and finishRecovery methods are not available to EOA. Users may mistakenly specify an EOA as recoverer, resulting in an inability to recover it.

## Recommendation
We recommend adding a check that _recoverer is a contract.
