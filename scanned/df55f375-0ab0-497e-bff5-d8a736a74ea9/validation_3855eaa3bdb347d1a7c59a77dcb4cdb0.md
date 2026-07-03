### Title
Transaction Displacement Extends Withdrawal Lock Period Beyond User Expectation - (File: contracts/KERNEL/KernelDepositPool.sol)

### Summary
`KernelDepositPool.initiateWithdrawal()` computes `unlockTime` using `block.timestamp` at execution time with no deadline guard. An attacker who displaces the transaction in the mempool causes it to land in a later block, pushing `unlockTime` further into the future and temporarily freezing the user's KERNEL tokens beyond the delay they intended to accept.

### Finding Description
`initiateWithdrawal()` immediately reduces the caller's staked balance and records a withdrawal with:

```solidity
uint256 unlockTime = block.timestamp + withdrawalDelay;
``` [1](#0-0) 

The function accepts no `deadline` parameter. Once the transaction is broadcast to the mempool it is publicly visible. An attacker can submit a stream of higher-gas-price transactions to fill block space (block stuffing / displacement), keeping the victim's transaction pending for additional blocks. When the transaction is eventually included, `block.timestamp` is later than the user expected, so `unlockTime` is correspondingly later. The user's KERNEL tokens — which were already deducted from `balanceOf` and `totalKernelStaked` at line 325-326 — are now locked until the inflated `unlockTime`, and `claimWithdrawal` will revert until that timestamp is reached:

```solidity
if (block.timestamp < withdrawal.unlockTime) {
    revert WithdrawalNotReady();
}
``` [2](#0-1) 

No deadline protection exists anywhere in the contract. [3](#0-2) 

### Impact Explanation
Once `initiateWithdrawal` executes, the user's staked balance is gone and the only path to recovery is `claimWithdrawal` after `unlockTime`. Because `unlockTime` is anchored to the actual execution timestamp, any displacement directly extends the lock period by the same duration. `MAX_WITHDRAWAL_DELAY` is 30 days; even a displacement of hours represents a meaningful, attacker-controlled extension of fund unavailability. This maps to **Medium — Temporary freezing of funds**. [4](#0-3) 

### Likelihood Explanation
The transaction is permissionless and publicly visible in the mempool. On L2 networks (where this contract may be deployed alongside the pool contracts in the same repo) block production is cheap, making displacement attacks significantly less expensive than on Ethereum mainnet. Any party who benefits from keeping a competitor's KERNEL tokens locked (e.g., a competing staker who earns a larger share of `rewardRate` while `totalKernelStaked` remains higher) has a direct economic incentive. Likelihood is **Low-Medium**. [5](#0-4) 

### Recommendation
Add a `deadline` parameter to `initiateWithdrawal` and revert if the transaction is included after it:

```solidity
function initiateWithdrawal(uint256 _amount, uint256 deadline) external nonReentrant updateReward(msg.sender) {
    if (block.timestamp > deadline) revert DeadlineExceeded();
    // ... rest of logic unchanged
}
```

This gives users a guaranteed upper bound on the timestamp used to compute `unlockTime`, eliminating the displacement vector.

### Proof of Concept

1. Alice calls `initiateWithdrawal(1000e18)` intending `unlockTime = T + withdrawalDelay`.
2. Attacker sees the transaction in the mempool and submits high-gas filler transactions, displacing Alice's tx by `Δ` seconds.
3. Alice's transaction lands at block timestamp `T + Δ`.
4. `unlockTime` is stored as `T + Δ + withdrawalDelay` instead of `T + withdrawalDelay`.
5. Alice's `balanceOf` is already 0 (line 325); she cannot re-stake or re-initiate.
6. Calling `claimWithdrawal` before `T + Δ + withdrawalDelay` reverts with `WithdrawalNotReady`.
7. Alice's KERNEL tokens are frozen for `Δ` seconds longer than she accepted. [6](#0-5)

### Citations

**File:** contracts/KERNEL/KernelDepositPool.sol (L35-35)
```text
    uint256 public constant MAX_WITHDRAWAL_DELAY = 30 days;
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

**File:** contracts/KERNEL/KernelDepositPool.sol (L408-413)
```text
    function rewardPerToken() public view returns (uint256) {
        if (totalKernelStaked == 0) {
            return rewardPerTokenStored;
        }
        return rewardPerTokenStored + (rewardRate * (lastTimeRewardApplicable() - updatedAt) * DECIMAL_PRECISION)
            / totalKernelStaked;
```
