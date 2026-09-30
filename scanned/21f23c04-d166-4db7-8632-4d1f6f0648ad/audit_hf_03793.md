# [M] Inconsistent use of VAULT_ACCOUNT_MIN_TIME in

## Summary
Severity: Medium
Contest weight: 0.4362
Dataset id: 20003
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
There is a considerable difference in implementation behaviour when a vault has yet to mature compared to after vault settlement.
There is some questionable functionality with the following require statement:
acts-v2/contracts/external/actions/VaultAccountAction.sol#L242
File: VaultAccountAction.sol
```solidity
require(vaultAccount.lastUpdateBlockTime + Constants.VAULT_ACCOUNT_MIN_TIME <= block.timestamp)
```
The lastUpdateBlockTime variable is updated in two cases:
• A user enters a vault position, updating the vault state; including lastUpdateBlockTime. This is a proactive measure to prevent users from quickly entering and exiting the vault.
• The vault has matured and as a result, each time vault fees are assessed for a given vault account, lastUpdateBlockTime is updated to block.timestamp after calculating the pro-rated fee for the prime cash vault.
Therefore, before a vault has matured, it is not possible to quickly enter and exit a vault. But after Constants.VAULT_ACCOUNT_MIN_TIME has passed, the user can exit the vault as many times as they like. However, the same does not hold true once a vault has matured. Each time a user exits the vault, they must wait Constants.VAULT_ACCOUNT_MIN_TIME time again to re-exit. This seems like inconsistent behaviour.
The exitVault() function will ultimately affect prime and non-prime vault users differently. It makes sense for the codebase to be written in such a way that functions execute in-line with user expectations.

## Recommendation
It might be worth adding an exception to VaultConfiguration.settleAccountOrAccruePrimeCashFees() so that when vault fees are calculated, lastUpdatedBlockTime is not updated to block.timestamp.
