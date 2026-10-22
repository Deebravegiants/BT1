# [M] `MuteAmplifier.rescueTokens

## Summary
Severity: Medium
Contest weight: 0.5926
Dataset id: 18265
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The MuteAmplifier contract contains a flaw in the rescueTokens function that governs the withdrawal of the muteToken used as staking rewards. The function is intended to prevent the contract owner from taking tokens that belong to stakers, but the implementation fails in two ways. First, when the contract reports zero stakers (totalStakers == 0) the function does not perform any balance check before allowing a rescue, which means an attacker can call rescueTokens and withdraw any amount of muteToken even while the staking period is still active. Second, when there are active stakers the require statement subtracts only totalRewards minus totalClaimedRewards from the contract balance, ignoring the amount already reclaimed to the treasury (totalReclaimed). Because totalReclaimed is part of the reward pool, the missing subtraction permits the caller to withdraw more than the unclaimed portion, and it also leaves a portion of rewards permanently locked because the rescue logic never accounts for them. The root cause is an incomplete accounting model and a missing conditional branch for the zero‑staker case. An attacker who can invoke rescueTokens can therefore drain rewards before users have earned them, or withdraw an amount that exceeds the true unclaimed reward pool, causing the reward distribution to break. Stakers may see their expected payouts reduced to zero or notice that their balances do not increase after the staking period, while the protocol may retain a residual amount of muteToken that can never be claimed. The issue was discovered during a Code4rena audit by comparing the rescueTokens checks with the accounting variables used elsewhere in the contract. It is subtle because the function contains a require statement that appears to protect the rewards, yet the condition is mathematically incorrect and the special case of zero stakers is omitted, making the bug easy to overlook in testing. The appropriate fix is to extend the balance check to subtract totalReclaimed as well, and to add a safeguard that, when totalStakers is zero, the amount rescued cannot exceed the remaining reward pool (totalRewards – totalClaimedRewards – totalReclaimed) or is prohibited until the staking end time. This brings the rescue logic in line with the contract’s accounting model and prevents unauthorized or excessive withdrawals, preserving the integrity of the reward system.

## Proof of Concept
`rescueTokens()` checks the below condition to rescue `muteToken`.
```solidity
    else if (tokenToRescue == muteToken) {
        if (totalStakers > 0) {
            require(amount <= IERC20(muteToken).balanceOf(address(this)).sub(totalRewards.sub(totalClaimedRewards)),
                "MuteAmplifier::rescueTokens: that muteToken belongs to stakers"
            );
        }
    }
```
But there are 2 problems.

  1. Currently, it doesn’t check anything when `totalStakers == 0`. So some parts(or 100%) of rewards can be withdrawn before the staking period. In this case, the reward system won’t work properly due to the lack of rewards.
  2. It checks the wrong condition when `totalStakers > 0` as well. As we can see [here](https://github.com/code-423n4/2023-03-mute/blob/4d8b13add2907b17ac14627cfa04e0c3cc9a2bed/contracts/amplifier/MuteAmplifier.sol#L241), some remaining rewards are tracked using `totalReclaimed` and transferred to treasury directly. So we should consider this amount as well.

## Recommendation
It should be modified like the below.
```solidity
    else if (tokenToRescue == muteToken) {
        if (totalStakers > 0) { //should check totalReclaimed as well
            require(amount <= IERC20(muteToken).balanceOf(address(this)).sub(totalRewards.sub(totalClaimedRewards).sub(totalReclaimed)),
                "MuteAmplifier::rescueTokens: that muteToken belongs to stakers"
            );
        }
        else if(block.timestamp <= endTime) { //no stakers but staking is still active, should maintain totalRewards
            require(amount <= IERC20(muteToken).balanceOf(address(this)).sub(totalRewards),
                "MuteAmplifier::rescueTokens: that muteToken belongs to stakers"
            );
        }
    }
```
