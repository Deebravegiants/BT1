### Title
Censorable `rewardsToken` Permanently Freezes Staker Rewards in `KernelDepositPool` — (File: contracts/KERNEL/KernelDepositPool.sol)

---

### Summary

`KernelDepositPool.getReward()` transfers accrued rewards directly to `msg.sender` via `rewardsToken.safeTransfer`. If `rewardsToken` is a censorable ERC20 (e.g., USDC or USDT) and the staker's address is blacklisted by that token, the transfer permanently reverts. There is no admin rescue path, no alternative claim address, and no try/catch fallback — the staker's earned rewards are frozen in the contract indefinitely.

---

### Finding Description

`KernelDepositPool.getReward()` is the sole mechanism for a staker to claim earned rewards:

```solidity
// contracts/KERNEL/KernelDepositPool.sol:382-390
function getReward() external nonReentrant updateReward(msg.sender) {
    uint256 rewardAmount = rewards[msg.sender];

    if (rewardAmount > 0) {
        rewards[msg.sender] = 0;
        rewardsToken.safeTransfer(msg.sender, rewardAmount);   // <-- reverts if blacklisted
        emit RewardsClaimed(msg.sender, rewardAmount);
    }
}
``` [1](#0-0) 

The `rewardsToken` is set once at initialization and has no admin setter, so it cannot be changed after deployment: [2](#0-1) 

If `rewardsToken` is USDC or USDT — both of which maintain on-chain blacklists — and a staker's address is added to that blacklist, every call to `getReward()` will revert at `safeTransfer`. Because `rewards[msg.sender]` is zeroed out in the same transaction (and reverts atomically with the failed transfer), the accounting is consistent but the staker can never extract their yield. No admin function exists to redirect or rescue the frozen balance.

The same structural issue exists in `MerkleDistributor.claim()`, where two sequential `safeTransfer` calls are made — one to `account` and one to `protocolTreasury`. If `protocolTreasury` is blacklisted by the reward token, **every user's** claim fails:

```solidity
IERC20(token).safeTransfer(account, amountToSend);
IERC20(token).safeTransfer(protocolTreasury, fee);   // <-- blocks all claims if treasury is blacklisted
``` [3](#0-2) 

---

### Impact Explanation

**Medium — Permanent freezing of unclaimed yield.**

A staker who has legitimately earned rewards through `KernelDepositPool` loses permanent access to those rewards if their address is blacklisted by the reward token. The funds remain in the contract with no recovery path. In the `MerkleDistributor` variant, blacklisting of `protocolTreasury` freezes all users' unclaimed yield simultaneously.

---

### Likelihood Explanation

USDC and USDT are the most widely used reward tokens in DeFi. Both maintain active blacklists used for regulatory compliance and sanctions enforcement. It is realistic that:

1. The protocol deploys `KernelDepositPool` with USDC or USDT as `rewardsToken`.
2. A staker's address is subsequently blacklisted (e.g., due to sanctions, exchange compliance, or protocol-level enforcement).
3. That staker can never claim their accrued rewards.

This does not require any malicious admin action — it is a foreseeable interaction between a legitimate reward token choice and standard token issuer behavior, exactly as the referenced judge noted for USDC/USDT.

---

### Recommendation

1. **Wrap the transfer in a try/catch** and keep rewards accrued if the transfer fails, allowing a future retry or admin rescue.
2. **Add an admin rescue function** that can redirect frozen rewards for a specific address to an alternative recipient.
3. **Alternatively**, restrict `rewardsToken` to non-censorable tokens only, enforced at initialization.

For `MerkleDistributor`, consider skipping the fee transfer (or sending to a fallback address) if the treasury transfer fails, rather than reverting the entire claim.

---

### Proof of Concept

1. `KernelDepositPool` is deployed with USDC as `rewardsToken`.
2. Alice stakes KERNEL tokens; over time she accrues `rewards[alice] = 1000e6` USDC.
3. USDC's issuer blacklists Alice's address.
4. Alice calls `getReward()`.
5. `rewardsToken.safeTransfer(alice, 1000e6)` reverts — the entire transaction reverts.
6. `rewards[alice]` remains `1000e6` (the zero-assignment is also reverted).
7. Alice retries indefinitely; every call reverts. Her 1000 USDC is permanently frozen in the contract.
8. There is no admin function to redirect or recover Alice's rewards. [1](#0-0) [4](#0-3)

### Citations

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

**File:** contracts/utils/MerkleDistributor/MerkleDistributor.sol (L137-146)
```text
        // Send the claimable amount to the user - deducting the fee
        uint256 fee = (claimableAmount * feeInBPS) / 10_000;
        uint256 amountToSend = claimableAmount - fee;

        IERC20(token).safeTransfer(account, amountToSend);

        // Send the fee to the protocol treasury
        IERC20(token).safeTransfer(protocolTreasury, fee);

        emit Claimed(index, account, claimableAmount);
```
