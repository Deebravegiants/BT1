### Title
`setMerkleRoot` Overwrites Previous Root Without Preserving Claimability, Permanently Freezing Unclaimed Yield — (File: `contracts/utils/MerkleDistributor/MerkleDistributor.sol`, `contracts/KERNEL/KernelMerkleDistributor.sol`)

---

### Summary

Both `MerkleDistributor` and `KernelMerkleDistributor` store only a single `currentMerkleRoot`. When `setMerkleRoot` is called, the previous root is silently overwritten. The `claim` function verifies proofs exclusively against `currentMerkleRoot`. Any user who has not yet claimed from the previous root loses the ability to do so, because their proof is no longer valid against the new root. If the new root does not cumulatively carry forward their unclaimed amount, their rewards are permanently frozen in the contract.

---

### Finding Description

`setMerkleRoot` in both contracts unconditionally overwrites `currentMerkleRoot` and increments `currentIndex`:

```solidity
// MerkleDistributor.sol L156-L166
function setMerkleRoot(bytes32 _merkleRootToSet) external onlyOwner {
    if (_merkleRootToSet == bytes32(0)) revert ZeroValueProvided();
    currentMerkleRoot = _merkleRootToSet;   // old root is gone
    currentMerkleRootIndex++;
    currentIndex++;
    emit MerkleRootSet(currentMerkleRootIndex, currentMerkleRoot);
}
```

The `claim` function then verifies every proof against the single live root:

```solidity
// MerkleDistributor.sol L121
if (!MerkleProofUpgradeable.verify(merkleProof, currentMerkleRoot, node)) {
    revert InvalidMerkleProof();
}
```

The `isClaimed` guard only checks whether the user's `lastClaimedIndex` is at or above the supplied `index`:

```solidity
// MerkleDistributor.sol L90-L93
function isClaimed(uint256 index, address account) public view override returns (bool) {
    if (index == 0) revert ZeroValueProvided();
    return userClaims[account].lastClaimedIndex >= index;
}
```

And the index-range guard only rejects indices strictly above `currentIndex`:

```solidity
// MerkleDistributor.sol L111-L113
if (index == 0 || index > currentIndex) {
    revert InvalidIndex();
}
```

After a root rotation, a user who holds a valid proof for the old root (index N) will:
1. Pass the `index > currentIndex` check (N ≤ N+1) ✓
2. Pass the `isClaimed` check (never claimed) ✓
3. **Fail** the merkle proof verification — `currentMerkleRoot` is now the new root, so the old proof is cryptographically invalid ✗

The contract stores no historical roots and provides no fallback path. The only way the user can still claim is if the off-chain operator has included their cumulative amount in the new root. The contract does not enforce this invariant in any way.

The identical pattern exists in `KernelMerkleDistributor.sol`:

```solidity
// KernelMerkleDistributor.sol L402-L413
function setMerkleRoot(bytes32 _merkleRootToSet) external onlyOwner {
    currentMerkleRoot = _merkleRootToSet;
    currentMerkleRootIndex++;
    currentIndex++;
    emit MerkleRootSet(currentMerkleRootIndex, currentMerkleRoot);
}
```

```solidity
// KernelMerkleDistributor.sol L321
if (!MerkleProofUpgradeable.verify(merkleProof, currentMerkleRoot, node)) {
    revert InvalidMerkleProof();
}
```

---

### Impact Explanation

If the new merkle root does not cumulatively include a user's previously unclaimed amount — whether due to an off-chain system error, a snapshot race condition, or an operator mistake — the user's reward tokens remain locked in the contract with no on-chain path to retrieve them. This constitutes **permanent freezing of unclaimed yield** (Medium severity per the allowed impact scope). The tokens are not burned; they simply become unreachable by the affected user.

---

### Likelihood Explanation

Merkle roots are expected to be updated periodically (e.g., weekly reward epochs). Each update is a routine admin operation. The contract provides no on-chain enforcement that the new root carries forward all unclaimed balances from the previous root. A snapshot timing error, an off-chain indexing bug, or a user who claims between snapshot and root publication can all produce a situation where a user's unclaimed amount is absent from the new root. Because root updates are frequent and the contract offers no safety net, the probability of at least one user being affected over the protocol's lifetime is non-trivial.

---

### Recommendation

1. **Store historical roots**: Replace the single `currentMerkleRoot` with a mapping `mapping(uint256 => bytes32) public merkleRoots` indexed by `currentMerkleRootIndex`. Allow `claim` to accept a `rootIndex` parameter and verify against `merkleRoots[rootIndex]`, so users can always claim from any past root.
2. **Alternatively, enforce cumulative invariant off-chain with a time-lock**: Introduce a minimum delay between `setMerkleRoot` calls (e.g., 24–48 hours) to give all users time to claim before the root is rotated.
3. **Emit the old root in the event**: At minimum, emit the previous root in `MerkleRootSet` so off-chain monitors can detect non-cumulative updates.

---

### Proof of Concept

1. Owner calls `setMerkleRoot(R1)` → `currentMerkleRoot = R1`, `currentIndex = 1`.
2. User A is entitled to 100 KERNEL tokens; their proof is `(index=1, account=A, cumulativeAmount=100, proof_for_R1)`.
3. User A does not claim before the next epoch.
4. Owner calls `setMerkleRoot(R2)` → `currentMerkleRoot = R2`, `currentIndex = 2`. R2 is generated from a snapshot that missed User A (e.g., snapshot taken before User A's eligibility was recorded).
5. User A calls `claim(1, A, 100, proof_for_R1)`:
   - `index (1) > currentIndex (2)` → false, passes ✓
   - `isClaimed(1, A)` → `userClaims[A].lastClaimedIndex (0) >= 1` → false, passes ✓
   - `MerkleProofUpgradeable.verify(proof_for_R1, R2, node)` → **reverts with `InvalidMerkleProof`** ✗
6. User A tries `claim(2, A, 100, proof_for_R2)` — no such proof exists because R2 does not include A.
7. User A's 100 KERNEL tokens are permanently frozen in the contract. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

### Citations

**File:** contracts/utils/MerkleDistributor/MerkleDistributor.sol (L89-94)
```text
    /// @inheritdoc IMerkleDistributor
    function isClaimed(uint256 index, address account) public view override returns (bool) {
        if (index == 0) revert ZeroValueProvided();

        return userClaims[account].lastClaimedIndex >= index;
    }
```

**File:** contracts/utils/MerkleDistributor/MerkleDistributor.sol (L107-123)
```text
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

**File:** contracts/KERNEL/KernelMerkleDistributor.sol (L319-323)
```text
        // Verify the merkle proof
        bytes32 node = keccak256(abi.encodePacked(index, account, cumulativeAmount));
        if (!MerkleProofUpgradeable.verify(merkleProof, currentMerkleRoot, node)) {
            revert InvalidMerkleProof();
        }
```

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
