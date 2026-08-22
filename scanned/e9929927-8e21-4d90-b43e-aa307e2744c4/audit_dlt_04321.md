# [M] `Withdraw` and `Cancel` time can be circumvented _recipientBalance()

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-nounsdao
Published: 2022-12-07
Source: https://github.com/sherlock-audit/2022-11-nounsdao-judging/issues/44
Type: sherlock-finding

## Details
yongkiws

medium

# `Withdraw` and `Cancel` time can be circumvented _recipientBalance()

## Summary
The balance is calculated using the `startTime()` of the stream, the amount of tokens that should be streamed, and the current rate at which tokens are being streamed. If the current block's timestamp is before the start time of the stream, the balance is 0. If the current block's timestamp is after the stop time of the stream, the balance is the total amount of tokens that should be streamed. Otherwise, the balance is calculated by multiplying the elapsed time by the rate per second, and dividing by a rate multiplier. Finally, the function takes any withdrawals into account by subtracting them from the balance.

## Vulnerability Detail
someone to call a function that changes the time period `elapsedTime()` and `_recipientBalance()` , an attacker can call the function to reduce the time period and then immediately withdraw funds that should be locked.

## Impact
Summary

## Code Snippet
-if the current block time is less than the start time. If so, it returns 0.
-if the current block time is greater than the stop time. If so, it returns the token amount.
-Otherwise, it calculates the elapsed time between the start time and the current block time.
-It then multiplies the elapsed time by the rate per second.
-Finally, it divides the result by the rate per second to get the token balance.
```solidity
 function _recipientBalance() internal view returns (uint256) {
        uint256 startTime_ = startTime();
        uint256 blockTime = block.timestamp;

        if (blockTime <= startTime_) return 0;

        uint256 tokenAmount_ = tokenAmount();
        uint256 balance;
        if (blockTime >= stopTime()) {
            balance = tokenAmount_;
        } else {
            // This is safe because: blockTime > startTime_ (checked above).
            unchecked {
                uint256 elapsedTime_ = blockTime - startTime_;
                balance = (elapsedTime_ * ratePerSecond()) / RATE_DECIMALS_MULTIPLIER;
            }
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-11-nounsdao-judging/issues/44_
