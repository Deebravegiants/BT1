### Title
Reward Sandwich Attack via Front-Running `notifyRewardAmount` with No Warmup Period and Uninitialized `withdrawalDelay` — (File: contracts/KERNEL/KernelDepositPool.sol)

---

### Summary

`KernelDepositPool` implements a Synthetix-style staking rewards model. There is no warmup period before rewards begin accruing, and `withdrawalDelay` is never set in `initialize()`, defaulting to `0`. An unprivileged attacker can front-run the admin's `notifyRewardAmount` call, immediately earn a disproportionate share of the new reward period, claim those rewards, and exit — stealing yield from legitimate long-term stakers.

---

### Finding Description

The `stake()` function is permissionless and applies the `updateReward` modifier, which snapshots `userRewardPerTokenPaid[attacker] = rewardPerTokenStored` at the moment of staking. [1](#0-0) 

When `notifyRewardAmount` is subsequently confirmed, it resets `rewardRate`, `finishAt`, and `updatedAt` to the new period's values. [2](#0-1) 

Because the attacker staked immediately before this call, their `userRewardPerTokenPaid` is set to the pre-call `rewardPerTokenStored`. All rewards accrued from the very start of the new period are therefore attributed to the attacker proportional to their share of `totalKernelStaked`. [3](#0-2) 

The critical amplifier is that `withdrawalDelay` is **never initialized** in `initialize()`: [4](#0-3) 

It defaults to `0`. `initiateWithdrawal` computes `unlockTime = block.timestamp + withdrawalDelay`, which equals `block.timestamp` when `withdrawalDelay == 0`. The `claimWithdrawal` guard `block.timestamp < withdrawal.unlockTime` is then always false, making the withdrawal immediately claimable in the same block. [5](#0-4) [6](#0-5) 

Even if `setWithdrawalDelay` is later called to a non-zero value, the absence of any warmup period means the attack remains viable — the attacker simply holds their stake for `withdrawalDelay` seconds, earning rewards the entire time, then exits. The `setWithdrawalDelay` setter enforces `> 0` but this is irrelevant if the function is never called before `notifyRewardAmount`. [7](#0-6) 

---

### Impact Explanation

**High — Theft of unclaimed yield.**

Legitimate stakers who have been staked for the entire reward period receive a diluted share of rewards. The attacker earns rewards proportional to `attackerStake / (attackerStake + legitimateStake)` for the duration they remain staked, then exits with both their KERNEL principal and the stolen yield. With `withdrawalDelay == 0`, the entire attack (stake → earn → claim → withdraw) can be executed across two consecutive blocks.

---

### Likelihood Explanation

**Medium.** The attacker must:
1. Monitor the mempool for a pending `notifyRewardAmount` transaction (trivially observable on-chain).
2. Hold sufficient KERNEL to make dilution profitable.

No privileged access is required. The `stake()` function is fully permissionless. The default `withdrawalDelay == 0` state requires no special timing — the attacker can exit immediately after accumulating any non-zero rewards.

---

### Recommendation

1. **Initialize `withdrawalDelay` to a non-zero value inside `initialize()`** (e.g., 7 days) so the contract is never deployed in an immediately-withdrawable state.
2. **Implement a warmup/cooldown period**: newly staked tokens should not accrue rewards until at least one full reward epoch has elapsed since staking, analogous to the "reward periods" fix adopted in the referenced GMX report.
3. **Alternatively**, snapshot eligible stakers at the time `notifyRewardAmount` is called and only distribute rewards to addresses that were staked before that snapshot.

---

### Proof of Concept

**Setup**: Alice has staked `100e18` KERNEL. Admin is about to call `notifyRewardAmount(1_000_000e18)` with `duration = 30 days`. `withdrawalDelay` is `0` (never initialized).

**Attack**:

```
Block N:
  Attacker observes pending notifyRewardAmount(1_000_000e18) in mempool.
  Attacker calls stake(9_900e18).
  → totalKernelStaked = 10_000e18 (attacker: 99%, Alice: 1%)
  → userRewardPerTokenPaid[attacker] = rewardPerTokenStored (current, pre-new-period)

Block N (same block, higher gas):
  notifyRewardAmount(1_000_000e18) confirms.
  → rewardRate = 1_000_000e18 / (30 days) ≈ 385e12 tokens/sec
  → finishAt = block.timestamp + 30 days

Block N+K (some blocks later):
  Attacker calls getReward()
  → earned(attacker) ≈ 0.99 × rewardRate × elapsed_time
  → Attacker receives ~99% of all rewards accrued so far.

  Attacker calls initiateWithdrawal(9_900e18)
  → unlockTime = block.timestamp + 0 = block.timestamp

  Attacker calls claimWithdrawal(withdrawalId)
  → block.timestamp >= unlockTime → passes immediately
  → Attacker receives 9_900e18 KERNEL back.
```

**Result**: Alice, who was the sole legitimate staker, receives only ~1% of the rewards she was entitled to. The attacker profits the difference with zero capital lockup cost (when `withdrawalDelay == 0`). [1](#0-0) [8](#0-7) [9](#0-8) [5](#0-4) [6](#0-5)

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

**File:** contracts/KERNEL/KernelDepositPool.sol (L344-358)
```text
    function claimWithdrawal(uint256 _withdrawalId) external nonReentrant {
        Withdrawal storage withdrawal = withdrawals[_withdrawalId];

        if (withdrawal.user == address(0)) {
            revert WithdrawalDoesNotExist();
        }

        if (withdrawal.user != msg.sender) {
            revert NotYourWithdrawal();
        }

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

**File:** contracts/KERNEL/KernelDepositPool.sol (L408-423)
```text
    function rewardPerToken() public view returns (uint256) {
        if (totalKernelStaked == 0) {
            return rewardPerTokenStored;
        }
        return rewardPerTokenStored + (rewardRate * (lastTimeRewardApplicable() - updatedAt) * DECIMAL_PRECISION)
            / totalKernelStaked;
    }

    /**
     * @notice Calculates the amount of rewards earned by an account
     * @param _account The account to for which rewards are calculated
     * @return The earned reward amount
     */
    function earned(address _account) public view returns (uint256) {
        return (balanceOf[_account] * (rewardPerToken() - userRewardPerTokenPaid[_account]) / DECIMAL_PRECISION)
            + rewards[_account];
```

**File:** contracts/KERNEL/KernelDepositPool.sol (L566-591)
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
```

**File:** contracts/KERNEL/KernelDepositPool.sol (L598-604)
```text
    function setWithdrawalDelay(uint256 _withdrawalDelay) external onlyRole(DEFAULT_ADMIN_ROLE) {
        if (_withdrawalDelay == 0) revert InvalidWithdrawalDelay();
        if (_withdrawalDelay > MAX_WITHDRAWAL_DELAY) revert MaximumWithdrawalDelayExceeded();

        withdrawalDelay = _withdrawalDelay;
        emit WithdrawalDelayUpdated(_withdrawalDelay);
    }
```
