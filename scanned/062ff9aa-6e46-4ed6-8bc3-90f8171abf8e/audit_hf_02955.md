# [M] Tokens for one additional period are distributed when they shouldn't be

## Summary
Severity: Medium
Contest weight: 0.5940
Dataset id: 16384
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The BuyAndBurn::distributeDragonXForBurning() function is permissionless, mainly expected to be called by the Auction::_distribute() function. According to the deployment file, the startTimeStamp of the BuyAndBurn.sol contract, will be exactly 1 day after the startTimestamp of the Auction.sol contract. During this time DragonX tokens will be accumulated within the BuyAndBurn contract. However, the implementation of the BuyAndBurn.sol contract distributes funds for one more period than it should.
From the Constants.sol contract we see the following:
```solidity
uint16 constant INTERVAL_TIME = 5 minutes;
uint16 constant INTERVALS_PER_DAY = uint16(24 hours / INTERVAL_TIME);
```
INTERVALS_PER_DAY = 288, so for every 24 hours there should be 288 interval distributions. Consider the following example:
The BuyAndBurn.sol startTimeStamp is set to 2 days and 14 hours.
The DragonX tokens balance of the BuyAndBurn.sol contract is 100_000e18
At 2 days 14 hours + 12 sec the BuyAndBurn::distributeDragonXForBurning() function is called, which will internally call the BuyAndBurn::_intervalUpdate() function.
As we can see from the BuyAndBurn::_calculateIntervals() function:
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
    missedIntervals = _calculateMissedIntervals(timeElapsedSince);
    _lastIntervalNumber = lastIntervalNumber + missedIntervals + 1;
    uint32 currentDay = Time.dayGap(startTimeStamp,
        uint32(block.timestamp));
    uint32 dayOfLastInterval = lastBurnedIntervalStartTimestamp == 0
        ? currentDay
        : Time.dayGap(startTimeStamp,
            lastBurnedIntervalStartTimestamp);
    if (currentDay == dayOfLastInterval) {
        uint256 dailyAllocation = wmul(totalDragonXDistributed,
            getDailyDragonXAllocation());
        uint128 _amountPerInterval = uint128(dailyAllocation /
            INTERVALS_PER_DAY);
        uint128 additionalAmount = _amountPerInterval *
            missedIntervals;
        _totalAmountForInterval = _amountPerInterval +
            additionalAmount;
        //@note - If the last interval was only updated, but not burned add its allocation to the next one.
        uint128 additional = prevInt.amountBurned == 0 ?
            prevInt.amountAllocated : 0;
        if (_totalAmountForInterval + additional >
            _totalAmountForInterval =
    } else {
        _totalAmountForInterval += additional;
```
The missedIntervals will be 0, however, the _totalAmountForInterval will be equal to the distribution for one period.
The dailyAllocation will be 15_000e18
The _amountPerInterval will be ~52e18
The _totalAmountForInterval will be ~52e18
Later on in the BuyAndBurn::_intervalUpdate() function, the lastBurnedIntervalStartTimestamp will be set to the startTimeStamp which is 2 days 14 hours
Now 12 more hours pass, the current block.timestamp is 3 days 2 hours and 12 seconds and the BuyAndBurn::distributeDragonXForBurning() function is called again.
When the BuyAndBurn::_intervalUpdate() function is called, which in turn calls the BuyAndBurn::_calculateIntervals() function internally, we get the following calculations:
The missedIntervals = 143
The _totalAmountForInterval will be ~7_500e18 (this amount is for 144 intervals)
In the BuyAndBurn::_intervalUpdate() function, the lastBurnedIntervalStartTimestamp will be set to 3 days and 2 hours
12 more hours pass and the current block.timestamp is 3 days 14 hours and 12 seconds, the current balance of DragonX tokens of the BuyAndBurn.sol contract is 200_000e18
This time we will enter the else statement of the BuyAndBurn::_calculateIntervals() function:
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
    missedIntervals = _calculateMissedIntervals(timeElapsedSince);
    _lastIntervalNumber = lastIntervalNumber + missedIntervals + 1;
    uint32 currentDay = Time.dayGap(startTimeStamp,
        uint32(block.timestamp));
    uint32 dayOfLastInterval = lastBurnedIntervalStartTimestamp == 0
        ? currentDay
        : Time.dayGap(startTimeStamp,
            lastBurnedIntervalStartTimestamp);
    else {
        uint32 _lastBurnedIntervalStartTimestamp =
            lastBurnedIntervalStartTimestamp;
        uint32 theEndOfTheDay =
            Time.getDayEnd(_lastBurnedIntervalStartTimestamp);
        while (currentDay >= dayOfLastInterval) {
            uint32 end = uint32(Time.blockTs() < theEndOfTheDay ?
                Time.blockTs() : theEndOfTheDay - 1);
            uint32 accumulatedIntervalsForTheDay = (end -
                _lastBurnedIntervalStartTimestamp) / INTERVAL_TIME;
            uint256 diff = balanceOf > _totalAmountForInterval ?
                balanceOf - _totalAmountForInterval : 0;
            //@note - If the day we are looping over the same day as the last interval's use the cached allocation, otherwise use the current balance
            uint256 forAllocation = Time.dayGap(startTimeStamp,
                lastBurnedIntervalStartTimestamp)
                == dayOfLastInterval
                ? totalDragonXDistributed
                : balanceOf >= _totalAmountForInterval + wmul(diff,
                    getDailyDragonXAllocation()) ? diff : 0;
            uint256 dailyAllocation = wmul(forAllocation,
                getDailyDragonXAllocation());
            ///@notice -> minus INTERVAL_TIME minutes since, at the end of the day the new epoch with new allocation
            _lastBurnedIntervalStartTimestamp = theEndOfTheDay -
            INTERVAL_TIME;
            ///@notice -> plus INTERVAL_TIME minutes to flip into the next day
            theEndOfTheDay =
                Time.getDayEnd(_lastBurnedIntervalStartTimestamp + INTERVAL_TIME);
            if (dayOfLastInterval == currentDay) beforeCurrDay =
                _totalAmountForInterval;
            _totalAmountForInterval +=
                uint128((dailyAllocation *
                    accumulatedIntervalsForTheDay) / INTERVALS_PER_DAY);
            dayOfLastInterval++;
            Interval memory prevInt = intervals[lastIntervalNumber];
            //@note - If the last interval was only updated, but not burned add its allocation to the next one.
            uint128 additional = prevInt.amountBurned == 0 ?
                prevInt.amountAllocated : 0;
            if (_totalAmountForInterval + additional >
                _totalAmountForInterval =
        } else {
            _totalAmountForInterval += additional;
```
The missedIntervals will be 143
The theEndOfTheDay will be 3 days and 14 hours
The end will be 3 days and 14 hours - 1 sec
The accumulatedIntervalsForTheDay will be 143
The dailyAllocation will be 15_000e18
The _lastBurnedIntervalStartTimestamp will be 3 days & 14 hours - 5 min
The theEndOfTheDay will be 4 days & 14 hours
The _totalAmountForInterval will be ~7_448e18
When we enter the next while loop iteration we get the following:
The end will be equal to the current block.timestamp which is 3 days & 14 hours & 12 seconds
The accumulatedIntervalsForTheDay will be 1
The diff will be ~192_552e18
The dailyAllocation will be ~28_882e18
The _totalAmountForInterval will be ~7_448e18 + ~100e18 = ~7_548e18
In the BuyAndBurn::_intervalUpdate() function, the lastBurnedIntervalStartTimestamp will be set to 3 days and 14 hours
As can be seen from the above example, a total of 15_100e18 tokens will be distributed(made available for burning) for a period of 1 day, when it should have been only 15_000e18 which is equal to the 288 Intervals that should occur during 24 hours.

## Recommendation
Consider adding a functionality that adds 1 interval(5 mins) to the lastBurnedIntervalStartTimestamp the first time the _intervalUpdate() function is invoked.
