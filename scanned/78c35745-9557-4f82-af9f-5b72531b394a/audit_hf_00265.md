# [H] cancelPromotion is too rigorous

## Summary
Severity: High
Contest weight: 0.5482
Dataset id: 1334
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When you cancel a promotion with `cancelPromotion()` then the promotion is complete deleted. This means no-one can claim any rewards anymore, because `_promotions[_promotionId]` no longer exists.

It also means all the unclaimed tokens (of the previous epochs) will stay locked in the contract.

## Proof of Concept
```solidity
function cancelPromotion(uint256 _promotionId, address _to) ... {
    ...
    uint256 _remainingRewards = _getRemainingRewards(_promotion);
    delete _promotions[_promotionId];
```

## Recommendation
In the function `cancelPromotion()` lower the `numberOfEpochs` or set a state variable, to allow user to claim their rewards.
