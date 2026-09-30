# [M] Revised EUSD Amount to Mint in _mintToTreasury()

## Summary
Severity: Medium
Contest weight: 0.4607
Dataset id: 12010
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the ERD protocol, the trove owner has to pay a low interest for the trove debt. The interest that is accumulated by a trove from the last operation to the present will be minted to the treasury. The interest is charged based on the borrowing rate. While reviewing the calculation of the repaid interest that will be minted to the treasury, we notice it is wrongly divided by the newLiquidityIndex. In the following, we show the related code snippet of the TroveLogic::_mintToTreasury() routine, which is used to calculate the accumulated interest amount for the scaledDebt when the borrow index changes from previousBorrowIndex to newBorrowIndex. Then the accumulated interest amount is scaled by dividing the newLiquidityIndex (line 185), and the result is used as the USDE amount to be minted to the treasury. However, we notice the EUSDToken contract implements a standard ERC20 which has no special processing for the liquidityIndex. As a result, the treasury actually receives a scaled token balance which may be less than the minted amount. Our analysis shows that we can directly use the accumulated interest amount as the USDE amount to be minted to the treasury.
```solidity
function _mintToTreasury(
    DataTypes.TroveData storage trove,
    uint256 scaledDebt,
    uint256 previousBorrowIndex,
    uint256 newLiquidityIndex,
    uint256 newBorrowIndex
) internal {
    MintToTreasuryLocalVars memory vars;
    // calculate the last principal variable debt
    vars.previousDebt = scaledDebt.rayMul(previousBorrowIndex);
    // calculate the new total supply after accumulation of the index
    vars.currentDebt = scaledDebt.rayMul(newBorrowIndex);
    // debt accrued is the sum of the current debt minus the sum of the debt at the last update
    vars.totalDebtAccrued = vars.currentDebt.sub(vars.previousDebt);
    vars.amountToMint = vars.totalDebtAccrued.rayDiv(newLiquidityIndex);
    if (vars.amountToMint != 0) {
        IEUSDToken(trove.eusdTokenAddress).mintToTreasury(
            vars.amountToMint,
            trove.factor
        );
    }
}
```

## Recommendation
Remove the division by the newLiquidityIndex and use the accumulated interest amount as the USDE amount to be minted to the treasury.
