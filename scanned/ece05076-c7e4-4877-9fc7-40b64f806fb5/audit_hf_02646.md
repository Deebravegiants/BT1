# [M] Incorrect Construction of stakedPhantomToken

## Summary
Severity: Medium
Contest weight: 0.3909
Dataset id: 14325
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the constructor code of ConvexV1BaseRewardPoolAdapter, the stakedPhantomToken is created with the pool’s
staking token passed in as ﬁrst parameter, instead of the pool address itself.
As such, phantom token will not return correct balances, which will result in unexpected behaviour in other functions.
Affected code:
```solidity
stakedPhantomToken = address(
    new ConvexStakedPositionToken(
        address(IBaseRewardPool(_baseRewardPool).stakingToken()),
        // note, 'stakingToken()' address referenced, instead of pool address
        cvxLPtoken
    )
);
```
Note constructor declaration of ConvexStakedPositionToken - constructor(address _pool, address _lptoken).

## Recommendation
Modify call constructing stakedPhantomToken from address(IBaseRewardPool(_baseRewardPool).stakingToken())
to address(IBaseRewardPool(_baseRewardPool)).
