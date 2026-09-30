# [C] TradableMarginHandler: can't perform liquidations

## Summary
Severity: Critical
Contest weight: 0.6158
Dataset id: 16120
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The attemptLiquidation() function of the TradableMarginHandler contract reverts if the position is liquidatable, leading to positions impossible to liquidate. This happens since there is an accounting underflow error on line 231 if the following condition is verified: marginBalance + (collateralAmount - protocolPercentOfCollateral) <= tradingFeesAccumulated. The issue is that this is the main condition to check if a position is liquidatable, i.e. the majority of the time, a position is liquidatable exactly because this condition is true, but this condition also prevents liquidations since the call to attemptLiquidation() will revert.
For clarification, take a look at the following code (a simplification of the logic in the TradableMarginHandler):
```solidity
contract test_liquidation {
    uint256 marginBalance = 100;
    uint256 collateralAmount = 200;
    uint256 protocolPercentOfCollateral = 20;
    uint256 tradingFeesAccumulated = 300;
    uint256 user_reserveBalance = 1000;
    function isPositionLiquidatable() view public returns(bool) { // returns true
        return marginBalance + (collateralAmount - protocolPercentOfCollateral) <= tradingFeesAccumulated;
    }
    function attemptLiquidation() public { // calls revert
        if(!isPositionLiquidatable()) return;
        uint256 totalAmountOwed = tradingFeesAccumulated + protocolPercentOfCollateral;
        user_reserveBalance += marginBalance + collateralAmount - totalAmountOwed; // underflows
    }
}
```
Under these conditions, all calls to attemptLiquidation() will revert.

## Recommendation
Use ints instead of uints, allowing for negative values to be incremented. In alternative, check if the increment to user_reserveBalance is positive or negative and perform addition or subtraction accordingly. A liquidation scenario similar to this one should also be included in the tests.
