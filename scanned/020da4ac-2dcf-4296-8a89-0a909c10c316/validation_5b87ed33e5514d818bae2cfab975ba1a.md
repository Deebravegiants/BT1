### Title
Zero-value fee transfer in `MerkleDistributor.claim()` causes DoS when `feeInBPS = 0` - (File: contracts/utils/MerkleDistributor/MerkleDistributor.sol)

---

### Summary

`MerkleDistributor.claim()` unconditionally calls `safeTransfer(protocolTreasury, fee)` even when `fee = 0`. ERC20 tokens that revert on zero-value transfers will cause every claim to fail, permanently freezing unclaimed yield in the contract.

---

### Finding Description

In `MerkleDistributor.claim()`, the fee is computed and then transferred to `protocolTreasury` without a zero-guard:

```solidity
uint256 fee = (claimableAmount * feeInBPS) / 10_000;
uint256 amountToSend = claimableAmount - fee;

IERC20(token).safeTransfer(account, amountToSend);

// Send the fee to the protocol treasury
IERC20(token).safeTransfer(protocolTreasury, fee);   // ← always called, even when fee == 0
``` [1](#0-0) 

When `feeInBPS = 0` (which is a valid configuration — `initialize` and `setFeeInBPS` both allow it), `fee` evaluates to `0` and the unconditional `safeTransfer(protocolTreasury, 0)` is executed. For the class of ERC20 tokens that revert on zero-value transfers, this causes the entire `claim()` call to revert. [2](#0-1) 

The sibling contract `KernelMerkleDistributor` correctly guards this transfer:

```solidity
if (fee > 0) {
    kernel.safeTransfer(protocolTreasury, fee);
}
``` [3](#0-2) 

`MerkleDistributor` lacks this guard entirely. [4](#0-3) 

---

### Impact Explanation

**Medium — Permanent freezing of unclaimed yield.**

All users with valid merkle proofs are blocked from claiming their token allocations. The tokens remain locked in the contract with no path to recovery for users (only the owner could work around it by raising `feeInBPS` above zero, but that imposes an unintended fee on claimants).

---

### Likelihood Explanation

`feeInBPS` defaults to whatever value is passed at initialization and can be set to `0` via `setFeeInBPS` at any time. The `MerkleDistributor` is a generic contract whose `token` is also admin-configurable, meaning it can be pointed at any ERC20 — including tokens in the "revert on zero-value transfer" category. The combination of `feeInBPS = 0` and such a token is a realistic operational state.

---

### Recommendation

Mirror the guard used in `KernelMerkleDistributor`:

```solidity
uint256 fee = (claimableAmount * feeInBPS) / 10_000;
uint256 amountToSend = claimableAmount - fee;

IERC20(token).safeTransfer(account, amountToSend);

if (fee > 0) {
    IERC20(token).safeTransfer(protocolTreasury, fee);
}
```

---

### Proof of Concept

1. Deploy `MerkleDistributor` with a token that reverts on zero-value transfers and `feeInBPS = 0`.
2. Owner calls `setMerkleRoot(root)` with a root encoding user allocations.
3. User calls `claim(index, account, cumulativeAmount, proof)` with a valid proof.
4. `claimableAmount > 0`, `fee = (claimableAmount * 0) / 10_000 = 0`.
5. `IERC20(token).safeTransfer(account, amountToSend)` succeeds.
6. `IERC20(token).safeTransfer(protocolTreasury, 0)` reverts (token rejects zero-value transfer).
7. Entire transaction reverts; user receives nothing. All subsequent claims by any user fail identically. [5](#0-4)

### Citations

**File:** contracts/utils/MerkleDistributor/MerkleDistributor.sol (L71-87)
```text
    function initialize(address token_, address _protocolTreasury, uint256 _feeInBPS) external initializer {
        // token can be set later but not the protocol treasury
        if (_protocolTreasury == address(0)) {
            revert ZeroValueProvided();
        }

        if (_feeInBPS > MAX_FEE_IN_BPS) {
            revert InvalidFeeInBPS();
        }

        __Ownable_init();
        __Pausable_init();

        token = token_;
        protocolTreasury = _protocolTreasury;
        feeInBPS = _feeInBPS;
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
