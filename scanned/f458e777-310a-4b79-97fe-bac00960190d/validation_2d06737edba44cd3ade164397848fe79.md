### Title
Rewards Permanently Locked in `KernelDepositPool` When `totalKernelStaked` Drops to Zero During Active Reward Period - (File: contracts/KERNEL/KernelDepositPool.sol)

### Summary
`KernelDepositPool` implements a Synthetix-style staking rewards mechanism. When `totalKernelStaked` reaches zero during an active reward distribution window, the `rewardPerToken()` accumulator stops advancing, causing all rewards that should have been distributed during that zero-staking interval to become permanently locked in the contract with no recovery path.

### Finding Description
`KernelDepositPool` tracks rewards using the standard Synthetix pattern: a global `rewardPerTokenStored` accumulator that advances at `rewardRate / totalKernelStaked` per second. The contract itself documents the flaw at lines 17–22:

> *"If `totalKernelStaked` ever hits zero during a reward distribution window, any remaining rewards for that period will stay locked in the contract."*

When `totalKernelStaked == 0`, the `rewardPerToken()` function short-circuits and returns the current `rewardPerTokenStored` unchanged. Meanwhile, `rewardRate` continues to tick and the reward tokens (already transferred into the contract by `notifyRewardAmount`) keep accumulating as unallocated balance. Because no user's `rewards[user]` mapping is ever credited for that interval, and because there is no admin sweep, rescue, or re-injection function for these stranded tokens, they are permanently frozen inside the contract.

The only mitigation mentioned is operational: the comment states that keeping at least 1 wei staked at all times prevents the issue. There is no on-chain enforcement of this invariant. [1](#0-0) [2](#0-1) 

### Impact Explanation
Any KERNEL rewards distributed during a zero-staking interval are permanently unrecoverable. The reward tokens sit in the contract with no function to sweep, redistribute, or refund them. This constitutes **permanent freezing of unclaimed yield** — Medium impact per the allowed scope.

### Likelihood Explanation
Any scenario where all stakers simultaneously exit during an active reward window triggers the bug. Realistic paths include:

- A single large staker who is the sole depositor calls `initiateWithdrawal` and waits out the delay, leaving `totalKernelStaked == 0` for the remainder of the reward period.
- Early-deployment periods where staker count is low and a coordinated or natural exit empties the pool.

The contract provides no on-chain guard (e.g., a minimum staked floor, or a `require(totalKernelStaked > 0)` before `notifyRewardAmount`) to prevent this state. [3](#0-2) 

### Recommendation
1. Add a `notifyRewardAmount` precondition: `require(totalKernelStaked > 0, "No stakers")`.
2. Alternatively, track the duration during which `totalKernelStaked == 0` and extend the reward window by that amount, or allow an admin to reclaim unallocated rewards via a dedicated rescue function.
3. Enforce a minimum staked amount on-chain rather than relying on an operational convention.

### Proof of Concept
1. Admin calls `notifyRewardAmount(1000e18)` with a 7-day duration. `rewardRate = 1000e18 / 7 days`.
2. Alice is the only staker with `balanceOf[Alice] = 100e18`, `totalKernelStaked = 100e18`.
3. After 3 days, Alice calls `initiateWithdrawal(100e18)`. After the withdrawal delay, she claims. `totalKernelStaked = 0`.
4. For the remaining 4 days, `rewardPerToken()` returns `rewardPerTokenStored` unchanged — no rewards are credited to anyone.
5. `≈ 571e18` reward tokens (`rewardRate * 4 days`) remain permanently locked in the contract. No function exists to recover them. [1](#0-0)

### Citations

**File:** contracts/KERNEL/KernelDepositPool.sol (L17-22)
```text
 * @dev Modified from https://github.com/Synthetixio/synthetix/blob/develop/contracts/StakingRewards.sol
 * @dev If `totalKernelStaked` ever hits zero during a reward distribution window, any remaining rewards
 *      for that period will stay locked in the contract. In this deployment, we're avoiding this issue by
 *      ensuring there are always some tokens staked before admin calls the `notifyRewardAmount` function,
 *      as well as for the entire duration of the reward period. Otherwise, staking just 1 wei by any address
 *      will ensure that the contract never has any unallocated rewards.
```

**File:** contracts/KERNEL/KernelDepositPool.sol (L62-109)
```text
    /// @notice The KERNEL token contract (used for staking)
    IERC20 public kernelToken;

    /// @notice The rewards token contract
    IERC20 public rewardsToken;

    /// @notice The duration of the rewards distribution
    uint256 public duration;

    /// @notice The timestamp when rewards distribution ends
    uint256 public finishAt;

    /// @notice The timestamp when the rewards were last updated
    uint256 public updatedAt;

    /// @notice The reward rate
    uint256 public rewardRate;

    /// @notice The reward per token stored
    uint256 public rewardPerTokenStored;

    /// @notice The latest rewardPerTokenStored checkpoint for each account. It gets updated on each user action
    mapping(address user => uint256 rewardPerTokenPaid) public userRewardPerTokenPaid;

    /// @notice Mapping of current accumulated rewards that have not been claimed for each user
    mapping(address user => uint256 reward) public rewards;

    /// @notice The total amount of staked KERNEL tokens
    uint256 public totalKernelStaked;

    /// @notice The balance of staked KERNEL tokens for each user
    mapping(address user => uint256 stakedBalance) public balanceOf;

    /// @notice Delay (in seconds) before withdrawals can be claimed after initiation
    uint256 public withdrawalDelay;

    /// @notice A global incremental counter for withdrawal IDs
    uint256 public withdrawalCounter;

    /// @notice Mapping of withdrawal IDs to their withdrawal info
    mapping(uint256 withdrawalId => Withdrawal withdrawal) public withdrawals;

    /// @notice Mapping of user addresses to their withdrawal IDs
    mapping(address user => uint256[] withdrawalIds) public userWithdrawalIds;

    /// @notice The maximum number of withdrawals that any user can have open (unclaimed) at any time
    uint256 public maxNumberOfWithdrawalsPerUser;

```
