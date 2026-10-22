# [M] `FlywheelCore.setBooster`

## Summary
Severity: Medium
Contest weight: 0.6501
Dataset id: 4834
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
A malicious authorized user can steal all unclaimed rewards and break the reward accounting

Even if the authorized user is benevolent the fact that there is a rug vector available may negatively impact the protocol’s reputation. Furthermore since this contract is meant to be used by other projects, the trustworthiness of every project cannot be vouched for.

## Proof of Concept
By setting a booster that returns zero for all calls to `boostedBalanceOf()` where the `user` address is not under the attacker’s control, and returning arbitrary values for those under his/her control, an attacker can choose specific amounts of `rewardToken` to assign to himself/herself. The attacker can then call `claimRewards()` to withdraw the funds. Any amounts that the attacker assigns to himself/herself over the amount that normally would have been assigned, upon claiming, is taken from other users’ unclaimed balances, since tokens are custodied by the `flywheelRewards` address rather than per-user accounts.
    
File: flywheel-v2/src/FlywheelCore.sol

```solidity
/// @notice swap out the flywheel booster contract
function setBooster(IFlywheelBooster newBooster) external requiresAuth {
    flywheelBooster = newBooster;

    emit FlywheelBoosterUpdate(address(newBooster));
}
```

[FlywheelCore.sol#L182-L187](https://github.com/fei-protocol/flywheel-v2/blob/77bfadf388db25cf5917d39cd9c0ad920f404aad/src/FlywheelCore.sol#L182-L187)  

File: flywheel-v2/src/FlywheelCore.sol

```solidity
uint256 supplierTokens = address(flywheelBooster) != address(0)
    ? flywheelBooster.boostedBalanceOf(strategy, user)
    : strategy.balanceOf(user);

// accumulate rewards by multiplying user tokens by rewardsPerToken index and adding on unclaimed
uint256 supplierDelta = (supplierTokens * deltaIndex) / ONE;
uint256 supplierAccrued = rewardsAccrued[user] + supplierDelta;

rewardsAccrued[user] = supplierAccrued;
```

[FlywheelCore.sol#L258-L266](https://github.com/fei-protocol/flywheel-v2/blob/77bfadf388db25cf5917d39cd9c0ad920f404aad/src/FlywheelCore.sol#L258-L266)  

File: flywheel-v2/src/FlywheelCore.sol

```solidity
function claimRewards(address user) external {
    uint256 accrued = rewardsAccrued[user];

    if (accrued != 0) {
        rewardsAccrued[user] = 0;

        rewardToken.safeTransferFrom(address(flywheelRewards), user, accrued);
    }
}
```

[FlywheelCore.sol#L119-L125](https://github.com/fei-protocol/flywheel-v2/blob/77bfadf388db25cf5917d39cd9c0ad920f404aad/src/FlywheelCore.sol#L119-L125)  

Projects also using `BaseFlywheelRewards` or its child contrats, are implicitly approving infinite transfers by the core

File: flywheel-v2/src/rewards/BaseFlywheelRewards.sol

```solidity
constructor(FlywheelCore _flywheel) {
    flywheel = _flywheel;
    ERC20 _rewardToken = _flywheel.rewardToken();
    rewardToken = _rewardToken;

    _rewardToken.safeApprove(address(_flywheel), type(uint256).max);
}
```

[BaseFlywheelRewards.sol#L25-L31](https://github.com/fei-protocol/flywheel-v2/blob/77bfadf388db25cf5917d39cd9c0ad920f404aad/src/rewards/BaseFlywheelRewards.sol#L25-L31)  

The attacker need not keep the booster set this way - he/she can set it, call `accrue()` for his/her specific user, and unset it, all in the same block.

## Recommendation
Make `flywheelRewards` immutable, or only allow it to change if there are no current users.

This is a similar issue to one which already affects the SushiSwap masterchef. If rewards are decreased without first calling the `accrue`-equivalent on the masterchef, then previous rewards are lost.

If trust minimization is a desired property (in my opinion it is), then these functions should be behind timelocks.

If a user can call accrue before the booster is updated, they can lock in past rewards as they are added onto the rewardsAccrued global state var `266 rewardsAccrued[user] = supplierAccrued;`

I don’t really see this as a vulnerability, but will leave it to the C4 judge.

I do see this as a vulnerability. Essentially, there is a backdoor by which a privileged address can extract value from users. A timelock would be a potential solution to mitigate some of the risk, as well as the mitigation options presented by the warden. 

`2 — Med: Assets not at direct risk, but the function of the protocol or its availability could be impacted, or leak value with a hypothetical attack path with stated assumptions, but external requirements.`

This is a hypothetical attack path with external requirements and deserves the medium severity rating.
