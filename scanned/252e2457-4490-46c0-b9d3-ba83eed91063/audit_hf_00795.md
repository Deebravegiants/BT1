# [H] H-16 | Pool Initialized Multiple Times

## Summary
Severity: High
Contest weight: 0.2560
Dataset id: 2531
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The initializePool function allows users to initialize a new pool, which users can then deposit the pool's assets into as well as access other functionalities. The initializePool function enforces a check to ensure that an already initialized pool can’t be reinitialized, as this would reset the pool's totalAssets and totalBorrows back to zero, wiping out all previous users' deposits and debt.
This check is done by ensuring that ownerOf[poolId] is zero, which implies the newly created pool does not currently exist. The problem is that the initializePool function allows the owner address to be set to zero. Therefore, a pool could be created with the ownerOf[poolId] as address zero, and since this check is used to ensure a pool is not being reinitialized, this will be bypassed in this case, and the pool can be reinitialized, resetting all values.

## Proof of Concept
https://github.com/GuardianAudits/sentiment-team-2/blob/POC_INITIALIZE_MULTIPLE_TIMES/test/guardian/pocs/initializeMultipleTimes.t.sol

## Recommendation
Since the zero address is used as a check to ensure a pool ID does not already exist in the initializePool function, restrict users from being able to set the owner parameter as the zero address to avoid the problem above.
