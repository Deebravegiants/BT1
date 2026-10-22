# [H] The unlockExponent does not work as intended when it is ≠ 1

## Summary
Severity: High
Contest weight: 0.3785
Dataset id: 16583
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The documentation and the chart in README.md shows that it is expected that when unlockExponent == 0 then immediately after funds unlockDelaySec the user can claim his whole locked amount. This is actually not working as intended, let’s look at the _getWithdrawableAmount function:
To calculate the amount to unlock, we have the following: uint256 totalUnlockedAmount = (record.totalAmount * factor) / precision;
record.totalAmount is the total locked amount, precision is a constant with a value of 1e8 and factor is calculated by this: uint256 factor = deltaTimeNormalized ** unlockExponent;
if (factor > precision) { factor = precision;
If we have unlockExponent == 0 then factor is always equal to 1, which is less than 1e8 so factor == 1
Now if we go back to the total amount to unlock math, we will get uint256 totalUnlockedAmount = (record.totalAmount * factor) / precision; so uint256 totalUnlockedAmount = record.totalAmount / precision
The expected unlocked amount was equal to record.totalAmount but instead we got record.totalAmount / precision which is incorrect. Now every subsequent time the _getWithdrawableAmount function is called, the math will be the same and the code will basically think there is no newly unlocked amount. This means that no user that has locked funds in Zerem will be able to withdraw more than totalLockedAmount / 1e8 ever, all of the other tokens will be stuck.
There is also a problem when unlockExponent > 1 , because the computed factor can easily be >= precision which will result in 100% of funds being unlocked too early.
Here is the important math: uint256 deltaTimeNormalized = (deltaTimeDelayed * precision) / unlockPeriodSec;
uint256 factor = deltaTimeNormalized ** unlockExponent;
if (factor > precision) { factor = precision;
uint256 totalUnlockedAmount = (record.totalAmount * factor) / precision;
and let’s look at example scenario:
unlockPeriodSec == 100000 , deltaTimeDelayed == 100 and precision == 1e8 so deltaTimeNormalized == 1e5
if unlockExponent > 1 for example when equal to 2, we will get factor = 1e5 ** 2 , so 1e10 which is > precision that is 1e8 so now factor = precision
Now totalUnlockedAmount = record.totalAmount * factor / factor which is record.totalAmount
even though only 1/1000th of the unlock period has passed and the unlockExponent was just 2 , the user can already claim all of their locked tokens.
The protocol does not work as expected in its core functionality and can also result in stuck tokens (value loss) for users or tokens unlocked too early, so it is High severity.

## Recommendation
Redesign the unlockExponent logic or just hardcode it to always be linear (a value of 1)
Client response
Resolved by removing the unlockExponent logic
