I found the analog. Let me verify the exact lines in `MerkleDistributor.sol` and check `KernelMerkleDistributor` for comparison.

### Title
Unconditional zero-value `safeTransfer` to `protocolTreasury` permanently freezes all user claims when `feeInBPS == 0` and token reverts on zero transfers - (File: contracts/utils/MerkleDistributor/MerkleDistributor.sol)

---

### Summary

`MerkleDistributor.claim()` unconditionally calls `IERC20(token).safeTransfer(protocolTreasury, fee)` even when `fee == 0`. If `feeInBPS` is set to `0` and the distributed token reverts on zero-value transfers, every user's `claim()` call will revert, permanently freezing all unclaimed yield inside the contract.

---

### Finding Description

In `contracts/utils/MerkleDistributor/MerkleDistributor.sol`, the `claim()` function computes a fee and then unconditionally transfers it to `protocolTreasury`:

```solidity
uint256 fee = (claimableAmount * feeInBPS) / 10_000;
uint256 amountToSend = claimableAmount - fee;

IERC20(token).safeTransfer(account, amountToSend);

// Send the fee to the protocol treasury
IERC20(token).safeTransfer(protocolTreasury, fee);   // ← no zero-check
``` [1](#0-0) 

When `feeInBPS == 0`, `fee` evaluates to `0`, and the unconditional `safeTransfer(protocolTreasury, 0)` is executed. Tokens that revert on zero-value transfers (e.g., LEND, BNB, and various ERC-20 variants) will cause this call to revert, making `claim()` permanently uncallable.

`feeInBPS` is allowed to be `0` — neither `initialize()` nor `setFeeInBPS()` enforce a non-zero lower bound:

```solidity
if (_feeInBPS > MAX_FEE_IN_BPS) {
    revert InvalidFeeInBPS();
}
``` [2](#0-1) 

The sibling contract `KernelMerkleDistributor` already contains the correct guard, confirming the fix is known:

```solidity
if (fee > 0) {
    kernel.safeTransfer(protocolTreasury, fee);
}
``` [3](#0-2) 

This guard is absent in `MerkleDistributor`. [4](#0-3) 

---

### Impact Explanation

**Medium — Permanent freezing of unclaimed yield.**

All tokens allocated to users in the Merkle tree become permanently unclaimable. The state update (`userClaims[account].cumulativeAmount = cumulativeAmount`) executes before the revert, so the accounting is corrupted: the contract records the claim as processed but the user never receives tokens. Every subsequent call also reverts because the cumulative amount is already updated, leaving funds locked in the distributor with no recovery path. [5](#0-4) 

---

### Likelihood Explanation

**Medium.**

Two conditions must hold simultaneously:
1. `feeInBPS` is set to `0` — a valid and operationally reasonable configuration (no protocol fee period), reachable via `setFeeInBPS(0)` by the owner.
2. The configured `token` reverts on zero-value transfers — a known property of several deployed ERC-20 tokens.

Neither condition requires attacker action; both are normal protocol states. Once both are true, the freeze is triggered by any ordinary user calling `claim()`. [6](#0-5) 

---

### Recommendation

Add a zero-check before the fee transfer, mirroring the pattern already used in `KernelMerkleDistributor`:

```solidity
if (fee > 0) {
    IERC20(token).safeTransfer(protocolTreasury, fee);
}
``` [4](#0-3) 

---

### Proof of Concept

1. Owner deploys `MerkleDistributor` with a token that reverts on zero-value transfers (e.g., LEND).
2. Owner calls `setFeeInBPS(0)` — valid, passes the `> MAX_FEE_IN_BPS` check.
3. Owner sets a Merkle root allocating 100 tokens to Alice.
4. Alice calls `claim(index, alice, 100, proof)`.
5. Execution reaches line 138: `fee = (100 * 0) / 10_000 = 0`.
6. Line 141: `safeTransfer(alice, 100)` succeeds.
7. Line 144: `safeTransfer(protocolTreasury, 0)` — token reverts on zero transfer → entire transaction reverts.
8. Alice's `userClaims` state was written at line 134–135 before the revert, so the storage update is also rolled back, but the call will revert on every attempt as long as `feeInBPS == 0` and the token is unchanged.
9. All users' claims are permanently frozen. [7](#0-6)

### Citations

**File:** contracts/utils/MerkleDistributor/MerkleDistributor.sol (L77-79)
```text
        if (_feeInBPS > MAX_FEE_IN_BPS) {
            revert InvalidFeeInBPS();
        }
```

**File:** contracts/utils/MerkleDistributor/MerkleDistributor.sol (L97-147)
```text
    function claim(
        uint256 index,
        address account,
        uint256 cumulativeAmount,
        bytes32[] calldata merkleProof
    )
        external
        override
        whenNotPaused
    {
        if (currentMerkleRoot == bytes32(0)) {
            revert ZeroValueProvided();
        }

        if (index == 0 || index > currentIndex) {
            revert InvalidIndex();
        }

        if (isClaimed(index, account)) {
            revert AlreadyClaimed();
        }

        // Verify the merkle proof.
        bytes32 node = keccak256(abi.encodePacked(index, account, cumulativeAmount));
        if (!MerkleProofUpgradeable.verify(merkleProof, currentMerkleRoot, node)) {
            revert InvalidMerkleProof();
        }

        // Calculate the claimable amount
        uint256 claimableAmount = cumulativeAmount - userClaims[account].cumulativeAmount;

        // Ensure there is something to claim
        if (claimableAmount == 0) {
            revert NoTokensToClaim();
        }

        // Update user claim info, and send the token.
        userClaims[account].lastClaimedIndex = index;
        userClaims[account].cumulativeAmount = cumulativeAmount;

        // Send the claimable amount to the user - deducting the fee
        uint256 fee = (claimableAmount * feeInBPS) / 10_000;
        uint256 amountToSend = claimableAmount - fee;

        IERC20(token).safeTransfer(account, amountToSend);

        // Send the fee to the protocol treasury
        IERC20(token).safeTransfer(protocolTreasury, fee);

        emit Claimed(index, account, claimableAmount);
    }
```

**File:** contracts/utils/MerkleDistributor/MerkleDistributor.sol (L196-206)
```text
    /// @dev only called by the owner.
    /// @param _feeInBPS The fee in BPS.
    function setFeeInBPS(uint256 _feeInBPS) external onlyOwner {
        if (_feeInBPS > MAX_FEE_IN_BPS) {
            revert InvalidFeeInBPS();
        }

        feeInBPS = _feeInBPS;

        emit FeeInBPSUpdated(_feeInBPS);
    }
```

**File:** contracts/KERNEL/KernelMerkleDistributor.sol (L341-343)
```text
        if (fee > 0) {
            kernel.safeTransfer(protocolTreasury, fee);
        }
```
