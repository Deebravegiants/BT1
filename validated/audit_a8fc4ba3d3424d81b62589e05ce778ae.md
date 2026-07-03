### Title
Merkle Root Overwrite in `setMerkleRoot` Permanently Freezes Unclaimed KERNEL Rewards - (File: `contracts/KERNEL/KernelMerkleDistributor.sol`)

---

### Summary

`KernelMerkleDistributor.setMerkleRoot` unconditionally overwrites `currentMerkleRoot` and increments `currentIndex`. Because `_processClaim` verifies proofs exclusively against the live `currentMerkleRoot`, any user who has not yet claimed under the previous root will find their old proof permanently invalid after the root is updated. If the replacement root omits a user or assigns them a new index they have no proof for, their unclaimed KERNEL rewards are frozen with no recovery path.

---

### Finding Description

`setMerkleRoot` is the sole mechanism for publishing distribution data:

```solidity
// KernelMerkleDistributor.sol L402-413
function setMerkleRoot(bytes32 _merkleRootToSet) external onlyOwner {
    if (_merkleRootToSet == bytes32(0)) {
        revert ZeroValueProvided();
    }
    currentMerkleRoot = _merkleRootToSet;   // ← unconditional overwrite
    currentMerkleRootIndex++;
    currentIndex++;
    emit MerkleRootSet(currentMerkleRootIndex, currentMerkleRoot);
}
``` [1](#0-0) 

Each call increments `currentIndex` by one. The merkle leaf is constructed as:

```solidity
bytes32 node = keccak256(abi.encodePacked(index, account, cumulativeAmount));
if (!MerkleProofUpgradeable.verify(merkleProof, currentMerkleRoot, node)) {
    revert InvalidMerkleProof();
}
``` [2](#0-1) 

The `index` is baked into the leaf. A user whose leaf was `(index=1, account=A, cumulativeAmount=100)` in root #1 must supply `index=1` when claiming. After `setMerkleRoot` is called a second time, `currentMerkleRoot` becomes root #2 (whose leaves carry `index=2`). The index-range check `index > currentIndex` still passes for `index=1` (since `currentIndex` is now 2), but the Merkle proof for `(index=1, account=A, cumulativeAmount=100)` is verified against root #2 and will always revert with `InvalidMerkleProof`. There is no fallback to the historical root. [3](#0-2) 

The contract stores only a single live root and provides no mechanism to claim against a superseded root:

```solidity
bytes32 public currentMerkleRoot;   // single slot, no history
``` [4](#0-3) 

---

### Impact Explanation

Any user who has not claimed before a root rotation loses access to their accrued KERNEL rewards permanently. The contract holds no record of the previous root, so there is no on-chain path to recover the claim. This constitutes **permanent freezing of unclaimed yield**.

Impact: **Medium — Permanent freezing of unclaimed yield.**

---

### Likelihood Explanation

The owner is expected to call `setMerkleRoot` repeatedly across distribution epochs (the contract is explicitly designed for cumulative, multi-epoch distributions). A root update is a routine operational action — e.g., correcting a miscalculated root, adding a new epoch, or responding to an off-chain data error. Any such update before all prior claimants have acted silently invalidates their proofs. No malicious intent is required; the design flaw is structural.

---

### Recommendation

1. **Store historical roots**: Map `merkleRootIndex => bytes32` and allow `_processClaim` to verify against the root that was active when the user's `index` was assigned.
2. **Enforce a claim window**: Require a minimum time-lock (e.g., 7 days) between successive `setMerkleRoot` calls, giving users time to claim before the root rotates.
3. **Validate continuity off-chain + on-chain**: Require the new cumulative root to provably include all accounts from the previous root at equal or greater amounts before accepting the update.

---

### Proof of Concept

1. Owner calls `setMerkleRoot(root1)`. `currentIndex = 1`, `currentMerkleRoot = root1`. Root1 contains leaf `(index=1, account=UserA, cumulativeAmount=100e18)`.
2. UserA is eligible for 100 KERNEL but does not claim immediately.
3. Owner discovers an error in root1 and calls `setMerkleRoot(root2)`. `currentIndex = 2`, `currentMerkleRoot = root2`. Root2 contains leaves with `index=2`; UserA is accidentally omitted.
4. UserA calls `claim(1, userA, 100e18, proofFromRoot1)`.
   - `index=1 <= currentIndex=2` → passes index check.
   - `isClaimed(1, userA)` → false (never claimed) → passes.
   - `MerkleProofUpgradeable.verify(proofFromRoot1, root2, node)` → **false** → reverts `InvalidMerkleProof`.
5. UserA has no valid proof for root2 (they are not in it). Their 100 KERNEL are permanently frozen in the contract. [5](#0-4) [6](#0-5)

### Citations

**File:** contracts/KERNEL/KernelMerkleDistributor.sol (L163-164)
```text
    /// @notice The current merkle root
    bytes32 public currentMerkleRoot;
```

**File:** contracts/KERNEL/KernelMerkleDistributor.sol (L307-323)
```text
        if (index == 0 || index > currentIndex) {
            revert InvalidIndex();
        }

        if (account != msg.sender) {
            revert Unauthorized();
        }

        if (isClaimed(index, account)) {
            revert AlreadyClaimed();
        }

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
