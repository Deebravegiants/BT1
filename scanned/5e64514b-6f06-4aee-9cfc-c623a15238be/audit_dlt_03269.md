# [H] ConvexStakingWrapper.sol after shutdown，rewards can be steal

## Summary
Severity: High
Chain: Smart contract
Component: 2023-07-reserve
Published: 2023-08-03
Source: https://github.com/code-423n4/2023-07-reserve-findings/issues/11
Type: code-finding

## Details
# Lines of code

 https://github.com/reserve-protocol/protocol/blob/e3d2681503499e81915797c77eeef8210352a138/contracts/plugins/assets/convex/vendor/ConvexStakingWrapper.sol#L296


# Vulnerability details

## Impact
After shutdown, checkpoints are stopped, leading to possible theft of rewards. 

## Proof of Concept
`ConvexStakingWrapper` No more `checkpoints` after `shutdown`, i.e. no updates `reward.reward_integral_for[user]`

```solidity
    function _beforeTokenTransfer(
        address _from,
        address _to,
        uint256
    ) internal override {
@>      _checkpoint([_from, _to]);
    }

    function _checkpoint(address[2] memory _accounts) internal nonReentrant {
        //if shutdown, no longer checkpoint in case there are problems
@>      if (isShutdown()) return;

        uint256 supply = _getTotalSupply();
        uint256[2] memory depositedBalance;
        depositedBalance[0] = _getDepositedBalance(_accounts[0]);
        depositedBalance[1] = _getDepositedBalance(_accounts[1]);

        IRewardStaking(convexPool).getReward(address(this), true);

        _claimExtras();

        uint256 rewardCount = rewards.length;
        for (uint256 i = 0; i < rewardCount; i++) {
            _calcRewardIntegral(i, _accounts, depositedBalance, supply, false);
        }
    }    
```

This would result in, after `shutdown`, being able to steal `rewards` by transferring `tokens` to new users

Example:
Suppose the current
reward.reward_integral = 1000

When a `shutdown` occurs
1. alice transfers 100 to the new user, bob.
Since bob is the new user and `_beforeTokenTransfer()->_checkpoint()` is not actually executed
Result.
balanceOf[bob] = 100
reward.reward_integral_for[bob] = 0

2. bob executes `claimRewards()` to steal the reward
reward amount = balanceOf[bob] * (reward.reward_integral - reward.reward_integral_for[bob])
              = 100 * (1000-0)
3. bob transfers the balance to other new users, looping steps 1-2 and stealing all rewards

## Tools Used

## Recommended Mitigation Steps

Still execute _checkpoint

```solidity

    function _checkpoint(address[2] memory _accounts) internal nonReentrant {
        //if shutdown, no longer checkpoint in case there are problems
 -      if (isShutdown()) return;

        uint256 supply = _getTotalSupply();
        uint256[2] memory depositedBalance;
        depositedBalance[0] = _getDepositedBalance(_accounts[0]);
        depositedBalance[1] = _getDepositedBalance(_accounts[1]);

        IRewardStaking(convexPool).getReward(address(this), true);

        _claimExtras();

        uint256 rewardCount = rewards.length;
        for (uint256 i = 0; i < rewardCount; i++) {
            _calcRewardIntegral(i, _accounts, depositedBalance, supply, false);
        }
    }    
```


## Assessed type

Context
