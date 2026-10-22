# [H] Exiting a validator will not be noticed by the Vault

## Summary
Severity: High
Contest weight: 0.2600
Dataset id: 16237
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Vault has a depositLimit that ensures no more LYX can be deposited when a certain number is reached. Inside deposit, there is the following check: uint256 newTotalDeposits = Math.max(validators * DEPOSIT_AMOUNT, totalStaked + totalUnstaked) + amount; if (newTotalDeposits > depositLimit) { revert DepositLimitExceeded(newTotalDeposits, depositLimit); The newTotalDeposits take the higher number between validators * DEPOSIT_AMOUNT and totalStaked + totalUnstaked, adds the amount, and compares it to the depositLimit. The problem is that when a validator is exited, the validators variable inside the Vault is not decreased as it should be. For example, if 10 validators are registered and after some time 5 of them are exited because of user withdrawals the validators * DEPOSIT_AMOUNT will be still equal to 320 while the totalStaked + totalUnstaked will be much smaller because of funds exiting the Vault. For simplicity, if the depositLimit is set to 320, no more users will be able to deposit LYX even though the funds in the Vault are much less than the limit.

## Recommendation
Consider comparing only totalStaked + totalUnstaked to the depositLimit as this should represent the actual balance related to the Vault. Additionally, consider implementing a mechanism to decrease the validators variable when a validator is exited.
