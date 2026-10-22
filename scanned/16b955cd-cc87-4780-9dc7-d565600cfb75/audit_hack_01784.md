# [M] Handle division by 0

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
#### Description
There are a few places in the code where division by zero may occur but isn't handled.

#### Examples
If the vault settles at exactly 0 value with 0 remaining strategy token value, there may be an unhandled division by zero trying to divide claims on the settled assets:


**contracts-v2/contracts/internal/vaults/VaultAccount.sol:L424-L436**
```solidity
int256 settledVaultValue = settlementRate.convertToUnderlying(residualAssetCashBalance)
    .add(totalStrategyTokenValueAtSettlement);

// If the vault is insolvent (meaning residualAssetCashBalance < 0), it is necessarily
// true that totalStrategyTokens == 0 (meaning all tokens were sold in an attempt to
// repay the debt). That means settledVaultValue == residualAssetCashBalance, strategyTokenClaim == 0
// and assetCashClaim == totalAccountValue. Accounts that are still solvent will be paid from the
// reserve, accounts that are insolvent will have a totalAccountValue == 0.
strategyTokenClaim = totalAccountValue.mul(vaultState.totalStrategyTokens.toInt())
    .div(settledVaultValue).toUint();

assetCashClaim = totalAccountValue.mul(residualAssetCashBalance)
    .div(settledVaultValue);
```

If a vault account is entirely insolvent and its `vaultShareValue` is zero, there will be an unhandled division by zero during liquidation:

**contracts-v2/contracts/external/actions/VaultAccountAction.sol:L274-L281**
```solidity
uint256 vaultSharesToLiquidator;
{
    vaultSharesToLiquidator = vaultAccount.tempCashBalance.toUint()
        .mul(vaultConfig.liquidationRate.toUint())
        .mul(vaultAccount.vaultShares)
        .div(vaultShareValue.toUint())
        .div(uint256(Constants.RATE_PRECISION));
}
```

If a vault account's secondary debt is being repaid when there is none, there will be an unhandled division by zero:

**contracts-v2/contracts/internal/vaults/VaultConfiguration.sol:L661-L666**
```solidity
VaultSecondaryBorrowStorage storage balance = 
    LibStorage.getVaultSecondaryBorrow()[vaultConfig.vault][maturity][currencyId];
uint256 totalfCashBorrowed = balance.totalfCashBorrowed;
uint256 totalAccountDebtShares = balance.totalAccountDebtShares;

fCashToLend = debtSharesToRepay.mul(totalfCashBorrowed).div(totalAccountDebtShares).toInt();
```

While these cases may be unlikely today, this code could be reutilized in other circumstances later that could cause reverts and even disrupt operations more frequently. 

#### Recommendation
Handle the cases where the denominator could be zero appropriately.
<!-- Supply advice on how to best fix the problem. -->
