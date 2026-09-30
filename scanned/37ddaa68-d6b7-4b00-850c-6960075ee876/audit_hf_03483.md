# [M] `_claimRewardsOnBehalf

## Summary
Severity: Medium
Contest weight: 0.7221
Dataset id: 19054
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability originates from an incorrect determination of the maximum reward amount that can be transferred when a user (or a third party) calls the internal function that claims rewards on behalf of an address. The contract keeps an accounting variable that accumulates each user’s unclaimed rewards through internal calculations, but the actual reward tokens are stored partly in an external Incentives Controller contract rather than in the main contract’s balance. When the claim function is invoked without the forceUpdate flag, it reads the contract’s token balance (REWARD_TOKEN.balanceOf(address(this))) and, if the calculated reward exceeds that balance, it silently reduces the reward to the available balance and then resets the user’s unclaimed reward counter to zero. Because the external controller still holds the missing tokens, the accounting entry for the user becomes larger than the real token holdings, and the excess amount is effectively lost. An attacker can trigger a claim on behalf of a victim while the contract’s balance is insufficient, causing the victim’s pending reward to be truncated and the internal record cleared, resulting in permanent loss of the victim’s accrued rewards. This issue manifests whenever the contract’s reward token balance is lower than the sum of all users’ unclaimed rewards and a claim is performed without forcing an update that would pull the missing tokens from the Incentives Controller. Affected parties include any token holder with pending rewards, the protocol’s economic model, and any downstream applications that rely on accurate reward accounting. The problem was discovered during a manual audit that compared the reward accounting logic with the actual token flow and identified that the _updateRewards and _updateUser functions only compute values without transferring tokens, while the claim function assumes the contract’s balance reflects the total rewards. The bug is subtle because the balance‑capping check appears reasonable at first glance, yet the mismatch between internal accounting and external token storage can go unnoticed until a user experiences a shortfall in the claimed amount. From a user’s perspective the UI may display a certain amount of pending rewards, but after initiating a claim the received amount can be zero or lower than expected, violating the expectation that all displayed rewards will be transferred. The flaw belongs to the class of reward‑distribution accounting errors where external token sources are not synchronized with internal state, leading to truncation or loss of funds. To remediate the issue the contract should only apply the balance‑cap logic when forceUpdate is true, or it should first pull the missing rewards from the Incentives Controller into the contract before performing the cap, and finally it must adjust the unclaimed reward record to reflect any shortfall rather than clearing it entirely.

## Proof of Concept
```solidity
_claimRewardsOnBehalf() for users to retrieve rewards:

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

    if (reward > totBal) {
        reward = totBal;
    }
    if (reward > 0) {
        _unclaimedRewards[onBehalfOf] = 0;
        _updateUserSnapshotRewardsPerToken(onBehalfOf);
        REWARD_TOKEN.safeTransfer(receiver, reward);
    }
}
```

From the code above, we can see that if the contract balance is not enough, it will only use the contract balance and set the unclaimed rewards to 0: `_unclaimedRewards[user]=0`.

But using the current contract’s balance is inaccurate, `REWARD_TOKEN` may still be stored in `INCENTIVES_CONTROLLER`.

`_updateRewards()` and `_updateUser()`, are just calculations, they don’t transfer `REWARD_TOKEN` to the current contract, but `_unclaimedRewards[user]` is always accumulating.

  1. `_updateRewards()` not transferable `REWARD_TOKEN`.

```solidity
function _updateRewards() internal {
...
    if (block.number > _lastRewardBlock) {
...

        address[] memory assets = new address[](1);
        assets[0] = address(ATOKEN);

        uint256 freshRewards = INCENTIVES_CONTROLLER.getRewardsBalance(assets, address(this));
        uint256 lifetimeRewards = _lifetimeRewardsClaimed.add(freshRewards);
        uint256 rewardsAccrued = lifetimeRewards.sub(_lifetimeRewards).wadToRay();

        _accRewardsPerToken = _accRewardsPerToken.add(
            (rewardsAccrued).rayDivNoRounding(supply.wadToRay())
        );
        _lifetimeRewards = lifetimeRewards;
    }
}
```

  2. But `_unclaimedRewards[user]` always accumulating.

```solidity
function _updateUser(address user) internal {
    uint256 balance = balanceOf(user);
    if (balance > 0) {
        uint256 pending = _getPendingRewards(user, balance, false);
        _unclaimedRewards[user] = _unclaimedRewards[user].add(pending);
    }
    _updateUserSnapshotRewardsPerToken(user);
}
```

This way if `_unclaimedRewards(forceUpdate=false)` is executed, it does not trigger the transfer of `REWARD_TOKEN` to the current contract. This makes it possible that `_unclaimedRewards[user] > REWARD_TOKEN.balanceOf(address(this))`. According to the `_claimedRewardsOnBehalf()` current code, the extra value is lost.

It is recommended that `if (reward > totBal)` be executed only if `forceUpdate=true`, to avoid losing user rewards.

## Recommendation
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

    if (forceUpdate && reward > totBal) {
        reward = totBal;
    }
    if (reward > 0) {
        _unclaimedRewards[onBehalfOf] = 0;
        _updateUserSnapshotRewardsPerToken(onBehalfOf);
        REWARD_TOKEN.safeTransfer(receiver, reward);
    }
}
```
