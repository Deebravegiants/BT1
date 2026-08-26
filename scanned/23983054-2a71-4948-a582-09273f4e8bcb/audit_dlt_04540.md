# [H] ConvexBoosterController.sol : incorrect reward pool address collected in `canDeposit`

## Summary
Severity: High
Chain: Smart contract
Component: 2022-12-sentiment
Published: 2022-12-02
Source: https://github.com/sherlock-audit/2022-12-sentiment-judging/issues/19
Type: sherlock-finding

## Details
ak1

high

# ConvexBoosterController.sol : incorrect reward pool address collected in `canDeposit`

## Summary
For booster,  `canDeposit` function returns the `lpToken` and `rewardPool` addresses.

The collected `rewardPool` is not of the `crvRewards`

## Vulnerability Detail
Here how the token address collected from booster.

        (address lpToken, , address rewardPool, ,) = IBooster(BOOSTER).poolInfo(pid);

The booster structure is,

    struct PoolInfo {
        address lptoken;
        address token;
        address gauge;
        address crvRewards;
        address stash;
        bool shutdown;
    }

the third argument is `gauge`, current implementation return this gauge as reward pool


## Impact
Incorrect reward pool is used which is not correct method. reward collection will not work.

## Code Snippet

https://github.com/sherlock-audit/2022-12-sentiment/blob/main/controller/src/convex/ConvexBoosterController.sol#L37

## Tool used

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-12-sentiment-judging/issues/19_
