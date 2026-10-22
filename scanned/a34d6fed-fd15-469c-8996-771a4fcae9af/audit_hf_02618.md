# [M] M-2 Funds locked due to the whitelist

## Summary
Severity: Medium
Contest weight: 0.3741
Dataset id: 14141
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
• LPExternalRequestsManager.sol#L346
```
The onlyAllowedProviders check is applied in LPExternalRequestsManager.withdrawAvailableCollateral(). If a provider is delisted after their request has been added to the processBurns() or completeBurns() operations, they will not be able to withdraw their funds.
This situation can occur if the whitelist has been inactive and is later activated via setWhitelistEnabled().

## Recommendation
We recommend removing the onlyAllowedProviders check in withdrawAvailableCollateral().
