# [M] **5.2.1 A market could be deprecated but still prevent liquidators to liquidate borrowers if** isLiquidateBor-

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
rowPaused **is** true

**Severity:** Medium Risk

**Context:** aave-v2/MorphoGovernance.sol#L358-L366, compound/MorphoGovernance.sol#L368-L

**Description:** Currently, when a market must be deprecated, Morpho checks that borrowing has been paused
before applying the new value for the flag.

```
function setIsDeprecated(address _poolToken, bool _isDeprecated)
external
onlyOwner
isMarketCreated(_poolToken)
{
if (!marketPauseStatus[_poolToken].isBorrowPaused) revert BorrowNotPaused();
marketPauseStatus[_poolToken].isDeprecated = _isDeprecated;
emit IsDeprecatedSet(_poolToken, _isDeprecated);
}
```
The same check should be done inisLiquidateBorrowPaused, allowing the deprecation of a market only ifisLiq-
uidateBorrowPaused == falseotherwise liquidators would not be able to liquidate borrowers on a deprecated
market.

**Recommendation:** Prevent the deprecation of a market if theisLiquidateBorrowPausedflag is set totrue.

Consider also checking theisDeprecatedflag in thesetIsLiquidateBorrowPausedto prevent pausing the liqui-
dation if the market is deprecated. If Morpho implements the specific behavior should also be aware of the issue
described in"setIsPausedForAllMarketsbypass the check done insetIsBorrowPausedand allow resuming bor-
row on a deprecated market".


**Morpho:** We acknowledge this issue. The reason behind this is the following: given what @MathisGD said, if we
want to be consistent we should prevent pausing the liquidation borrow on a deprecated asset. However, there
might be an issue (we don't know) with the liquidation borrow and the operator would not be able to pause it. For
this reason, we prefer to leave things as it is.

**Spearbit:** Acknowledged.
