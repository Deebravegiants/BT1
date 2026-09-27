# [C] 6.1 Adjusted Bias Measured Possibly Too Late

## Summary
Severity: Critical
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Security Critical Version 1 Code Corrected

The amount of excluded votes belonging to the users in the blacklist are counted by the internal
function _getAdjustedBias for the recently concluded period when _updateBribePeriod() is
called. However, the period update only happens when users interact with the contract. Between the start
of the new voting period (timestamp / WEEK * WEEK) and the time _updateBribePeriod() is
called, a blacklist user can cast a new vote on the gauge, which is incorrectly counted by
``_getAdjustedBias() as belonging to the previous period.

rewardPerToken at period T is computed as

```
rewardPerToken(T) = rewardPerPeriod / (total_bias(T) - omitted_reward(T_blacklisted_last_vote))
```
So the periods of total_bias and omitted_reward might not match.

Since the bribe creator has full control on who to include in the blacklist and what gauge to set the bribe
on, they can make rewardPerToken as high as they desire by making the denominator arbitrarily small
with a blacklisted user that they control. Since _claim() doesn't check that
bribe.totalRewardAmount is not exceeded when distributing the reward, a dishonest bribe creator
can use this bug to steal funds from other bribes.

Code corrected

A check has been added so that subtracting the bias of a blacklisted user is only performed if the
blacklisted user has voted before the start of the period. Otherwise bias is not deducted and rewarded
users get a bit less.

```
_lastVote = gaugeController.last_user_vote(_addressesBlacklisted[i], gauge);
if (period > _lastVote) {
_bias = _getAddrBias(userSlope.slope, userSlope.end, period);
gaugeBias -= _bias;
}
```

A check is also introduced so that the cumulative bribe payout never exceeds the
bribe.totalRewardAmount.
