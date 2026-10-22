# [M] Secondary debt dust balances are not trun-

## Summary
Severity: Medium
Contest weight: 0.5878
Dataset id: 20014
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Dust balances in primary debt are truncated toward zero. However, this truncation was not performed against secondary debts.

```solidity
function updateAccountDebt(
// ...SNIP...
    // Truncate dust balances towards zero
    if (0 < vaultState.totalDebtUnderlying && vaultState.totalDebtUnderlying < 10) vaultState.totalDebtUnderlying = 0;
// ...SNIP...
}
```

vaultState.totalDebtUnderlying is primarily used to track the total debt of primary currency. Within the updateAccountDebt function, any dust balance in the vaultState.totalDebtUnderlying is truncated towards zero at the end of the function as shown above.

```solidity
function _updateTotalSecondaryDebt(
    VaultConfig memory vaultConfig,
    address account,
    uint16 currencyId,
    uint256 maturity,
    int256 netUnderlyingDebt,
    PrimeRate memory pr
) private {
    VaultStateStorage storage balance =
        LibStorage.getVaultSecondaryBorrow()
        [vaultConfig.vault][maturity][currencyId];
    int256 totalDebtUnderlying =
        VaultStateLib.readDebtStorageToUnderlying(pr, maturity, balance.totalDebt);

    // Set the new debt underlying to storage
    totalDebtUnderlying = totalDebtUnderlying.add(netUnderlyingDebt);
    VaultStateLib.setTotalDebtStorage(
        balance, pr, vaultConfig, currencyId, maturity,
        totalDebtUnderlying, false // not settled
    );
```

However, this approach was not consistently applied when handling dust balance in secondary debt within the _updateTotalSecondaryDebt function. Within the _updateTotalSecondaryDebt function, the dust balance in secondary debts is not truncated.

The inconsistency in handling dust balances in primary and secondary debt could potentially lead to discrepancies in debt accounting in the protocol, accumulation of dust, and result in unforeseen consequences.

## Recommendation
Consider truncating dust balance in secondary debt within the _updateTotalSecondaryDebt function similar to what has been done for primary debt.
