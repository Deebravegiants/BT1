# [H] `withdrawETH` can cause users to lose unclaimed ETH rewards

## Summary
Severity: High
Contest weight: 0.6843
Dataset id: 17142
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Function `_distributeETHRewardsToUserForToken()` is used to distribute remaining reward of user and it’s called in `_onWithdraw()` of `GiantMevAndFeesPool`. but function `withdrawETH()` in `GiantPoolBase` don’t call either of them and burn user giant LP token balance so if user withdraw his funds and has some remaining ETH rewards he would lose those rewards because his balance set to zero.

## Proof of Concept
This is `withdrawETH()` code in `GiantPoolBase`:

```solidity
/// @notice Allow a user to chose to burn their LP tokens for ETH only if the requested amount is idle and available from the contract
/// @param _amount of LP tokens user is burning in exchange for same amount of ETH
function withdrawETH(uint256 _amount) external nonReentrant {
    require(_amount >= MIN_STAKING_AMOUNT, "Invalid amount");
    require(lpTokenETH.balanceOf(msg.sender) >= _amount, "Invalid balance");
    require(idleETH >= _amount, "Come back later or withdraw less ETH");

    idleETH -= _amount;

    lpTokenETH.burn(msg.sender, _amount);
    (bool success,) = msg.sender.call{value: _amount}("");
    require(success, "Failed to transfer ETH");

    emit LPBurnedForETH(msg.sender, _amount);
}
```

As you can see it burn user `lpTokenETH` balance and don’t call either `_distributeETHRewardsToUserForToken()` or `_onWithdraw()`. and in function `claimRewards()` uses `lpTokenETH.balanceOf(msg.sender)` to calculate user rewards so if user balance get to `0` user won’t get the remaining rewards. These are steps that this bug happens:

1. `user1` deposit `10` ETH into the giant pool and `claimed[user1][lpTokenETH]` is `20` and `accumulatedETHPerLPShare` is `2`.
2. some time passes and `accumulatedETHPerLPShare` set to `3`.
3. `user1` unclaimed rewards are `10 * 3 - 20 = 10` ETH.
4. `user1` withdraw his `10` ETH by calling `withdrawETH(10)` and contract set `lpTokenETH` balance of `user1` to `0` and transfer `10` ETH to user.
5. now if `user1` calls `claimRewards()` he would get `0` reward as his `lpTokenETH` balance is `0`.

so users lose their unclaimed rewards by withdrawing their funds.

## Recommendation
User’s unclaimed funds should be calculated and transferred before any actions that change user’s balance.
