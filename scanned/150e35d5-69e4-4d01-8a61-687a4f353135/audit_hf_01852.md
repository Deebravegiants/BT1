# [H] H-3 DoS of cooldown

## Summary
Severity: High
Contest weight: 0.1298
Dataset id: 10276
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The checkTransaction function serves as a guard for the BORG_SAFE multisig and checks the call's parameters for it. Currently, this function is publicly accessible, making it possible for any actor to call it. The function resets the last execution timestamp, which affects the cooldown check. Therefore, any actor can front-run any BORG SAFE transaction, causing it to fail and blocking the BORG SAFE:  
• borgCore.sol#L153  
• borgCore.sol#L166.

## Recommendation
We recommend restricting access to this function only from the BORG_SAFE contract.
