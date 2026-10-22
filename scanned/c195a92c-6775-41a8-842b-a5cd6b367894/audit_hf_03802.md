# [M] No minimum borrow size check against sec-

## Summary
Severity: Medium
Contest weight: 0.4451
Dataset id: 20015
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Secondary debts were not checked against the minimum borrow size during exit, which could lead to accounts with insufficient debt becoming insolvent and the protocol incurring bad debts.

```solidity
function _setVaultAccount(
// ...SNIP...
    // An account must maintain a minimum borrow size in order to enter the vault. If the account
    // wants to exit under the minimum borrow size it must fully exit so that we do not have dust
    // accounts that become insolvent.
    if (
        vaultAccount.accountDebtUnderlying.neg() < vaultConfig.minAccountBorrowSize &&
        // During local currency liquidation and settlement, the min borrow check is skipped
        checkMinBorrow
    ) {
        // due to rounding in the
        // vaultSharesToLiquidator calculation
        require(vaultAccount.accountDebtUnderlying == 0 || vaultAccount.vaultShares <= 1, "Min Borrow");
    }
```

A vault account has one primary debt (accountDebtUnderlying) and one or more secondary debts (accountDebtOne and accountDebtTwo).

When a vault account exits the vault, Notional will check that its primary debt (accountDebtUnderlying) meets the minimum borrow size requirement. If a vault account wants to exit under the minimum borrow size, it must fully exit so that we do not have dust accounts that become insolvent. This check is being performed in Line 140 above.

However, this check is not performed against the secondary debts. As a result, it is possible that the secondary debts fall below the minimum borrow size after exiting. Vault accounts with debt below the minimum borrow size are at risk of becoming insolvent, leaving the protocol with bad debts.

## Recommendation
Consider performing a similar check against the secondary debts (accountDebtOne and accountDebtTwo) within the _setVaultAccount function to ensure they do not fall below the minimum borrow size.
