# [M] LenderActions's moveQuoteToken can create

## Summary
Severity: Medium
Contest weight: 0.2598
Dataset id: 20082
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
moveQuoteToken() doesn't ensure that pool debt is less than deposits after operation, while unutilized deposit fee can reduce total deposits as a result of the move.
Unutilized deposit fee can create a poolState_.debt > Deposits.treeSum(deposits_) state, which isn't controlled for in moveQuoteToken().
Pool can enter technical corner case when LUP is actually lower than HTP, numerically it will not be the case due to bounded nature of LUP calculation.
This breaks the core logic of the pool with the corresponding material miscalculations, but has low probability, so setting the severity to be medium.
moveQuoteToken() can reduce overall deposits due to unutilized deposit fee incurred:
external/LenderActions.sol#L285-L289
```
lup_ = Deposits.getLup(deposits_, poolState_.debt);
// apply unutilized deposit fee if quote token is moved from above the LUP to below the LUP
if (vars.fromBucketPrice >= lup_ && vars.toBucketPrice < lup_) {
    movedAmount_ = Maths.wmul(movedAmount_, Maths.WAD - _depositFeeRate(poolState_.rate));
}
```
But debt < deposits state aren't controlled for:
external/LenderActions.sol#L311-L312
```
// check loan book's htp against new lup, revert if move drives LUP below HTP
if (params_.fromIndex < params_.toIndex && vars.htp > lup_) revert LUPBelowHTP();
```
As it's done in removeQuoteToken(), where it is LUP < HTP || poolState_.debt > Deposits.treeSum(deposits_):
external/LenderActions.sol#L413-L425
```
lup_ = Deposits.getLup(deposits_, poolState_.debt);
uint256 htp = Maths.wmul(params_.thresholdPrice, poolState_.inflator);
if (
    // check loan book's htp doesn't exceed new lup
    htp > lup_
    ||
    // ensure that pool debt < deposits after removal
    // this can happen if lup and htp are less than min bucket price and htp > lup (since LUP is capped at min bucket price)
    (poolState_.debt != 0 && poolState_.debt > Deposits.treeSum(deposits_))
) revert LUPBelowHTP();
```
LUP is being bounded by deposits tree, i.e. the calculation assumes that total debt (the amount whose index is being located) is lower than total deposits (the tree where it is being located):
internal/Deposits.sol#L411-L422
```
/**
 * @dev Returns the price at which the sum of deposits is greater than or
 * equal to `debt_`.
 * @dev `debt_` must be less than or equal to the total deposits.
 *
 * @param deposits_ Deposits state struct.
 * @param debt_ The debt amount to calculate `LUP` for.
 * @return The price at which the sum of deposits reaches debt_.
 */
function getLup(
    DepositsState storage deposits_,
    uint256 debt_
) internal view returns (uint256) {
    return _priceAt(findIndexOfSum(deposits_, debt_));
}
```

## Recommendation
Consider adding the (poolState_.debt != 0 && poolState_.debt > Deposits.treeSum(deposits_)) logic to moveQuoteToken():
external/LenderActions.sol#L311-L312
```
// check loan book's htp against new lup, revert if move drives LUP below HTP
if (params_.fromIndex < params_.toIndex && (vars.htp > lup_ || (poolState_.debt != 0 && poolState_.debt > Deposits.treeSum(deposits_)))) revert LUPBelowHTP();
```
The same approach can be added to HTP check in the kickWithDeposit() case.
