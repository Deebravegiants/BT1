# [M] _claimRewardsOnBehalf() User's rewards may be lost

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-07-reserve
Published: 2023-08-03
Source: https://github.com/code-423n4/2023-07-reserve-findings/issues/10
Type: code-finding

## Details
# Lines of code

https://github.com/reserve-protocol/protocol/blob/e3d2681503499e81915797c77eeef8210352a138/contracts/plugins/assets/aave/StaticATokenLM.sol#L459-L461


# Vulnerability details

## Impact
Incorrect determination of maximum rewards, which may lead to loss of user rewards

## Proof of Concept
`_claimRewardsOnBehalf()` For users to retrieve rewards

```solidity
    function _claimRewardsOnBehalf(
        address onBehalfOf,
        address receiver,
        bool forceUpdate
    ) internal {
        if (forceUpdate) {
            _collectAndUpdateRewards();
        }

        uint256 balance = balanceOf(onBehalfOf);
        uint256 reward = _getClaimableRewards(onBehalfOf, balance, false);
        uint256 totBal = REWARD_TOKEN.balanceOf(address(this));

@>      if (reward > totBal) {
@>          reward = totBal;
@>      }
        if (reward > 0) {
@>          _unclaimedRewards[onBehalfOf] = 0;
            _updateUserSnapshotRewardsPerToken(onBehalfOf);
            REWARD_TOKEN.safeTransfer(receiver, reward);
        }
    }
```

From the code above, we can see that if the contract balance is not enough, it will only use the contract balance and set the unclaimed rewards to 0: `_unclaimedRewards[user]=0`.

But using the current contract's balance is inaccurate, `REWARD_TOKEN` may still be stored in `INCENTIVES_CONTROLLER

`_updateRewards()` and `_updateUser()`, are just calculations, they don't transfer `REWARD_TOKEN` to the current contract, but `_unclaimedRewards[user]` is always accumulating

1. `_updateRewards()` not transferable `REWARD_TOKEN`
```
    function _updateRewards() internal {
...
        if (block.number > _lastRewardBlock) {
...

            address[] memory assets = new address[](1);
            assets[0] = address(ATOKEN);

@>          uint256 freshRewards = INCENTIVES_CONTROLLER.getRewardsBalance(assets, address(this));
            uint256 lifetimeRewards = _lifetimeRewardsClaimed.add(freshRewards);
            uint256 rewardsAccrued = lifetimeRewards.sub(_lifetimeRewards).wadToRay();

@>          _accRewardsPerToken = _accRewardsPerToken.add(
                (rewardsAccrued).rayDivNoRounding(supply.wadToRay())
            );
            _lifetimeRewards = lifetimeRewards;
        }
    }
```

2. but `_unclaimedRewards[user]` always accumulating

```solidity
    function _updateUser(address user) internal {
        uint256 balance = balanceOf(user);
        if (balance > 0) {
            uint256 pending = _getPendingRewards(user, balance, false);
@>          _unclaimedRewards[user] = _unclaimedRewards[user].add(pending);
        }
        _updateUserSnapshotRewardsPerToken(user);
    }
```


This way if `_unclaimedRewards(forceUpdate=false)` is executed, it does not trigger the transfer of `REWARD_TOKEN` to the current contract.
This makes it possible that `_unclaimedRewards[user] > REWARD_TOKEN.balanceOf(address(this))` 
According to the `_claimedRewardsOnBehalf()` current code, the extra value is lost.

It is recommended that `if (reward > totBal)` be executed only if `forceUpdate=true`, to avoid losing user rewards.

## Tools Used

## Recommended Mitigation Steps

```solidity
    function _claimRewardsOnBehalf(
        address onBehalfOf,
        address receiver,
        bool forceUpdate
    ) internal {
        if (forceUpdate) {
            _collectAndUpdateRewards();
        }

        uint256 balance = balanceOf(onBehalfOf);
        uint256 reward = _getClaimableRewards(onBehalfOf, balance, false);
        uint256 totBal = REWARD_TOKEN.balanceOf(address(this));

-       if (reward > totBal) {
+       if (forceUpdate && reward > totBal) {
            reward = totBal;
        }
        if (reward > 0) {
            _unclaimedRewards[onBehalfOf] = 0;
            _updateUserSnapshotRewardsPerToken(onBehalfOf);
            REWARD_TOKEN.safeTransfer(receiver, reward);
        }
    }
```


## Assessed type

Context
