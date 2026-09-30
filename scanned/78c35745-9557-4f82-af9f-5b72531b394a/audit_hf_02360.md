# [M] Improved Liquidation Logic in PluzAccountManager

## Summary
Severity: Medium
Contest weight: 0.4597
Dataset id: 12788
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Pluz protocol has a core PluzAccountManager contract to oversee the account creation and management. In the process of examining the liquidation logic of an underwater position, we notice current implementation should be improved. In the following, we show the implementation of the related routine, i.e., liquidateCollateral(). This routine has a rather straightforward logic in repaying the debt from the calling user (a.k.a., liquidator) and seizing the collateral from the borrower being liquidated. It comes to our attention that the _lendAsset token is a rebasing one and the repayment funds are directly transferred from the liquidator in term of lendPoolActualAsset (line 271). With that, there is no need to unwrap the _lendAsset at all 1 (line 270). Moreover, this routine can also be improved to have the nonReentrant modifier to block unintended reentrancy attempts. Note other public functions from this PluzAccountManager contract have this nonReentrant modifier consistently applied.
```solidity
function liquidateCollateral(address account, uint256 debtToCover, address liquidationFeeTo) public {
    AccountLib.Health memory health = getAccountHealth(account);
    if (!health.isLiquidatable) revert Errors.AccountHealthy();
    // Mark account liquidatable if it isn't already.
    if (_accountLiquidationStartTime[account] == 0) {
        _accountLiquidationStartTime[account] = block.timestamp;
        emit AccountLiquidationStarted(account);
        this._afterLiquidationStarted(account);
    }
    // The collateral credited to the owner of the Account, not the Account itself.
    address accountOwner = _accountOwnerCache[account];
    uint256 debtAmount = getDebtAmount(account);
    AccountLib.CollateralLiquidation memory _result = _simulateCollateralLiquidation(accountOwner, debtAmount, debtToCover);
    // Transfer collateral to caller and their fee wallet
    _withdrawAssets(accountOwner, msg.sender, _result.collateralAmount - _result.bonusCollateral);
    _withdrawAssets(accountOwner, liquidationFeeTo, _result.bonusCollateral);
    // Transfer debt from sender to account.
    uint256 convertAmount = _convertAmount(_result.actualDebtToLiquidate, IERC20Rebasing(address(_lendAsset)));
    IERC20Rebasing(address(_lendAsset)).unwrap(_result.actualDebtToLiquidate);
    _lendPoolActualAsset.safeTransferFrom(msg.sender, account, convertAmount);
    IAccount(account).repay(_result.actualDebtToLiquidate);
    emit CollateralLiquidation(
        account, _result.collateralAmount, _result.bonusCollateral, _result.actualDebtToLiquidate);
}
```

## Recommendation
Revise the above-mentioned routine to properly liquidate an underwater user position.
