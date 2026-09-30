# [C] C-4 Incorrect accounting of commissions

## Summary
Severity: Critical
Contest weight: 0.1614
Dataset id: 16426
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the OnchainLOB.sol#L261 function, the total_commission value is accounted for twice: once as the
commission and once as the token_y value of the trader. This duplication can lead to incorrect commission
accounting and potential contract malfunction due to mismatched accounted and actual balances. Additionally,
it may allow the market maker account to exploit the commission system for profit.
This issue is rated as critical severity as it may lead to malfunction due to contract state inconsistency and
enable the market maker to gain undesired profit.

## Recommendation
We recommend addressing the commission accounting error in the placeOrder function to prevent
discrepancies in balance accounts and potential exploitation for profit.
