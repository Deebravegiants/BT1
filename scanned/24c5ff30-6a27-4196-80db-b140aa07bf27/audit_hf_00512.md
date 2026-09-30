# [M] M-03 | DoS Via Deposit Before First Epoch

## Summary
Severity: Medium
Contest weight: 0.1044
Dataset id: 1970
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Deposits before the first epoch are possible, with a minimum deposit amount of 1e3. Any pending deposits before the first epoch are utilized to establish the initial liquidity position within the _createNewLiquidityPosition function. This function deducts a dust amount of 1e4 from the deposited collateral amounts. If a user intentionally deposits an amount between 1e3 and 1e4 before the first epoch, and there are no other deposits, the initialization will fail due to underflow at [this line](https://github.com/GuardianAudits/foil-1/blob/5b3416a28dfaa24ba3844e10081e55425d0a286a/packages/protocol/src/vault/Vault.sol#L341).

## Recommendation
Consider setting the minimum deposit amount higher than the dust. Alternatively, keep the codebase unchanged but externally deposit the difference if this situation occurs.
