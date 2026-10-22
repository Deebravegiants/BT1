# [H] VaultAccountSecondaryDebtShareStorage.maturity

## Summary
Severity: High
Contest weight: 0.9038
Dataset id: 20013
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
VaultAccountSecondaryDebtShareStorage.maturity will be cleared prematurely during liquidation. If both the accountDebtOne and accountDebtTwo of secondary currencies are zero, Notional will consider both debt shares to be cleared to zero, and the maturity will be cleared as well as shown below.

```solidity
function _setAccountMaturity(
    VaultAccountSecondaryDebtShareStorage storage accountStorage,
    int256 accountDebtOne,
    int256 accountDebtTwo,
    uint40 maturity
) private {
    if (accountDebtOne == 0 && accountDebtTwo == 0) {
        // If both debt shares are cleared to zero, clear the maturity as well.
        accountStorage.maturity = 0;
    } else {
        // In all other cases, set the account to the designated maturity
        accountStorage.maturity = maturity;
    }
}
```

VaultLiquidationAction.deleverageAccount function

Within the VaultLiquidationAction.deleverageAccount function, it will call the _reduceAccountDebt function.

Referring to the _reduceAccountDebt function below. Assume that the currencyIndex references a secondary currency. In this case, the else logic in Line 251 will be that only ONE of the prime rates will be set as it assumes that the other prime rate will not be used (Refer to Line 252 - 255). However, this assumption is incorrect.

Assume that the currencyIndex is 1. Then netUnderlyingDebtOne parameter will be set to a non-zero value (depositUnderlyingInternal) at Line 261 while netUnderlyingDebtTwo parameter will be set to zero at Line 262. This is because, in Line 263 of the _reduceAccountDebt function, the pr[0] will be set to the prime rate, while the pr[1] will be zero or empty. It will then proceed to call the VaultSecondaryBorrow.updateAccountSecondaryDebt

```solidity
function _reduceAccountDebt(
    VaultConfig memory vaultConfig,
    VaultState memory vaultState,
    VaultAccount memory vaultAccount,
    PrimeRate memory primeRate,
    uint256 currencyIndex,
    int256 depositUnderlyingInternal,
    bool checkMinBorrow
) private {
    if (currencyIndex == 0) {
        vaultAccount.updateAccountDebt(vaultState, depositUnderlyingInternal, 0);
        vaultState.setVaultState(vaultConfig);
    } else {
        // Only set one of the prime rates, the other prime rate is not used since
        // the net debt amount is set to zero
        PrimeRate[2] memory pr;
        pr[currencyIndex - 1] = primeRate;

        VaultSecondaryBorrow.updateAccountSecondaryDebt(
            vaultConfig,
            vaultAccount.account,
            vaultAccount.maturity,
            currencyIndex == 1 ? depositUnderlyingInternal : 0,
            currencyIndex == 2 ? depositUnderlyingInternal : 0,
            pr,
            checkMinBorrow
        );
    }
}
```

Within the updateAccountSecondaryDebt function, at Line 272, assume that accountStorage.accountDebtTwo is 100. However, since pr[1] is not initialized, the VaultStateLib.readDebtStorageToUnderlying will return a zero value and set the accountDebtTwo to zero.

Assume that the liquidator calls the deleverageAccount function to clear all the debt of the currencyIndex secondary currency. Line 274 will be executed, and accountDebtOne will be set to zero. At Line 301, the _setAccountMaturity will set the accountStorage.maturity = 0, which clears the vault account's maturity.

An important point here is that the liquidator did not clear the accountDebtTwo. Yet, accountDebtTwo became zero in memory during the execution and caused Notional to wrongly assume that both debt shares had been cleared to zero.

```solidity
function updateAccountSecondaryDebt(
    VaultConfig memory vaultConfig,
    address account,
    uint256 maturity,
    int256 netUnderlyingDebtOne,
    int256 netUnderlyingDebtTwo,
    PrimeRate[2] memory pr,
    bool checkMinBorrow
) internal {
    VaultAccountSecondaryDebtShareStorage storage accountStorage =
        LibStorage.getVaultAccountSecondaryDebtShare()[account][vaultConfig.vault];
    // Check maturity
    uint256 accountMaturity = accountStorage.maturity;
    require(accountMaturity == maturity || accountMaturity == 0);

    int256 accountDebtOne =
        VaultStateLib.readDebtStorageToUnderlying(pr[0], maturity, accountStorage.accountDebtOne);

    int256 accountDebtTwo =
        VaultStateLib.readDebtStorageToUnderlying(pr[1], maturity, accountStorage.accountDebtTwo);

    if (netUnderlyingDebtOne != 0) {
        accountDebtOne = accountDebtOne.add(netUnderlyingDebtOne);

        _updateTotalSecondaryDebt(
            vaultConfig, account,
            vaultConfig.secondaryBorrowCurrencies[0], maturity, netUnderlyingDebtOne,
            pr[0]
        );

        accountStorage.accountDebtOne =
            VaultStateLib.calculateDebtStorage(pr[0], maturity, accountDebtOne)
            .neg().toUint().toUint80();
    }

    if (netUnderlyingDebtTwo != 0) {
        accountDebtTwo = accountDebtTwo.add(netUnderlyingDebtTwo);

        _updateTotalSecondaryDebt(
            vaultConfig, account,
            vaultConfig.secondaryBorrowCurrencies[1], maturity, netUnderlyingDebtTwo,
            pr[1]
        );

        accountStorage.accountDebtTwo =
            VaultStateLib.calculateDebtStorage(pr[1], maturity, accountDebtTwo)
            .neg().toUint().toUint80();
    }

    if (checkMinBorrow) {
        // No overflow on negation due to overflow checks above
        require(accountDebtOne == 0 || vaultConfig.minAccountSecondaryBorrow[0] <= -accountDebtOne, "min borrow");
        require(accountDebtTwo == 0 || vaultConfig.minAccountSecondaryBorrow[1] <= -accountDebtTwo, "min borrow");
    }

    _setAccountMaturity(accountStorage, accountDebtOne, accountDebtTwo, maturity.toUint40());
}
```

• maturity and accountDebtOne are zero  
• accountDebtTwo = 100

```solidity
struct VaultAccountSecondaryDebtShareStorage {
    // Maturity for the account's secondary borrows. This is stored separately from
    // the vault account maturity to ensure that we have access to the proper state
    // during a roll borrow position. It should never be allowed to deviate from the
    // vaultAccount.maturity value (unless it is cleared to zero).
    uint40 maturity;
    // Account debt for the first secondary currency in either fCash or pCash denomination
    uint80 accountDebtOne;
    // Account debt for the second secondary currency in either fCash or pCash denomination
    uint80 accountDebtTwo;
}
```

Firstly, it does not make sense to have accountDebtTwo but no maturity in storage, which also means the vault account data is corrupted. Secondly, when maturity is zero, it also means that the vault account did not borrow anything from Notional. Lastly, many vault logic would break since it relies on the maturity value.

VaultLiquidationAction.liquidateVaultCashBalance function

The root cause lies in the implementation of the _reduceAccountDebt function. Since liquidateVaultCashBalance function calls the _reduceAccountDebt function to reduce the debt of the vault account being liquidated, the same issue will occur here.

Any vault logic that relies on the VaultAccountSecondaryDebtShareStorage's maturity value would break since it has been cleared (set to zero). For instance, a vault account cannot be settled anymore as the following settleSecondaryBorrow function will always revert. Since storedMaturity == 0 but accountDebtTwo is not zero, Line 399 below will always revert.

As a result, a vault account with secondary currency debt cannot be settled. This also means that the vault account cannot exit since a vault account needs to be settled before exiting, causing users' assets to be stuck within the protocol.

```solidity
function settleSecondaryBorrow(VaultConfig memory vaultConfig, address account) internal returns (bool) {
    if (!vaultConfig.hasSecondaryBorrows()) return false;

    VaultAccountSecondaryDebtShareStorage storage accountStorage =
        LibStorage.getVaultAccountSecondaryDebtShare()[account][vaultConfig.vault];
    uint256 storedMaturity = accountStorage.maturity;

    int256 accountDebtOne =
        -int256(uint256(accountStorage.accountDebtOne));
    int256 accountDebtTwo =
        -int256(uint256(accountStorage.accountDebtTwo));

    if (storedMaturity == 0) {
        // Handles edge condition where an account is holding vault shares past maturity without
        // any debt position.
        require(accountDebtOne == 0 && accountDebtTwo == 0);
    } else {
```

In addition, the vault account data is corrupted as there is a secondary debt without maturity, which might affect internal accounting and tracking.

## Recommendation
Fetch the prime rate of both secondary currencies because they are both needed within the updateAccountSecondaryDebt function when converting debt storage to underlying.

```solidity
function _reduceAccountDebt(
    VaultConfig memory vaultConfig,
    VaultState memory vaultState,
    VaultAccount memory vaultAccount,
    PrimeRate memory primeRate,
    uint256 currencyIndex,
    int256 depositUnderlyingInternal,
    bool checkMinBorrow
) private {
    if (currencyIndex == 0) {
        vaultAccount.updateAccountDebt(vaultState, depositUnderlyingInternal, 0);
        vaultState.setVaultState(vaultConfig);
    } else {
        // Only set one of the prime rates, the other prime rate is not used since
        // the net debt amount is set to zero
        PrimeRate[2] memory pr;
        pr = VaultSecondaryBorrow.getSecondaryPrimeRateStateful(vaultConfig);

        VaultSecondaryBorrow.updateAccountSecondaryDebt(
            vaultConfig,
            vaultAccount.account,
            vaultAccount.maturity,
            currencyIndex == 1 ? depositUnderlyingInternal : 0,
            currencyIndex == 2 ? depositUnderlyingInternal : 0,
            pr,
            checkMinBorrow
        );
    }
}
```
