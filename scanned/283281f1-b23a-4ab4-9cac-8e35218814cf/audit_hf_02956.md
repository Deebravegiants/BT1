# [M] BuyAndBurn will allocate more tokens than it should if the first interval update happens after more than day

## Summary
Severity: Medium
Contest weight: 0.5934
Dataset id: 16385
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
If the first interval update happens more than a day after the start time, the elapsed time will count as the same day no matter how long it is.
Meaning, if the update happens 48 hours after the start, it'll allocate 15% of the initial DragonX deposit twice, so 30% in total.
Here's a PoC:
```solidity
function test_allocates_more_than_it_should() public {
    // This test shows how the `_calculateIntervals` function sets the `_lastBurnedIntervalStartTimestamp` to the end of the day
    // even if the current timestamp is in the middle of the day
    // setup
    MockERC20 dragonX = new MockERC20("DragonX", "DRGNX");
    // start time to is beginning of the current day
    uint32 startTime = uint32(1735135200) / 1 days * 1 days;
    VyperBoostBuyAndBurn bnb = new VyperBoostBuyAndBurn(startTime,
    vm.startPrank(user);
    bnb.distributeDragonXForBurning(100e18);
    vm.stopPrank();
    // we warp 48 hours into the future
    // so we'd expect the total allocated amount to be:
    // first day:
    // 100e18 * 15% = 15e18
    // second day:
    // 85e18 * 15% = 12.75e18
    // total allocation = 15e18 + 12.75e18 = 27.75e18
    vm.warp(startTime + 48 hours);
    vm.prank(user);
    bnb.distributeDragonXForBurning(1);
    (uint128 allocated,) = bnb.intervals(bnb.lastIntervalNumber());
    // will fail
    // 30052083333333333141 != 27750000000000000000
    assertEq(allocated, 27.75e18);
```
The issue is that _calculateIntervals() will calculate dayOfLastInterval as currentDay if lastBurnedIntervalTimestamp == 0.
```solidity
function _calculateIntervals(uint256 timeElapsedSince)
    internal
    view
    returns (
        uint32 _lastIntervalNumber,
        uint128 _totalAmountForInterval,
        uint16 missedIntervals,
        uint256 beforeCurrDay
    )
{
    uint32 currentDay = Time.dayGap(startTimeStamp,
        uint32(block.timestamp));
    uint32 dayOfLastInterval = lastBurnedIntervalStartTimestamp == 0
        ? currentDay
        : Time.dayGap(startTimeStamp,
            lastBurnedIntervalStartTimestamp);
```

## Recommendation
If lastBurnedIntervalTimestamp == 0, dayOfLastInterval should be Time.dayGap(startTimeStamp, startTimestamp).
