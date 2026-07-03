### Title
Merkle Distributor Contracts Set Root Without Contract Balance Validation, Enabling Permanent Freezing of Unclaimed Yield - (File: contracts/KERNEL/KernelTop100MerkleDistributor.sol, contracts/KERNEL/KernelMerkleDistributor.sol, contracts/utils/MerkleDistributor/MerkleDistributor.sol)

---

### Summary

All three Merkle distributor contracts in scope (`KernelTop100MerkleDistributor`, `KernelMerkleDistributor`, `MerkleDistributor`) set or update a Merkle root without any on-chain validation that the contract's token balance is sufficient to cover the total claims encoded in the tree. In `KernelTop100MerkleDistributor`, an additional `withdrawTokens()` function allows the owner to drain the contract after the root is set, with no accounting of outstanding obligations. Users holding valid Merkle proofs will have their `claim()` or `claimAndStake()` calls revert due to insufficient token balance, permanently freezing their unclaimed yield.

---

### Finding Description

**`KernelMerkleDistributor.setMerkleRoot()`** and **`MerkleDistributor.setMerkleRoot()`** accept a new Merkle root with no accompanying total-amount parameter and no check that `kernel.balanceOf(address(this))` covers the sum of all new incremental claims encoded in the tree. [1](#0-0) [2](#0-1) 

**`KernelTop100MerkleDistributor`** sets its single Merkle root at initialization and never updates it, but exposes `withdrawTokens()` which transfers any amount of any token out of the contract with no check against the total amount still owed to users per the Merkle tree: [3](#0-2) 

The vesting schedule in `KernelTop100MerkleDistributor` (30-day linear vest) means users will be claiming incrementally over time. If the contract is underfunded at any point during the vesting window, `kernel.safeTransfer()` inside `claim()` will revert: [4](#0-3) 

There is no on-chain mechanism to track the total amount committed by the Merkle tree versus the current contract balance. The contract relies entirely on the owner to maintain solvency, with no enforcement.

---

### Impact Explanation

**Medium. Permanent freezing of unclaimed yield.**

Users with valid Merkle proofs for KERNEL token allocations will be unable to claim their vested rewards if the contract is underfunded. Because `userClaims[user].amountClaimed` is updated before the transfer in `claim()`, a revert on the `safeTransfer` line means the state update is rolled back and the user can retry — but if the contract remains underfunded, the yield is permanently inaccessible until the owner re-funds the contract. In the worst case (e.g., owner calls `withdrawTokens()` to recover "excess" tokens without accounting for unvested allocations), all remaining claimants lose access to their yield.

---

### Likelihood Explanation

**Low-Medium.** The owner is responsible for funding the contract and must manually ensure the balance covers all Merkle tree leaves. Operational errors (miscalculation of total allocation, partial funding, or calling `withdrawTokens()` without accounting for unvested amounts) are realistic. The 30-day vesting window in `KernelTop100MerkleDistributor` creates a prolonged exposure window. No malicious intent is required — an honest accounting mistake is sufficient.

---

### Recommendation

1. In `setMerkleRoot()` (and `initialize()` for `KernelTop100MerkleDistributor`), require a `_totalAmount` parameter and validate `IERC20(token).balanceOf(address(this)) >= _totalAmount` before accepting the new root.
2. In `KernelTop100MerkleDistributor.withdrawTokens()`, track a `totalCommitted` state variable (set at initialization) and a `totalClaimed` counter (incremented on each successful claim), then enforce `_amount <= balanceOf(address(this)) - (totalCommitted - totalClaimed)`.
3. Document clearly in user-facing materials that the contract's solvency depends on the owner maintaining sufficient balance, as the Merkle root opaquely encodes obligations that cannot be validated on-chain.

---

### Proof of Concept

1. Owner deploys `KernelTop100MerkleDistributor` with a Merkle root encoding 1,000,000 KERNEL total across 100 users (10,000 KERNEL each), but only funds the contract with 900,000 KERNEL.
2. The first 90 users successfully call `claim()` and receive their vested amounts over the 30-day window.
3. Users 91–100 call `claim()` with valid Merkle proofs; `kernel.safeTransfer(user, amountToSend)` reverts because `kernel.balanceOf(address(this)) < amountToSend`.
4. These 10 users permanently lose access to their 100,000 KERNEL in unclaimed yield.

**Alternative path via `withdrawTokens()`:**
1. Owner deploys and correctly funds the contract with 1,000,000 KERNEL.
2. After 15 days, 50% of tokens have been claimed. Owner observes 500,000 KERNEL remaining and calls `withdrawTokens(kernel, 500_000e18, treasury)`, believing the contract is now empty of obligations.
3. The remaining 50 users, who have not yet claimed their vested portions, call `claim()` and receive reverts. [5](#0-4) [3](#0-2)

### Citations

**File:** contracts/KERNEL/KernelMerkleDistributor.sol (L402-413)
```text
    function setMerkleRoot(bytes32 _merkleRootToSet) external onlyOwner {
        if (_merkleRootToSet == bytes32(0)) {
            revert ZeroValueProvided();
        }

        currentMerkleRoot = _merkleRootToSet;

        currentMerkleRootIndex++;
        currentIndex++;

        emit MerkleRootSet(currentMerkleRootIndex, currentMerkleRoot);
    }
```

**File:** contracts/utils/MerkleDistributor/MerkleDistributor.sol (L156-167)
```text
    function setMerkleRoot(bytes32 _merkleRootToSet) external onlyOwner {
        if (_merkleRootToSet == bytes32(0)) {
            revert ZeroValueProvided();
        }

        currentMerkleRoot = _merkleRootToSet;

        currentMerkleRootIndex++;
        currentIndex++;

        emit MerkleRootSet(currentMerkleRootIndex, currentMerkleRoot);
    }
```

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

**File:** contracts/KERNEL/KernelTop100MerkleDistributor.sol (L461-472)
```text
    function withdrawTokens(address _token, uint256 _amount, address _recipient) external onlyOwner {
        UtilLib.checkNonZeroAddress(_token);
        UtilLib.checkNonZeroAddress(_recipient);

        if (_amount == 0) {
            revert ZeroValueProvided();
        }

        IERC20(_token).safeTransfer(_recipient, _amount);

        emit TokensWithdrawn(_token, _amount, _recipient);
    }
```
