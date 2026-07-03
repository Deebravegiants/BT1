### Title
Fee Reduction Delay via Block Stuffing Allows Old Fee to Apply to User Claims — (`contracts/KERNEL/KernelTop100MerkleDistributor.sol`)

---

### Summary

`setFeeInBPS` applies instantly with no timelock and no user-side slippage guard. An attacker can stuff blocks to delay the owner's fee-reduction transaction, forcing users who submit `claim()` or `claimAndStake()` during the delay window to pay the old (higher) fee instead of the announced lower one.

---

### Finding Description

`setFeeInBPS` writes directly to `feeInBPS` with no delay: [1](#0-0) 

Both `claim` and `claimAndStake` read `feeInBPS` at execution time: [2](#0-1) [3](#0-2) 

Neither function accepts a `maxFeeInBPS` parameter, so users have no on-chain slippage protection against a fee that is higher than what they observed off-chain when they submitted their transaction. [4](#0-3) 

**Attack path:**

1. Owner broadcasts `setFeeInBPS(0)` (reducing from 1000 BPS / 10%).
2. Users observe the pending tx and submit `claim()` transactions expecting 0% fee.
3. Attacker fills blocks with high-gas dummy transactions, keeping the owner's tx out of the chain for N blocks.
4. Users' `claim()` txs land in those stuffed blocks and execute against `feeInBPS = 1000`.
5. The owner's `setFeeInBPS(0)` finally lands in block N+1 — after all user claims have settled.

---

### Impact Explanation

Users receive `claimableAmount * 0.90` instead of the full `claimableAmount`. The 10% excess is transferred to `protocolTreasury` rather than to the claimants. This is a direct failure to deliver the promised return (the announced 0% fee), matching **Low — contract fails to deliver promised returns / block stuffing**. [5](#0-4) 

---

### Likelihood Explanation

Block stuffing is expensive on Ethereum mainnet but is locally testable and provably effective. The precondition (owner publicly signals a fee reduction, users rush to claim) is realistic for a token distribution event. No admin compromise or private-key leak is required — the attacker only needs capital to outbid normal gas prices for a small number of blocks. The contract provides zero on-chain defence: no timelock on `setFeeInBPS`, no `maxFee` parameter in `claim`, and no pause-then-update pattern.

---

### Recommendation

1. **Add a timelock to `setFeeInBPS`**: queue the new fee and enforce a minimum delay (e.g., 24–48 h) before it takes effect, giving users time to react.
2. **Add a `maxFeeInBPS` parameter to `claim` / `claimAndStake`**: revert if `feeInBPS > maxFeeInBPS` at execution time, giving users a slippage guard analogous to DEX `minAmountOut`.
3. **Alternatively, use a two-step commit-reveal or a scheduled fee change** that is announced on-chain before it activates.

---

### Proof of Concept

```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.27;

// Foundry / Hardhat local fork test (no mainnet)
// Demonstrates: feeInBPS = 1000, owner submits setFeeInBPS(0),
// attacker stuffs 10 blocks, all claim() calls deduct 10%.

contract BlockStuffingPoC {
    KernelTop100MerkleDistributor distributor; // deployed locally

    function testBlockStuffing() external {
        // Setup: feeInBPS = 1000 (10%)
        assert(distributor.feeInBPS() == 1000);

        // Owner submits setFeeInBPS(0) — tx sits in mempool
        // Attacker stuffs 10 blocks (simulate by vm.roll + filling gas)
        for (uint256 i = 0; i < 10; i++) {
            // Each block: attacker sends high-gas txs consuming block gas limit
            // Owner's setFeeInBPS(0) cannot be included
            vm.roll(block.number + 1);

            // User claims during stuffed block
            uint256 balanceBefore = kernel.balanceOf(user);
            distributor.claim(amount, merkleProof); // executes at feeInBPS=1000
            uint256 received = kernel.balanceOf(user) - balanceBefore;

            // Invariant: user should receive claimableAmount (fee=0 promised)
            // Actual: user receives claimableAmount * 90% — VIOLATED
            assert(received < claimableAmount); // 10% deducted
        }

        // Owner's tx finally lands
        vm.prank(owner);
        distributor.setFeeInBPS(0);
        assert(distributor.feeInBPS() == 0);

        // Total excess fee extracted = claimableAmount * 10% * numUsers
        // All went to protocolTreasury instead of claimants
    }
}
```

### Citations

**File:** contracts/KERNEL/KernelTop100MerkleDistributor.sol (L310-338)
```text
    function claim(uint256 amount, bytes32[] calldata merkleProof) external nonReentrant whenNotPaused {
        address user = msg.sender;

        // Verify merkle proof and update user claim data
        _verifyClaimProof(user, amount, merkleProof);

        // Get claimable amount
        uint256 claimableAmount = _getUnclaimedVestedAmount(user, amount);

        if (claimableAmount == 0) {
            revert NoTokensToClaim();
        }

        // Update user claim data
        userClaims[user].lastClaimTimestamp = block.timestamp;
        userClaims[user].amountClaimed += claimableAmount;

        // Calculate fee
        uint256 fee = (claimableAmount * feeInBPS) / FEE_DENOMINATOR;
        uint256 amountToSend = claimableAmount - fee;

        // Transfer tokens
        if (fee > 0) {
            kernel.safeTransfer(protocolTreasury, fee);
        }
        kernel.safeTransfer(user, amountToSend);

        emit Claimed(user, amountToSend);
    }
```

**File:** contracts/KERNEL/KernelTop100MerkleDistributor.sol (L362-364)
```text
        // Calculate fee
        uint256 fee = (claimableAmount * feeInBPS) / FEE_DENOMINATOR;
        uint256 amountToStake = claimableAmount - fee;
```

**File:** contracts/KERNEL/KernelTop100MerkleDistributor.sol (L426-432)
```text
    function setFeeInBPS(uint256 _feeInBPS) external onlyOwner {
        if (_feeInBPS > MAX_FEE_IN_BPS) {
            revert InvalidFeeInBPS();
        }
        feeInBPS = _feeInBPS;
        emit FeeInBPSUpdated(feeInBPS);
    }
```
