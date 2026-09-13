# [M] 7.3 Race Condition on Loss

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Design Medium Version 1 Code Corrected

When a strategy made a loss, a race condition between veAngle holder / long term admins and Standard
Liquidity Providers (SLPs) will arise:

Angle Stakers will attempt to call pullSurplus() to evacuate the surplus and protect their profits while
SLPs will try to call harvest() on the strategy, which reports the loss to the PoolManager and at least
partially tries to cover the loss using interestsAccumulated of the Angle Stakers.

However, the receivers of the funds can trick the SLPs by pulling surplus after each gain immediately.

Code corrected:

A new variable tracking the debt to be covered by the admins has been introduced. When the loss is too
high such that the currently available interestsAccumulated are not enough to cover for the losses,
this debt is accrued. If there is a gain, the gain is first going to reimburse the debt and only afterwards
accrue new interestsAccumulated.

Note that upon the first loss to be reported the race condition still exists. Admins may withdraw the
interestsAccumulated first but then have to cover the debt accrued by the reported loss with the
next profit/profits reported.
