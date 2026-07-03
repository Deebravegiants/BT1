### Title
Front-Running `notifyRewardAmount` Enables Disproportionate Reward Capture with Zero-Delay Exit - (File: contracts/KERNEL/KernelDepositPool.sol)

---

### Summary

`KernelDepositPool.notifyRewardAmount` is a privileged admin transaction that is visible in the public mempool before execution. Because there is no mechanism to freeze staking balances before the reward period begins, and because `withdrawalDelay` is never initialized in `initialize` (defaulting to `0`), an attacker can front-run the admin transaction by staking a large amount of KERNEL tokens, capture a disproportionate share of the entire reward period's emissions, and exit the position in the same block as reward collection — stealing yield from all existing legitimate stakers.

---

### Finding Description

`KernelDepositPool` is a Synthetix-style staking rewards contract. The admin calls `notifyRewardAmount` to begin a new reward period, which sets `rewardRate = receivedAmount / duration` and `finishAt = block.timestamp + duration`. [1](#0-0) 

The reward each staker earns per second is proportional to `balanceOf[user] / totalKernelStaked`. Because `notifyRewardAmount` is submitted as a regular Ethereum transaction, it is visible in the mempool before it is mined. An attacker can observe it and submit `stake(largeAmount)` with a higher gas price, causing it to execute first. [2](#0-1) 

After the attacker's `stake` executes, `totalKernelStaked` is inflated. When `notifyRewardAmount` then executes, the `rewardRate` is fixed for the entire duration. The attacker's share of every second of emissions is `attackerStake / (legitimateStake + attackerStake)`, which can approach 100% with sufficient capital.

The second structural flaw compounds the attack: `withdrawalDelay` is a state variable declared at line 96 but is **never assigned** in the `initialize` function. [3](#0-2) 

It therefore defaults to `0`. In `claimWithdrawal`, the only guard is: [4](#0-3) 

With `withdrawalDelay = 0`, `unlockTime = block.timestamp + 0 = block.timestamp`, so `block.timestamp >= unlockTime` is immediately satisfied. The attacker can call `initiateWithdrawal` and `claimWithdrawal` in the same block as `getReward`, completing the full attack atomically (or across two blocks with no meaningful delay). [5](#0-4) 

---

### Impact Explanation

**High — Theft of unclaimed yield.**

Existing stakers who deposited KERNEL tokens in good faith have their proportional reward share diluted for the entire reward period. The attacker captures the stolen yield via `getReward()` and recovers their principal immediately via `initiateWithdrawal` + `claimWithdrawal`. The loss to legitimate stakers is bounded by the total reward amount for the period and scales with the attacker's capital relative to the existing pool. [6](#0-5) 

---

### Likelihood Explanation

**Medium.** The attack requires:
1. Capital to stake (returned at the end, so it is a flash-loan-compatible or self-funded operation).
2. Mempool visibility of the admin's `notifyRewardAmount` transaction (trivially available on all public EVM chains).
3. Ability to submit a transaction with higher gas (standard MEV tooling).

There is no technical barrier. The attack is profitable whenever the reward amount for the period exceeds the gas cost of the two transactions. Given that `notifyRewardAmount` is called periodically to fund ongoing staking incentives, every invocation is an opportunity.

---

### Recommendation

1. **Snapshot-based eligibility**: Record a `stakingStartTime` per user and only count stake toward rewards if it was deposited before the current reward period began (i.e., before `notifyRewardAmount` was called). Alternatively, require a minimum staking duration before rewards accrue.

2. **Initialize `withdrawalDelay`**: Set a non-zero `withdrawalDelay` in `initialize` to prevent same-block exit. The `setWithdrawalDelay` function already enforces `_withdrawalDelay > 0`, but this guard is bypassed entirely because the initial value is never set. [7](#0-6) 

3. **Two-step reward start**: Separate the reward funding step (transferring tokens) from the reward activation step (setting `rewardRate`), with a time delay between them, so that the exact activation block cannot be predicted and front-run.

---

### Proof of Concept

```
Block N (mempool): Admin submits notifyRewardAmount(1_000_000e18)

Block N (attacker front-runs):
  tx1: KERNEL.approve(KernelDepositPool, 10_000_000e18)
  tx2: KernelDepositPool.stake(10_000_000e18)
       → balanceOf[attacker] = 10_000_000e18
       → totalKernelStaked = 10_000_000e18 + legitimateStake (e.g. 1_000_000e18)
       → attacker share ≈ 90.9%

Block N (admin tx executes after attacker):
  notifyRewardAmount(1_000_000e18)
       → rewardRate = 1_000_000e18 / duration
       → attacker earns ≈ 909_090e18 of the 1_000_000e18 reward pool

After duration (or any time later):
  KernelDepositPool.getReward()
       → attacker receives ≈ 909_090e18 reward tokens

  KernelDepositPool.initiateWithdrawal(10_000_000e18)
       → unlockTime = block.timestamp + 0 = block.timestamp

  KernelDepositPool.claimWithdrawal(withdrawalId)
       → block.timestamp >= unlockTime → passes immediately
       → attacker recovers 10_000_000e18 KERNEL principal

Net result: attacker steals ≈ 909_090e18 reward tokens from legitimate stakers
            at zero net capital cost (principal fully recovered).
``` [8](#0-7) [9](#0-8)

### Citations

**File:** contracts/KERNEL/KernelDepositPool.sol (L259-271)
```text
    function initialize(address _admin, address _kernelToken, address _rewardToken) external initializer {
        UtilLib.checkNonZeroAddress(_admin);
        UtilLib.checkNonZeroAddress(_kernelToken);
        UtilLib.checkNonZeroAddress(_rewardToken);

        __AccessControl_init();
        __ReentrancyGuard_init();

        _setupRole(DEFAULT_ADMIN_ROLE, _admin);

        kernelToken = IERC20(_kernelToken);
        rewardsToken = IERC20(_rewardToken);
    }
```

**File:** contracts/KERNEL/KernelDepositPool.sol (L281-289)
```text
    function stake(uint256 _amount) external nonReentrant updateReward(msg.sender) {
        if (_amount == 0) revert AmountZero();

        balanceOf[msg.sender] += _amount;
        totalKernelStaked += _amount;
        kernelToken.safeTransferFrom(msg.sender, address(this), _amount);

        emit Staked(msg.sender, _amount);
    }
```

**File:** contracts/KERNEL/KernelDepositPool.sol (L320-338)
```text
    function initiateWithdrawal(uint256 _amount) external nonReentrant updateReward(msg.sender) {
        if (_amount == 0) revert AmountZero();
        if (balanceOf[msg.sender] < _amount) revert InsufficientStakedBalance();
        if (userWithdrawalIds[msg.sender].length >= maxNumberOfWithdrawalsPerUser) revert WithdrawalLimitReached();

        balanceOf[msg.sender] -= _amount;
        totalKernelStaked -= _amount;

        // Create a withdrawal record
        uint256 withdrawalId = ++withdrawalCounter;
        uint256 unlockTime = block.timestamp + withdrawalDelay;

        withdrawals[withdrawalId] = Withdrawal({
            user: msg.sender, amount: _amount, unlockTime: unlockTime, claimed: false, withdrawalId: withdrawalId
        });
        userWithdrawalIds[msg.sender].push(withdrawalId);

        emit WithdrawalInitiated(msg.sender, _amount, withdrawalId, unlockTime);
    }
```

**File:** contracts/KERNEL/KernelDepositPool.sol (L355-357)
```text
        if (block.timestamp < withdrawal.unlockTime) {
            revert WithdrawalNotReady();
        }
```

**File:** contracts/KERNEL/KernelDepositPool.sol (L382-390)
```text
    function getReward() external nonReentrant updateReward(msg.sender) {
        uint256 rewardAmount = rewards[msg.sender];

        if (rewardAmount > 0) {
            rewards[msg.sender] = 0;
            rewardsToken.safeTransfer(msg.sender, rewardAmount);
            emit RewardsClaimed(msg.sender, rewardAmount);
        }
    }
```

**File:** contracts/KERNEL/KernelDepositPool.sol (L408-413)
```text
    function rewardPerToken() public view returns (uint256) {
        if (totalKernelStaked == 0) {
            return rewardPerTokenStored;
        }
        return rewardPerTokenStored + (rewardRate * (lastTimeRewardApplicable() - updatedAt) * DECIMAL_PRECISION)
            / totalKernelStaked;
```

**File:** contracts/KERNEL/KernelDepositPool.sol (L566-592)
```text
    function notifyRewardAmount(uint256 _amount) external onlyRole(DEFAULT_ADMIN_ROLE) updateReward(address(0)) {
        if (_amount == 0) revert AmountZero();

        // Prevent starting a reward period when no tokens are staked to avoid unallocated rewards
        if (totalKernelStaked == 0) revert NoStakedTokens();

        // Transfer reward tokens into the contract
        uint256 balanceBefore = rewardsToken.balanceOf(address(this));
        rewardsToken.safeTransferFrom(msg.sender, address(this), _amount);
        uint256 balanceAfter = rewardsToken.balanceOf(address(this));
        // Calculate the actual amount of tokens received in case of a transfer fee (tax)
        uint256 receivedAmount = balanceAfter - balanceBefore;

        if (block.timestamp >= finishAt) {
            rewardRate = receivedAmount / duration;
        } else {
            uint256 remaining = (finishAt - block.timestamp) * rewardRate;
            rewardRate = (receivedAmount + remaining) / duration;
        }

        if (rewardRate == 0) revert RewardRateZero();

        finishAt = block.timestamp + duration;
        updatedAt = block.timestamp;

        emit NotifyRewardAmount(receivedAmount, finishAt);
    }
```

**File:** contracts/KERNEL/KernelDepositPool.sol (L598-603)
```text
    function setWithdrawalDelay(uint256 _withdrawalDelay) external onlyRole(DEFAULT_ADMIN_ROLE) {
        if (_withdrawalDelay == 0) revert InvalidWithdrawalDelay();
        if (_withdrawalDelay > MAX_WITHDRAWAL_DELAY) revert MaximumWithdrawalDelayExceeded();

        withdrawalDelay = _withdrawalDelay;
        emit WithdrawalDelayUpdated(_withdrawalDelay);
```
