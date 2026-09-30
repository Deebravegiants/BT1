# [M] `stakerewardV2pool.withdraw

## Summary
Severity: Medium
Contest weight: 0.7112
Dataset id: 18816
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability resides in the staking pool contract where the withdraw function does not enforce the boost lock period that is intended to restrict fund withdrawals until a predefined unlock time. When a user stakes tokens, they can optionally lock their position for a chosen duration to obtain a higher reward boost. The boost logic records an unlock timestamp for each account, and the protocol’s economic design assumes that users cannot withdraw their principal or claim the boosted rewards before this timestamp. However, the withdraw implementation only checks that the withdrawal amount is greater than zero and then updates internal balances and transfers the staking token, completely omitting any verification of the boost lock. As a result, a user can stake, set the longest lock to maximize the boost, and immediately call withdraw to retrieve both the original stake and the inflated reward amount, despite the lock not having expired. This can be exploited repeatedly: the attacker stakes a small amount, locks for the maximum boost, immediately withdraws, and repeats the cycle, extracting boosted rewards without ever locking capital. The impact is a distortion of the reward distribution model, leading to an unintended outflow of reward tokens from the pool, erosion of incentives for honest participants, and potential depletion of the reward reserve. The issue manifests whenever a user who has an active boost attempts to withdraw; it does not depend on the specific lock duration chosen. All participants of the protocol are affected because the reward pool may be drained, reducing the returns for legitimate stakers. The flaw was discovered during a manual audit by reviewing the withdraw function and noticing the absence of a lock‑time check that is present in other parts of the contract, such as the boost contract. It can be hard to notice because the function appears to perform a standard withdrawal and the missing check does not raise a compilation warning; only a careful inspection of the business logic reveals the inconsistency. To remediate, the withdraw function should include a requirement that the current block timestamp is greater than or equal to the unlock time returned by the boost contract for the caller, thereby enforcing the intended lock‑in period before allowing any token transfer. This aligns the contract’s behavior with its economic assumptions and prevents users from receiving boosted rewards without honoring the lock period.

## Proof of Concept
`withdraw()` should prevent withdrawals during the boost lock, but there is no such logic.

The below steps show how users can charge more rewards without locking their funds.

  1. Alice stakes their funds using [stake()](https://github.com/code-423n4/2023-06-lybra/blob/5d70170f2c68dbd3f7b8c0c8fd6b0b2218784ea6/contracts/lybra/miner/stakerewardV2pool.sol#L83).
  2. They set the longest lock duration to get the highest boost using [setLockStatus()](https://github.com/code-423n4/2023-06-lybra/blob/5d70170f2c68dbd3f7b8c0c8fd6b0b2218784ea6/contracts/lybra/miner/esLBRBoost.sol#L38).
  3. After that, when they want to withdraw their staking funds, they call [withdraw()](https://github.com/code-423n4/2023-06-lybra/blob/5d70170f2c68dbd3f7b8c0c8fd6b0b2218784ea6/contracts/lybra/miner/stakerewardV2pool.sol#L93).

```solidity
function withdraw(uint256 _amount) external updateReward(msg.sender) {
    require(_amount > 0, "amount = 0");
    balanceOf[msg.sender] -= _amount;
    totalSupply -= _amount;
    stakingToken.transfer(msg.sender, _amount);
    emit WithdrawToken(msg.sender, _amount, block.timestamp);
}
```

  4. Then, the highest boost factor will be applied to their rewards in [earned()](https://github.com/code-423n4/2023-06-lybra/blob/5d70170f2c68dbd3f7b8c0c8fd6b0b2218784ea6/contracts/lybra/miner/stakerewardV2pool.sol#L106) and they can withdraw all of their staking funds and rewards immediately without checking any lock duration.

```solidity
// Calculates and returns the earned rewards for a user
function earned(address _account) public view returns (uint256) {
    return ((balanceOf[_account] * getBoost(_account) * (rewardPerToken() - userRewardPerTokenPaid[_account])) / 1e38) + rewards[_account];
}
```

## Recommendation
`withdraw()` should check the boost lock like this:

```solidity
function withdraw(uint256 _amount) external updateReward(msg.sender) {
    require(block.timestamp >= esLBRBoost.getUnlockTime(msg.sender), "Your lock-in period has not ended.");

    require(_amount > 0, "amount = 0");
    balanceOf[msg.sender] -= _amount;
    totalSupply -= _amount;
    stakingToken.transfer(msg.sender, _amount);
    emit WithdrawToken(msg.sender, _amount, block.timestamp);
}
```
