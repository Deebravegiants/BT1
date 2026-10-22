# [M] AV-3 | Vault Cap Can Be Bypassed

## Summary
Severity: Medium
Contest weight: 0.3928
Dataset id: 20517
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Before depositing funds into the protocol, the deposit functions perform a check to ensure the vault cap will not be exceeded:
```solidity
require(totalAssets() + assets <= previewVaultCap(), "AssetVault: over vault cap");
```

However, the totalAssets() function does not consider the funds that are still pending to be sent into the AggregateVault. As a result, User A can deposit funds that reach the cap but will not be included in the TVL.

User B will then make another deposit, and since the current TVL has not been updated yet, their deposit to AssetVault will also go through. Once both requests are settled, the vault cap will be bypassed.

## Recommendation
Validate the vault cap upon request execution so that it cannot be easily exceeded by a potentially significant amount.
