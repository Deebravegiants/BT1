# [M] M-04 Unmitigated

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-07-angle-mitigation
Published: 2023-07-18
Source: https://github.com/code-423n4/2023-07-angle-mitigation-findings/issues/3
Type: code-finding

## Details
# Lines of code




# Vulnerability details

While the fix improves the APR estimation for the case that is described in the finding, it significantly worsens it for other scenarios (which may happen in practice when we assume underlying staking protocols with relatively constant APRs). For instance, consider the situation where we have `updateDelay = 20 days` (or alternatively a governor / guardian that just calls `accrue` every 20 days) and `vestingPeriod = 10 days`. We further assume that the real APR is exactly 5%. We then have:
- During the first 10 days after an `accrue` call, the function reports a value of 5%, which is correct.
- From day 11 to 20, `lockedProfit()` is 0 and the function will report an APR of 0%, which is wrong.

As it was mentioned by the sponsor, the goal of the function is to provide an estimate that is correct in the long term. This was the case for the old version without the zero check, as it would have always reported a value of 5%. The new version reports a value of 0% for 50% of the time, although no user ever observes an APR of 0 over a longer (>20 days) timespan.
