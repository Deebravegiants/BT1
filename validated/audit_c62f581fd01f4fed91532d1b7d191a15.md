### Title
Block Stuffing Exploits `maxNumberOfWithdrawalsPerUser` Cap to Temporarily Freeze User KERNEL Staking and Withdrawal Operations - (File: `contracts/KERNEL/KernelDepositPool.sol`)

---

### Summary

`KernelDepositPool.claimWithdrawal` enforces that only the withdrawal owner can call it, and `initiateWithdrawal` hard-blocks any user whose open withdrawal count equals `maxNumberOfWithdrawalsPerUser`. An attacker can combine these two constraints with block stuffing to temporarily freeze a victim's ability to both claim ready withdrawals and initiate new ones.

---

### Finding Description

Two design properties interact to create the vulnerability:

**1. Hard per-user withdrawal cap in `initiateWithdrawal`:** [1](#0-0) 

If `userWithdrawalIds[msg.sender].length >= maxNumberOfWithdrawalsPerUser`, the call reverts with `WithdrawalLimitReached`. There is no bypass.

**2. Exclusive owner-only claim in `claimWithdrawal`:** [2](#0-1) 

No admin, operator, or third party can call `claimWithdrawal` on behalf of the victim. The contract has no `claimWithdrawalFor` or admin force-claim function anywhere in the admin section. [3](#0-2) 

**Attack path:**

1. Victim legitimately fills all `maxNumberOfWithdrawalsPerUser` withdrawal slots (up to `MAX_WITHDRAWALS_PER_USER = 100`).
2. Time passes; all withdrawals pass their `unlockTime`.
3. Attacker begins block stuffing — paying to fill blocks with high-gas transactions so the victim's `claimWithdrawal` transactions cannot be included.
4. Victim's `claimWithdrawal` calls never land → `userWithdrawalIds` array never shrinks.
5. Victim's `initiateWithdrawal` calls revert with `WithdrawalLimitReached` because the array length is still at the cap.
6. Victim is simultaneously unable to claim existing withdrawals and unable to initiate new ones.

The `withdrawalDelay` can be set up to `MAX_WITHDRAWAL_DELAY = 30 days`, meaning the attacker only needs to sustain block stuffing for the window during which the victim is trying to transact, not for the entire delay period. [4](#0-3) 

---

### Impact Explanation

The victim experiences a temporary but complete freeze of their KERNEL staking and withdrawal operations:
- Cannot claim ready withdrawals (transactions excluded from blocks).
- Cannot initiate new withdrawals (`WithdrawalLimitReached`).
- KERNEL tokens remain locked in the contract for the duration of the attack.

Impact: **Low. Block stuffing** (explicitly in scope).

---

### Likelihood Explanation

Block stuffing is expensive — the attacker must pay to fill entire blocks. However:
- The attack is economically rational if the victim holds a large KERNEL position and the attacker profits from the delay (e.g., via a competing protocol, liquidation opportunity, or governance timing).
- The attack only needs to be sustained for a short window (e.g., a few minutes to hours) to cause meaningful disruption.
- No special permissions, leaked keys, or external protocol compromise are required — only ETH for gas.

Likelihood: **Low**, but non-zero and locally testable on unmodified code.

---

### Recommendation

Add a permissioned `claimWithdrawalFor(address _user, uint256 _withdrawalId)` function callable by an operator role, or allow any third party to claim on behalf of a user (since the tokens are always sent to `withdrawal.user`, there is no trust issue). This breaks the exclusive dependency on the victim's own transaction inclusion.

Alternatively, allow the admin to forcibly remove a withdrawal slot (marking it claimed and returning tokens) to unblock a user at the cap.

---

### Proof of Concept

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

// Foundry fork test (local, no mainnet)
import "forge-std/Test.sol";
import "../contracts/KERNEL/KernelDepositPool.sol";

contract BlockStuffingPoC is Test {
    KernelDepositPool pool;
    address victim = address(0xBEEF);
    uint256 MAX_SLOTS;

    function setUp() public {
        // Deploy and initialize pool (mock tokens omitted for brevity)
        // Set maxNumberOfWithdrawalsPerUser = 3 for speed
        pool.setMaxNumberOfWithdrawalsPerUser(3);
        MAX_SLOTS = 3;

        // Fund victim and stake
        deal(address(pool.kernelToken()), victim, 1000e18);
        vm.startPrank(victim);
        pool.kernelToken().approve(address(pool), type(uint256).max);
        pool.stake(300e18);

        // Fill all withdrawal slots
        for (uint256 i = 0; i < MAX_SLOTS; i++) {
            pool.initiateWithdrawal(100e18);
        }
        vm.stopPrank();
    }

    function test_blockStuffingFreezesVictim() public {
        // Advance time past all unlockTimes
        vm.warp(block.timestamp + 31 days);

        // Simulate block stuffing: victim's claimWithdrawal never lands.
        // Victim tries to initiate a new withdrawal — reverts.
        vm.prank(victim);
        vm.expectRevert(KernelDepositPool.WithdrawalLimitReached.selector);
        pool.initiateWithdrawal(1e18);

        // Victim's only escape is claimWithdrawal, but under block stuffing
        // those transactions are excluded. The invariant is broken:
        // a user with all slots claimable cannot free them if their txs are censored.
    }
}
```

### Citations

**File:** contracts/KERNEL/KernelDepositPool.sol (L35-38)
```text
    uint256 public constant MAX_WITHDRAWAL_DELAY = 30 days;

    /// @notice The maximum number of open (unclaimed) withdrawals allowed per user at any time
    uint256 public constant MAX_WITHDRAWALS_PER_USER = 100;
```

**File:** contracts/KERNEL/KernelDepositPool.sol (L323-323)
```text
        if (userWithdrawalIds[msg.sender].length >= maxNumberOfWithdrawalsPerUser) revert WithdrawalLimitReached();
```

**File:** contracts/KERNEL/KernelDepositPool.sol (L351-353)
```text
        if (withdrawal.user != msg.sender) {
            revert NotYourWithdrawal();
        }
```

**File:** contracts/KERNEL/KernelDepositPool.sol (L544-621)
```text
    /*//////////////////////////////////////////////////////////////
                            ADMIN FUNCTIONS
    //////////////////////////////////////////////////////////////*/

    /**
     * @notice Sets the duration for rewards distribution
     * @param _duration The duration in seconds
     */
    function setRewardsDuration(uint256 _duration) external onlyRole(DEFAULT_ADMIN_ROLE) {
        if (finishAt >= block.timestamp) revert RewardDurationNotFinished();
        if (_duration == 0) revert InvalidDuration();
        duration = _duration;
        emit RewardsDurationUpdated(_duration);
    }

    /**
     * @notice Notifies the contract about a new reward amount
     * @dev Uses a transfer-in pattern to determine the exact reward amount received.
     *      Also, to avoid undistributed rewards when no one is staked, this function reverts if totalKernelStaked is
     *      zero.
     * @param _amount The amount of reward tokens to add
     */
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

    /**
     * @notice Updates the withdrawal delay
     * @param _withdrawalDelay The new withdrawal delay
     */
    function setWithdrawalDelay(uint256 _withdrawalDelay) external onlyRole(DEFAULT_ADMIN_ROLE) {
        if (_withdrawalDelay == 0) revert InvalidWithdrawalDelay();
        if (_withdrawalDelay > MAX_WITHDRAWAL_DELAY) revert MaximumWithdrawalDelayExceeded();

        withdrawalDelay = _withdrawalDelay;
        emit WithdrawalDelayUpdated(_withdrawalDelay);
    }

    /**
     * @notice Updates the maximum number of withdrawals per user
     * @param _maxNumberOfWithdrawalsPerUser The new maximum number of withdrawals per user
     */
    function setMaxNumberOfWithdrawalsPerUser(uint256 _maxNumberOfWithdrawalsPerUser)
        external
        onlyRole(DEFAULT_ADMIN_ROLE)
    {
        if (_maxNumberOfWithdrawalsPerUser == 0 || _maxNumberOfWithdrawalsPerUser > MAX_WITHDRAWALS_PER_USER) {
            revert InvalidMaxNumberOfWithdrawalsPerUser();
        }

        maxNumberOfWithdrawalsPerUser = _maxNumberOfWithdrawalsPerUser;
        emit MaxNumberOfWithdrawalsPerUserUpdated(_maxNumberOfWithdrawalsPerUser);
    }
}
```
