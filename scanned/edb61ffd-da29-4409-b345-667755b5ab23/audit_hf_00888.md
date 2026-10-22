# [M] Incorrect debt calculation for BrimeDen

## Summary
Severity: Medium
Contest weight: 0.6957
Dataset id: 2644
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
Whenever calculate ICR in DenManager instance, getCurrentICR will be called.
function getCurrentICR(address _borrower, uint256 _price) public view returns (uint256) {
    (uint256 currentCollateral, uint256 currentDebt) = getDenCollAndDebt(_borrower);
    uint256 ICR = BeraborrowMath._computeCR(currentCollateral, currentDebt, _price);
    return ICR;
}
In getDenCollAndDebt in DenManager.sol, it will call getEntireDebtAndColl function.
But in getEntireDebtAndColl function, it does not check borrower is brimeDen.
function getEntireDebtAndColl(
    address _borrower
) public view returns (uint256 debt, uint256 coll, uint256 pendingDebtReward, uint256 pendingCollateralReward) {
    Den storage t = Dens[_borrower];
    debt = t.debt;
    coll = t.coll;
    (pendingCollateralReward, pendingDebtReward) = getPendingCollAndDebtRewards(_borrower);

    // Accrued den interest for correct liquidation values. This assumes the index to be updated.

    uint256 denInterestIndex = t.activeInterestIndex;
    if (denInterestIndex > 0) {
        (uint256 currentIndex, ) = _calculateInterestIndex();
        debt = (debt * currentIndex) / denInterestIndex;
    }
    debt = debt + pendingDebtReward;
    coll = coll + pendingCollateralReward;
}
```
But BrimeDen does not pay any interest. This miscalculation will cause BrimeDen's ICR value as lower. (ICR = coll / debt)
When BrimeDen holds debt within a DenManager, an incorrect calculation of BrimeDen's ICR will gradually decrease over time. This issue can lead to an unexpected liquidation in the LiquidationManager.
```solidity
function liquidateDens(IDenManager denManager, uint256 maxDensToLiquidate, uint256 maxICR, address liquidator) public {
    ...
    uint ICR = denManager.getCurrentICR(account, denManagerValues.price);
    uint applicableMCR = _getApplicableMCR(ICR, account, denManagerValues);
    if (ICR > maxICR) {
        ...
    }
    if (ICR <= _LSP_CR_LIMIT) {
        singleLiquidation = _liquidateWithoutSP(denManager, account);
        _applyLiquidationValuesToTotals(totals, singleLiquidation);
    } else if (ICR < applicableMCR) {
        singleLiquidation = _liquidateNormalMode(
            denManager,
            account,
            debtInStabPool,
            denManagerValues.sunsetting
        );
        debtInStabPool -= singleLiquidation.debtToOffset;
        _applyLiquidationValuesToTotals(totals, singleLiquidation);
    } else break; // break if the loop reaches a Den with ICR >= MCR
}
```

## Recommendation
```solidity
function getEntireDebtAndColl(
    address _borrower
) public view returns (uint256 debt, uint256 coll, uint256 pendingDebtReward, uint256 pendingCollateralReward) {
    ...
    // Accrued den interest for correct liquidation values. This assumes the index to be updated.

    uint256 denInterestIndex = t.activeInterestIndex;
    if (denInterestIndex > 0 && _borrower != brimeDen) {
        (uint256 currentIndex, ) = _calculateInterestIndex();
        debt = (debt * currentIndex) / denInterestIndex;
    }
    debt = debt + pendingDebtReward;
    coll = coll + pendingCollateralReward;
}
```
