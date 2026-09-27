# [H] 5.1.1 UnaccruedSecondsdo not increase even if nobody is actively staking

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** High Risk

**Context:** Lock.sol.sol#L

**Description** : Theunstreamedvariable tracks whether someone is staking in the contract or not. However, because
of the division precision loss at Locke.sol#L164-L166 and Locke.sol#L187,unstreamed > 0may happen even
when everyone has already withdrawn all deposited tokens from the contract, i.e.ts.token = 0for everyone.

Consider the following proof of concept with only two users, Alice and Bob:

- streamDuration = 8888
- Att = startTime, Alice stakes1052 weiof deposit tokens.
- Att = startTime + 99, Bob stakes6733 weiof deposit tokens.
- Att = startTime + 36, both Alice and Bob exits from the contract.

At this point Alice’s and Bob’sts.tokensare both 0 butunstreamed = 1 wei. The abovementined numbers are
the resault of a fuzzing campaign and were not carefully crafted, therefore this issue can also occur under normal
circumstances.

```
function updateStreamInternal() internal {
```
```
uint256 tdelta = timestamp - lastUpdate;
if (tdelta > 0) {
if (unstreamed == 0) {
unaccruedSeconds += uint32(tdelta);
} else {
unstreamed -= uint112(tdelta * unstreamed / (endStream - lastUpdate));
}
}
```
```
}
```
**Recommendation:** Consider using totalVirtualBalance == 0instead ofunstreamed == 0
