# [M] 5.2.1 ThestreamAmtcheck may prolong a user in the stream

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Medium Risk

**Context:** Locke.sol#L

**Description** : Assume that the amount of tokens staked by a user (ts.tokens) is low. This check allows another
person to deposit a large stake in order to prolong the user in a stream (untilstreamAmtfor the user becomes
non-zero). For this duration the user would be receiving a bad rate or 0 altogether for the reward token while being
unable to exit from the pool.

```
if (streamAmt == 0) revert ZeroAmount();
```
Therefore, if Alice stakes a small amount of deposit token and Bob comes along and deposits a very large amount
of deposit token, tt’s in Alice’s interest to exit the pool as early as possible especially when this is an indefinite
stream. Otherwise the user would be receiving a bad rate for their deposit token.

**Recommendation:** The ideal scenario is ifstreamAmtends up being zero for a certainaccTimeDelta, the user
should be able to exit the pool withts.tokensas long as they don’t receive rewards for the same duration.
However, in practice, implementing this may create issues related tounaccuredseconds.
