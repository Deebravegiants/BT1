# [M] 5.3.9 It is not possible to callexecuteCommitments()for multiple old commits

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Medium Risk

**Context:** poolUpkeep() in LeveragedPool

**Description:** Assuming the pool has not been updated for many update intervals,performUpkeepSinglePool()
can callpoolUpkeep()repeatedly with_boundedIntervals == trueand a bounded amount of gas to fix this
situation.

In this context the following problem occurs:

- In the first run ofpoolUpkeep(),lastPriceTimestampwill be set toblock.timestamp.
- In the next run of poolUpkeep(), processing will stop at require(intervalPassed(),..), because
    block.timestamphasn’t increased.

This means the rest of the commitments won’t be executed byexecuteCommitments()andupdateIntervalId,
which is updated inexecuteCommitments(), will start lagging.


```
function poolUpkeep(..., bool _boundedIntervals, uint256 _numberOfIntervals) external override
,! onlyKeeper {
require(intervalPassed(), "Update interval hasn't passed");// next time lastPriceTimestamp ==
,! block.timestamp
executePriceChange(_oldPrice, _newPrice);// should only to this once (in combination with
,! _boundedIntervals==true)
IPoolCommitter(poolCommitter).executeCommitments(_boundedIntervals, _numberOfIntervals);
lastPriceTimestamp = block.timestamp;// shouldn't update until all executeCommitments() are
,! processed
}
function intervalPassed() public view override returns (bool) {
unchecked {
return block.timestamp >= lastPriceTimestamp + updateInterval;
}
}
}
```
**Recommendation:**

- Redesign the logic withboundedIntervals(see the related issues)
- UpdatelastPriceTimestamponly once all old commitments are processed.
- EnsureexecutePriceChange()is only executed once for a series of old commitments to prevent negative
    side effects.

**Tracer:** As part of PR 392, we have a hardcoded limit to avoid running out of gas, but this also solves the user-
supplied data problems. Let us know if you think this is a valid solution.

**Spearbit:** Acknowledged.
