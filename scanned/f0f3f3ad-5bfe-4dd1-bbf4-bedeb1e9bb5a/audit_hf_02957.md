# [M] Different amounts of tokens will be distributed per interval, depending on how often the _intervalUpdate() function is invoked

## Summary
Severity: Medium
Contest weight: 0.2519
Dataset id: 16386
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The BuyAndBurn::distributeDragonXForBurning() function is permissionless, mainly expected to be called by the Auction::_distribute() function. However, depending on how often the _intervalUpdate() function is invoked, the dailyAllocation of DragonX token for each new day will be different.
According to the deployment file, the startTimeStamp of the BuyAndBurn.sol contract, will be exactly 1 day after the startTimestamp of the Auction.sol contract.
Consider the following example:
The BuyAndBurn.sol startTimeStamp is set to 2 days and 14 hours.
The DragonX tokens balance of the BuyAndBurn.sol contract is 100_000e18
At 2 days 14 hours + 12 sec the BuyAndBurn::distributeDragonXForBurning() function is called, which will internally call the BuyAndBurn::_intervalUpdate() function.
We will get the following calculations from the BuyAndBurn::_calculateIntervals() function:
- The missedIntervals will be 0, however, the _totalAmountForInterval will be equal to the distribution for one period.
- The dailyAllocation will be 15_000e18
- The _amountPerInterval will be ~52e18
- The _totalAmountForInterval will be ~52e18
- Later on in the BuyAndBurn::_intervalUpdate() function, the lastBurnedIntervalStartTimestamp will be set to the startTimeStamp which is 2 days 14 hours
Now 12 more hours pass, the current block.timestamp is 3 days 2 hours and 12 seconds and the BuyAndBurn::distributeDragonXForBurning() function is called again.
When the BuyAndBurn::_intervalUpdate() function is called, which in turn calls the BuyAndBurn::_calculateIntervals() function internally, we get the following calculations:
- The missedIntervals = 143
- The _totalAmountForInterval will be ~7_500e18 (this amount is for 144 intervals)
- In the BuyAndBurn::_intervalUpdate() function, the lastBurnedIntervalStartTimestamp will be set to 3 days and 2 hours
12 more hours pass and the current block.timestamp is 3 days 14 hours and 12 seconds, the current balance of DragonX tokens of the BuyAndBurn.sol contract is 200_000e18
This time we will enter the else statement of the BuyAndBurn::_calculateIntervals() function:
- The missedIntervals will be 143
- The theEndOfTheDay will be 3 days and 14 hours
- The end will be 3 days and 14 hours - 1 sec
- The accumulatedIntervalsForTheDay will be 143
- The dailyAllocation will be 15_000e18
- The _lastBurnedIntervalStartTimestamp will be 3 days & 14 hours - 5 min
- The theEndOfTheDay will be 4 days & 14 hours
- The _totalAmountForInterval will be ~7_448e18
- When we enter the next while loop iteration we get the following:
  - The end will be equal to the current block.timestamp which is 3 days & 14 hours & 12 seconds
  - The accumulatedIntervalsForTheDay will be 1
  - The diff will be ~192_552e18
  - The dailyAllocation will be ~28_882e18
  - The _totalAmountForInterval will be ~7_448e18 + ~100e18 = ~7_548e18
  - In the _updateSnapshot() function, the totalDragonXDistributed will be set to ~192_552e18
  - In the BuyAndBurn::_intervalUpdate() function, the lastBurnedIntervalStartTimestamp will be set to 3 days and 14 hours.
Now let's consider a different scenario
The BuyAndBurn.sol startTimeStamp is set to 2 days and 14 hours.
The DragonX tokens balance of the BuyAndBurn.sol contract is 100_000e18
At 2 days 14 hours + 287 * 5 mins + 12 sec the BuyAndBurn::distributeDragonXForBurning() function is called, which will internally call the BuyAndBurn::_intervalUpdate() function.
We will get the following calculations from the BuyAndBurn::_calculateIntervals() function:
- The missedIntervals will be 287
- The dailyAllocation will be 15_000e18
- The _amountPerInterval will be ~52e18
- The _totalAmountForInterval will be ~15_000e18
- Later on in the BuyAndBurn::_intervalUpdate() function, the lastBurnedIntervalStartTimestamp will be set to the startTimeStamp which is 2 days 14 hours + 287 * 5 mins which will be equal to 3 days 14 hours - 5 min
5 more minutes pass and the current block.timestamp is 3 days 14 hours and 12 seconds, the current balance of DragonX tokens of the BuyAndBurn.sol contract is 200_000e18
This time we will enter the else statement of the BuyAndBurn::_calculateIntervals() function:
- The missedIntervals will be 0
- The theEndOfTheDay will be 3 days and 14 hours
- The end will be 3 days and 14 hours - 1 sec
- The accumulatedIntervalsForTheDay will be 0
- The _lastBurnedIntervalStartTimestamp will be 3 days & 14 hours - 5 min
- The theEndOfTheDay will be 4 days & 14 hours
- The _totalAmountForInterval will be 0
- When we enter the next while loop iteration we get the following:
  - The end will be equal to the current block.timestamp which is 3 days & 14 hours & 12 seconds
  - The accumulatedIntervalsForTheDay will be 1
  - The diff will be 200_000e18
  - The dailyAllocation will be 30_000e18
  - The _totalAmountForInterval will be 0 + ~104e18 = ~104e18
  - In the _updateSnapshot() function, the totalDragonXDistributed will be set to 200_000e18
  - In the BuyAndBurn::_intervalUpdate() function, the lastBurnedIntervalStartTimestamp will be set to 3 days and 14 hours.
As we can see from the above examples in both of the cases the protocol distributes almost equal amounts for the same periods ~15_100e18. However in the first case, the totalDragonXDistributed will be ~192_552e18, and in the second 200_000e18. This is a significant difference because when the calculations for the next interval are performed the dailyAllocation in the first example will be 192_552e18 * 0.15e18 / 1e18 = 28_882e18, and in the second example the dailyAllocation will be 30_000e18 Based on the fact that the sole purpose of the BuyAndBurn.sol contract is to determine how much tokens should be distributed for burning, and thus incentives for the users calling the swapDragonXToVyperAndBurn() function, I believe the above described discrepancies warrant a medium impact.

## Recommendation
Consider implementing an iterative system in the _calculateIntervals() function that guarantees each interval is calculated separately. Or implement an offchain oracle that guarantees the BuyAndBurn::_intervalUpdate() function is invoked in each period.
