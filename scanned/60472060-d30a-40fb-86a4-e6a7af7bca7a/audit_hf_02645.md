# [H] extraReward2 is Not Set in the constructor()

## Summary
Severity: High
Contest weight: 0.5765
Dataset id: 14321
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
_extraReward2 is never set in the constructor of ConvexV1_BaseRewardPool.sol.
Gearbox integrates the Convex platform by allowing borrowers to stake their Convex LP tokens. Gearbox makes use
of a phantom ERC20 token to represent the borrower’s position in the reward pool. Extra rewards can be attached to
a reward pool on top of any Curve and Convex rewards.
Within the constructor() code, _extraReward2 is never set and will end up storing the zero address. As a result,
extraReward2 will also contain the zero address and extraReward1 will be overwritten with the address intended for
extraReward2. The affected code is shown below:
```solidity
if (extraRewardLength >= 1) {
    _extraReward1 = IRewards(
        IBaseRewardPool(_baseRewardPool).extraRewards(0)
    ).rewardToken();
    if (extraRewardLength >= 2) {
        _extraReward1 = IRewards(
            IBaseRewardPool(_baseRewardPool).extraRewards(1)
        ).rewardToken(); // assign to _extraReward2, not _extraReward1
    }
}
```

## Recommendation
Modify the constructor() code to store the extra rewards in their correct, corresponding variables _extraReward1
and _extraReward2.
