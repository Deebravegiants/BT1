# [M] M-17 | Accounts Without Debt Stuck In V2

## Summary
Severity: Medium
Contest weight: 0.1209
Dataset id: 2594
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
It is possible for an account to have no debt but both liquid collateral and escrowed entries. This can occur with multiple ways, for example they might paid their debt by burning. With a quick scan we were able to identify good amount of accounts that are in this position, which shows that we can assume there are much more. These accounts are not migratable because of the check in _gatherFromV2 which reverts with NothingToMigrate error. These accounts can not create new debt as well because issuing is stopped. Hence these accounts have to wait for their locks to expire in order to be able to utilize them, until then their tokens will be locked with no utilization.

## Recommendation
Two possible ways to resolve this issue: 1. Create a new function to only migrate locks from V2 to V3. 2. Remove the debtSharesMigrated == 0 check from _gatherFromV2. This can require more changes because debt share value of the user is used in a lot of divisions. Divide by zero's should be prevented by locking the routes that can lead to divide by zero if debt share is 0.
