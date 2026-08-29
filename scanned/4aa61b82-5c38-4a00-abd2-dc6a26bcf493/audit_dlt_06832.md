# [M] Inaccurate fees computation

## Summary
Severity: Medium
Chain: Smart contract
Component: 2021-11-unlock
Published: 2021-11-24
Source: https://github.com/code-423n4/2021-11-unlock-findings/issues/165
Type: code-finding

## Details
# Handle

cmichel


# Vulnerability details

The `MixinTransfer.shareKey` function wants to compute a fee such that `time + fee * time == timeRemaining (timePlusFee)`:

```solidity
uint fee = getTransferFee(keyOwner, _timeShared);
uint timePlusFee = _timeShared + fee;
```

However, if the time remaining is less than the computed fee time, **the computation changes and a different formula is applied**.
The fee is now simply taken on the remaining time.

```solidity
if(timePlusFee < timeRemaining) {
  // now we can safely set the time
  time = _timeShared;
  // deduct time from parent key, including transfer fee
  _timeMachine(_tokenId, timePlusFee, false);
} else {
  // we have to recalculate the fee here
  fee = getTransferFee(keyOwner, timeRemaining);
  // @audit want it such that time + fee * time == timeRemaining, but fee is taken on timeRemaining instead of time
  time = timeRemaining - fee;
}
```

It should compute the `time` without fee as `time = timeRemaining / (1.0 + fee_as_decimal)` instead, i.e., `time = BASIS_POINTS_DEN * timeRemaining / (transferFeeBasisPoints + BASIS_POINTS_DEN)`.

#### POC
To demonstrate the difference with a 10% fee and a `_timeShared = 10,000s` which should be credited to the `to` account.

The correct time plus fee which is reduced from `from` (as in the `timePlusFee < timeRemaining` branch) would be `10,000 + 10% * 10,000 = 11,000`.


_Trimmed to 38 lines — full report: https://github.com/code-423n4/2021-11-unlock-findings/issues/165_
