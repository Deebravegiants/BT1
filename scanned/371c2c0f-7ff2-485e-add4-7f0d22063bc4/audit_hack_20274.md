# [M] 5.3.1 The value oflastExecutionPricefails to update ifpool.poolUpkeep()reverts

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Medium Risk

**Context:** PoolKeeper.sol#L119-L

**Description:** TheperformUpkeepSinglePool()function of thePoolKeepercontract updatesexecutionPrice[]
with the latest price and callspool.poolUpkeep()to process the price difference. However,pool.poolUpkeep()
can revert, for example due to thecheckInvariantsBeforeFunctionmodifier inmintTokens().

Ifpool.poolUpkeep()reverts then the previous price value is lost and the processing will not be accurate. There-
fore, it is safer to store the new price only ifpool.poolUpkeep()has been executed succesfully.

```
function performUpkeepSinglePool(...) public override {
...
int256 lastExecutionPrice = executionPrice[_pool];
executionPrice[_pool] = latestPrice; // previous price can get lost if poolUpkeep() reverts
...
try pool.poolUpkeep(lastExecutionPrice, latestPrice, _boundedIntervals, _numberOfIntervals) {
... // executionPrice[_pool] should be updated here
} catch Error(string memory reason) {
...
}
}
```
**Recommendation:** To prevent losing thelatestPricevalue, theexecutionPrice[_pool]variable should be
updated only ifpoolUpkeep()doesn’t revert.

```
function performUpkeepSinglePool(...) public override {
...
int256 lastExecutionPrice = executionPrice[_pool];
```
- executionPrice[_pool] = latestPrice;
    ...
    try pool.poolUpkeep(lastExecutionPrice, latestPrice, _boundedIntervals, _numberOfIntervals) {
+ executionPrice[_pool] = latestPrice;
    ...
    } catch Error(string memory reason) {
       ...
    }
}

Alternatively, the administration of theexecutionPrices could be done within the calledpoolUpkeep()function of
theLeveragedPoolcontract.

**Tracer:** Valid, fixed in PR 327.

**Spearbit:** Acknowledged.
