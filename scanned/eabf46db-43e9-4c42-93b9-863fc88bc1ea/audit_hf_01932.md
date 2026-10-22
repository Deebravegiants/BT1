# [H] Distribution.getCurrentPoolRate() function will revert after block.timestamp reaches the maximum end time causing unrecoverable DoS

## Summary
Severity: High
Contest weight: 0.7844
Dataset id: 10564
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
For a given period bound by startTime_ and endTime_ and an interval_ LinearDistributionIntervalDecrease.sol.getPeriodReward() checks if that period is contained within a single interval or spread over multiple ones. In the case where the provided period is spread over several intervals, the reward calculations use the LinearDistributionIntervalDecrease._calculatePartPeriodReward() and LinearDistributionIntervalDecrease._calculateFullPeriodReward() functions.
# LinearDistributionIntervalDecrease.sol
// Calculate interval that less then 'interval_' range
uint256 timePassedBefore_ = startTime_ - payoutStart_;
if ((timePassedBefore_ / interval_) == ((endTime_ - payoutStart_) / interval_)) {
uint256 intervalsPassed_ = timePassedBefore_ / interval_;
uint256 intervalFullReward_ = initialAmount_ - intervalsPassed_ * decreaseAmount_;
return (intervalFullReward_ * (endTime_ - startTime_)) / interval_;
}
// Calculate interval that more then 'interval_' range
uint256 firstPeriodReward_ = _calculatePartPeriodReward(...);
uint256 secondPeriodReward_ = _calculateFullPeriodReward(...);
uint256 thirdPeriodReward_ = _calculatePartPeriodReward(...);
return firstPeriodReward_ + secondPeriodReward_ + thirdPeriodReward_;
A problem arises when initialAmount is not exactly divisible by decreaseAmount. When endTime_ is equal to or beyond the maxEndTime_ (the cutoff point) it is regarded as a new interval. Therefore, if startTime_ is contained within the last period, the reward calculation inside LinearDistributionIntervalDecrease._calculateFullPeriodReward() will revert since LinearDistributionIntervalDecrease._divideCeil() will round up and initialAmount_ - decreaseRewardAmount_ will underflow.
uint256 timePassedBefore_ = startTime_ - payoutStart_;
uint256 intervalsPassedBefore_ = _divideCeil(timePassedBefore_, interval_);
uint256 decreaseRewardAmount_ = intervalsPassedBefore_ * decreaseAmount_;
// Overflow impossible because 'endTime_' can't be more then 'maxEndTime_'
uint256 initialReward_ = initialAmount_ - decreaseRewardAmount_;
Here is a mock example. Assume the following configuration
initialAmount_ = 10
decreaseAmount = 3
payoutStart = 100
interval = 10
startTime = 135
endTime = 140
First we have the condition if ((timePassedBefore_ / interval_) == ((endTime_ - payoutStart_) / interval_)) .... This evaluates to (35 / 10) == (40 / 10) which is false. The reward calculation will continue inside LinearDistributionIntervalDecrease._calculateFullPeriodReward()
The intervals passed are computed uint256 intervalsPassedBefore_ = _divideCeil(timePassedBefore_, interval_); This evaluates to (35 + 10 - 1) / (10) which is 4
The decrease amount is uint256 decreaseRewardAmount_ = intervalsPassedBefore_ * decreaseAmount_; This evaluates to (4x3 = 12)
The interval reward amount is uint256 initialReward_ = initialAmount_ - decreaseRewardAmount_; This evaluates to (10 - 12) and the function reverts.
The Impact implications are that Distribution._getCurrentPoolRate() will revert when block.timestamp becomes or surpasses the maximum end time of the distribution. This will block the stake, withdraw, claim, and edit functionality inside Distribution.sol.
Note that for this issue to occur initialAmount must not be evenly divisible by decreaseAmount which according to the Whitepaper it is not:
The block reward will start at 14,400 MOR per day and then decline by 2.468994701 MOR each day, until the reward reaches 0 on day 5,833.
```

## Recommendation
```solidity
