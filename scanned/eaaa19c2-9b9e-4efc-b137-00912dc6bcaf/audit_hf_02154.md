# [M] Proper Asset Rebalance For Disabled Target Vaults

## Summary
Severity: Medium
Contest weight: 0.3893
Dataset id: 12062
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In Feeder, the FeedVault contract is an essential one with a number key risk parameters that can be dynamically configured by privileged account, i.e., admin. While examining a specific privileged function toggleTargetVault(), we realize the current handling logic needs to be improved. To elaborate, we show below the related toggleTargetVault() routine. It implements a basic logic in toggling the enable status of the given target vault. However, when a target vault is disabled, the funds allocated to the target vault for investment needs to retrieved back for reallocation. Such reallocation operation is not performed yet.
```solidity
* @dev Toggle enable
```

## Recommendation
Revise the above toggleTargetVault() routine so that the funds are properly re-balanced for all active target vaults.
