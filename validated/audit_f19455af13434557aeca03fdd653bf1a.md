### Title
Zero-value fee transfer in `MerkleDistributor.claim()` causes permanent revert for tokens that reject zero-value transfers - (File: contracts/utils/MerkleDistributor/MerkleDistributor.sol)

### Summary
`MerkleDistributor.claim()` unconditionally calls `IERC20(token).safeTransfer(protocolTreasury, fee)` even when `fee` is zero. When the distributed token reverts on zero-value transfers, all user claims revert, permanently freezing unclaimed yield.

### Finding Description
In `MerkleDistributor.claim()`, the fee is computed as:

```solidity
uint256 fee = (claimableAmount * feeInBPS) / 10_000;
uint256 amountToSend = claimableAmount - fee;

IERC20(token).safeTransfer(account, amountToSend);

// Send the fee to the protocol treasury
IERC20(token).safeTransfer(protocolTreasury, fee);
```

`fee` evaluates to zero in two realistic scenarios:
1. The owner sets `feeInBPS = 0` (explicitly allowed by `setFeeInBPS`, which only enforces `_feeInBPS <= MAX_FEE_IN_BPS`).
2. Integer division truncation: e.g., `feeInBPS = 1` and `claimableAmount = 99` → `fee = (99 * 1) / 10_000 = 0`.

In both cases, `safeTransfer(protocolTreasury, 0)` is called unconditionally. Tokens that revert on zero-value transfers (a known class of non-standard ERC-20 tokens) will cause the entire `claim()` call to revert.

The sibling contract `KernelMerkleDistributor._processClaim()` already applies the correct guard (`if (fee > 0) { kernel.safeTransfer(protocolTreasury, fee); }`), confirming the team is aware of this pattern — but `MerkleDistributor` was not updated consistently. [1](#0-0) [2](#0-1) 

### Impact Explanation
Any user whose `claimableAmount` produces a zero fee (due to truncation or `feeInBPS == 0`) will have their `claim()` permanently revert if the distributed token rejects zero-value transfers. The user's cumulative claim state is updated **before** the transfer, meaning the state is marked as claimed but no tokens are received — permanently freezing unclaimed yield.

**Impact: High — Permanent freezing of unclaimed yield.** [3](#0-2) 

### Likelihood Explanation
- `feeInBPS` can be set to 0 by the owner at any time via `setFeeInBPS`.
- Even with non-zero `feeInBPS`, integer truncation makes `fee == 0` for small claimable amounts (e.g., `feeInBPS = 1`, `claimableAmount < 10_000`).
- The `MerkleDistributor` is a generic distributor that can be deployed with any ERC-20 token, including tokens with non-standard zero-transfer behavior.
- The entry path is fully unprivileged: any user calls `claim()` with a valid merkle proof. [4](#0-3) 

### Recommendation
Add a zero-check before the fee transfer, mirroring the pattern already used in `KernelMerkleDistributor`:

```solidity
if (fee > 0) {
    IERC20(token).safeTransfer(protocolTreasury, fee);
}
``` [5](#0-4) 

### Proof of Concept
1. Deploy `MerkleDistributor` with a token that reverts on zero-value transfers and `feeInBPS = 0`.
2. Set a merkle root with a valid leaf for a user with `cumulativeAmount = 100`.
3. User calls `claim(index, account, 100, proof)`.
4. `fee = (100 * 0) / 10_000 = 0`.
5. `IERC20(token).safeTransfer(account, 100)` succeeds.
6. `IERC20(token).safeTransfer(protocolTreasury, 0)` reverts.
7. The entire transaction reverts; the user cannot claim their tokens.

Alternatively, with `feeInBPS = 1` and `claimableAmount = 50`: `fee = (50 * 1) / 10_000 = 0` → same revert path. [6](#0-5)

### Citations

**File:** contracts/utils/MerkleDistributor/MerkleDistributor.sol (L96-147)
```text
    /// @inheritdoc IMerkleDistributor
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

**File:** contracts/KERNEL/KernelMerkleDistributor.sol (L338-343)
```text
        uint256 fee = (claimableAmount * feeInBPS) / FEE_DENOMINATOR;
        uint256 amountToSend = claimableAmount - fee;

        if (fee > 0) {
            kernel.safeTransfer(protocolTreasury, fee);
        }
```
