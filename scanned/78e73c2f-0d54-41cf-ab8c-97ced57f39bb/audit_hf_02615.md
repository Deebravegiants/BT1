# [M] M-2 Funds Locked Due to the Whitelist

## Summary
Severity: Medium
Contest weight: 0.3703
Dataset id: 14126
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
• ExternalRequestsManagerBetaV1.sol#L209
• ExternalRequestsManagerBetaV1.sol#L148
```
The onlyAllowedProviders check is applied in cancel operations. If a provider gets delisted after creating a pending request, they won't be able to cancel it.
This situation may arise when the whitelist was inactive and then got activated via setWhitelistEnabled().

## Recommendation
We recommend removing the onlyAllowedProviders check from cancelMint() and cancelBurn().
