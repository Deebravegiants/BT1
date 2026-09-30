# [M] Inaccurate fees computation

## Summary
Severity: Medium
Contest weight: 0.1669
Dataset id: 1191
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The `MixinTransfer.shareKey` function wants to compute a fee such that `time + fee * time == timeRemaining (timePlusFee)`:
    
    uint fee = getTransferFee(keyOwner, _timeShared);
    uint timePlusFee = _timeShared + fee;

However, if the time remaining is less than the computed fee time, **the computation changes and a different formula is applied**. The fee is now simply taken on the remaining time.
    
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

It should compute the `time` without fee as `time = BASIS_POINTS_DEN * timeRemaining / (1.0 + fee_as_decimal)` instead, i.e., `time = BASIS_POINTS_DEN * timeRemaining / (transferFeeBasisPoints + BASIS_POINTS_DEN)`.

## Recommendation
It should change the first `if` branch condition to `timePlusFee <= timeRemaining` (less than or equal). In the `else` branch, it should compute the time without fee as `time = BASIS_POINTS_DEN * timeRemaining / (transferFeeBasisPoints + BASIS_POINTS_DEN)`.

Great find!
