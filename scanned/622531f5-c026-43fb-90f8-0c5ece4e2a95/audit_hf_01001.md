# [M] First leveraged pool is extra penalized

## Summary
Severity: Medium
Contest weight: 0.4027
Dataset id: 3329
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
To handle the increased risk from liquidity providers providing the same liquidity in multiple pools the protocol has a leverage fee that is taken on the profits made, this only kicks in when a liquidity provider provides liquidity in more than one pool: VirtualPool::_payRewardsAndFees:
```solidity
uint256 leverageFee;
if (1 < nbPools_) {
    // The risk fee is only applied when using leverage
    leverageFee =
        (rewards_ * (self.leverageFeePerPool * nbPools_)) /
        HUNDRED_PERCENT;
} // ...
```
The issue here is that the first "additional" pool will get unfairly penalized. If you stake in one pool you get 0 leverageFee applied. If you stake in two pools you get 2*leverageFee applied. While you stake in a third pool you only get one additional leverageFee for this pool (3*leverageFee). I.e. the second pool costs 2 leverage fees, compared to the rest.

## Recommendation
Consider just taking the leverageFee for the additional pools: - (rewards_ * (self.leverageFeePerPool * nbPools_)) / + (rewards_ * (self.leverageFeePerPool * nbPools_ - 1)) /
