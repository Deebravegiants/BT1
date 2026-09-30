# [M] `cancelPromotion`

## Summary
Severity: Medium
Contest weight: 0.3936
Dataset id: 1326
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
For unstarted promotions, `cancelPromotion()` will revert at `block.timestamp - _promotion.startTimestamp` in `_getCurrentEpochId()`.

Call stack: `cancelPromotion()` -> `_getRemainingRewards()` -> `_getCurrentEpochId()`.

```solidity
function _getRemainingRewards(Promotion memory _promotion) internal view returns (uint256) {
    // _tokensPerEpoch * _numberOfEpochsLeft
    return
        _promotion.tokensPerEpoch *
        (_promotion.numberOfEpochs - _getCurrentEpochId(_promotion));
}

function _getCurrentEpochId(Promotion memory _promotion) internal view returns (uint256) {
    // elapsedTimestamp / epochDurationTimestamp
    return (block.timestamp - _promotion.startTimestamp) / _promotion.epochDuration;
}
```

## Recommendation
Consider checking if `_promotion.startTimestamp > block.timestamp` and refund `_promotion.tokensPerEpoch * _promotion.numberOfEpochs` in `cancelPromotion()`.
