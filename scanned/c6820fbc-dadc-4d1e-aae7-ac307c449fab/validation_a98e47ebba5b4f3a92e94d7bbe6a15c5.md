### Title
Missing Staked-vs-Reward Balance Distinction in `notifyRewardAmount` Allows Reward Overclaim Into Staked Principal - (File: contracts/KERNEL/KernelDepositPool.sol)

### Summary
`KernelDepositPool` operates with `kernelToken` (staking) and `rewardsToken` (rewards) that can be configured as the same token. The `notifyRewardAmount` function is missing the standard Synthetix solvency check (`rewardRate * duration <= rewardsToken.balanceOf(address(this)) - totalKernelStaked`), and `getReward()` transfers reward tokens without verifying that the reward amount does not exceed the reward-only portion of the contract balance. This is the direct analog to the reported ShyftStaking vulnerability.

### Finding Description

`KernelDepositPool` is initialized with two separate token addresses:

```solidity
function initialize(address _admin, address _kernelToken, address _rewardToken) external initializer {
    kernelToken = IERC20(_kernelToken);
    rewardsToken = IERC20(_rewardToken);
}
```

There is no guard preventing `_kernelToken == _rewardToken`. When they are the same token, the contract's balance holds both staked principal (`totalKernelStaked`) and reward tokens in a single undifferentiated pool.

The `notifyRewardAmount` function sets `rewardRate` but performs no check that the total promised rewards (`rewardRate * duration`) do not exceed the reward-only portion of the balance:

```solidity
if (block.timestamp >= finishAt) {
    rewardRate = receivedAmount / duration;
} else {
    uint256 remaining = (finishAt - block.timestamp) * rewardRate;
    rewardRate = (receivedAmount + remaining) / duration;
}
if (rewardRate == 0) revert RewardRateZero();
```

The standard Synthetix guard — `require(rewardRate * duration <= rewardsToken.balanceOf(address(this)))` — is entirely absent. When `kernelToken == rewardsToken`, the correct guard must be:

```
rewardRate * duration <= rewardsToken.balanceOf(address(this)) - totalKernelStaked
```

because `rewardsToken.balanceOf(address(this))` includes staked principal. Without this guard, the `else` branch can set a `rewardRate` such that `rewardRate * duration` exceeds the reward-only balance (e.g., when `remaining` from a prior period is rolled forward while the actual reward balance has been partially drained by prior `getReward()` calls).

`getReward()` then transfers the computed reward amount with no balance guard:

```solidity
function getReward() external nonReentrant updateReward(msg.sender) {
    uint256 rewardAmount = rewards[msg.sender];
    if (rewardAmount > 0) {
        rewards[msg.sender] = 0;
        rewardsToken.safeTransfer(msg.sender, rewardAmount);
        emit RewardsClaimed(msg.sender, rewardAmount);
    }
}
```

There is no check `rewardAmount <= rewardsToken.balanceOf(address(this)) - totalKernelStaked`. When `kernelToken == rewardsToken`, this transfer draws from the combined pool, which includes staked principal. Early reward claimants drain the reward portion; later claimants' `safeTransfer` calls succeed by consuming staked principal, leaving stakers unable to recover their full deposit.

The protocol's own documentation defines the error `RewardAmountGreaterThanBalance` but it is never referenced in the actual contract source, confirming the check was intended but omitted.

### Impact Explanation

When `kernelToken == rewardsToken`:
- Reward claimants who call `getReward()` after the reward-only balance is exhausted receive tokens that belong to stakers.
- Stakers who subsequently call `claimWithdrawal()` receive less than their deposited principal, or the call reverts entirely.
- This constitutes **theft of unclaimed yield** (reward claimants receive staked principal) and potential **protocol insolvency** (stakers cannot recover principal).

### Likelihood Explanation

The `initialize` function places no constraint preventing `_kernelToken == _rewardToken`. A self-staking KERNEL rewards model (stake KERNEL, earn KERNEL) is a common and natural deployment choice for this contract. Once deployed with the same token, the vulnerability is latent and activates whenever the reward-only balance is insufficient to cover all outstanding `rewards[user]` entries — a condition reachable through normal user interactions (`getReward()` calls) without any privileged action beyond the initial (legitimate) `notifyRewardAmount` call.

### Recommendation

1. Add the solvency check in `notifyRewardAmount`, distinguishing staked from reward funds when the tokens are the same:

```solidity
uint256 rewardBalance = (address(rewardsToken) == address(kernelToken))
    ? rewardsToken.balanceOf(address(this)) - totalKernelStaked
    : rewardsToken.balanceOf(address(this));
if (rewardRate * duration > rewardBalance) revert RewardAmountGreaterThanBalance();