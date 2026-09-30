# [M] DOS Attack in joinRushPool

## Summary
Severity: Medium
Contest weight: 0.4121
Dataset id: 4155
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
function joinRushPool(RushPoolKey[] calldata keys) external nonReentrant {
    uint256 balance = ERC20(address(keys[i].stakeToken)).balanceOf(msgSender);
    stakeAmountUpdated = remainderStakeAmount + balance >
        ? keys[i].stakeCap - remainderStakeAmount
        : balance;
    // ensure there is capacity left and that we're increasing the
    // user's stake
    // the user's stake may increase when either
    // 1) the user isn't staked yet or
    // 2) the user staked & hit the stake cap but more capacity has
    // opened up since then
    (stakeAmountUpdated == 0 || stakeAmountUpdated <= userState.stakeAmount)
    continue;
```
Attacker's steps:
Attacker observes a pending joinRushPool transaction
Attacker front-runs by calling joinRushPool to fill the pool to its cap
Victim's transaction reverts due to no remaining capacity
Attacker back-runs by calling exitRushPool to withdraw their stake
The attacker can repeat this pattern to consistently block other users from joining the pool. The only cost is gas fees for the sandwich transactions.

## Recommendation
It's recommended that minimum stake duration be added or an unstaking delay implemented.
