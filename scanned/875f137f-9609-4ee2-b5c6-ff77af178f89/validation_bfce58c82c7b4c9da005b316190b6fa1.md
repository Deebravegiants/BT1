Looking at the `MerkleDistributor` contract in full, I need to trace the exact mechanics of `setMerkleRoot()` and `claim()` to determine if the described exploit path is real.

### Title
Owner Can Permanently Invalidate Unclaimed Yield by Replacing Merkle Root Without Carrying Forward Prior Allocations — (`contracts/utils/MerkleDistributor/MerkleDistributor.sol`)

---

### Summary

`MerkleDistributor.setMerkleRoot()` unconditionally overwrites `currentMerkleRoot` with no requirement that the new root carries forward all previously allocated but unclaimed amounts. Because `claim()` verifies proofs exclusively against `currentMerkleRoot`, any user whose leaf is absent from the new root permanently loses their unclaimed yield with no recovery path.

---

### Finding Description

`setMerkleRoot()` has a single guard — the new root must be non-zero — and then immediately replaces the live root: [1](#0-0) 

The contract stores **only one root at a time**. No historical roots are retained: [2](#0-1) 

`claim()` verifies the caller's proof exclusively against `currentMerkleRoot`: [3](#0-2) 

The index guard in `claim()` does **not** protect against this. After `setMerkleRoot()` increments `currentIndex` to 2, a user submitting `index=1` still passes `index > currentIndex` (1 ≤ 2), but their proof is then verified against the new root and fails: [4](#0-3) 

The contract uses a **cumulative** claim model — `claimableAmount = cumulativeAmount - userClaims[account].cumulativeAmount` — which architecturally implies that each new root must carry forward all prior allocations: [5](#0-4) 

There is no time-lock, no grace period, no snapshot of the old root, and no on-chain enforcement that the new root subsumes all prior unclaimed allocations. The invariant is entirely off-chain and unenforced.

---

### Impact Explanation

Any user whose leaf is omitted from the new root loses their entire unclaimed cumulative allocation permanently. The tokens remain locked in the contract with no callable path to recover them. This matches **High — Theft/permanent freezing of unclaimed yield**.

---

### Likelihood Explanation

The owner role is required, which reduces likelihood. However, this does **not** require malicious intent: a routine root rotation (e.g., a scripting error, a recomputed tree that drops inactive addresses, or a partial snapshot) can accidentally omit users. The contract provides zero on-chain protection against this class of mistake. Given that Merkle root updates are expected to be frequent operational events, the probability of accidental omission over the protocol's lifetime is non-trivial.

---

### Recommendation

1. **Enforce cumulative carry-forward off-chain** with a mandatory audit step before each `setMerkleRoot()` call, and document this as a hard invariant.
2. **Add a time-lock** (e.g., a two-step commit/reveal with a delay) so users can claim against the old root before it is replaced.
3. **Store the previous root** and allow claims against it for a grace window:
   ```solidity
   bytes32 public previousMerkleRoot;
   uint256 public rootUpdatedAt;
   uint256 public constant GRACE_PERIOD = 7 days;
   ```
   Then in `claim()`, also accept proofs against `previousMerkleRoot` if `block.timestamp < rootUpdatedAt + GRACE_PERIOD`.
4. Alternatively, use a **bitmap of claimed indices per root** so each root epoch is independently claimable.

---

### Proof of Concept

```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.27;

// Pseudocode — run against a local fork or Foundry test

function testStaleRootInvalidatesUserClaim() public {
    // 1. Owner sets root N containing user A with index=1, cumulativeAmount=100e18
    bytes32 rootN = buildMerkleRoot([(index=1, userA, 100e18)]);
    distributor.setMerkleRoot(rootN);

    // 2. Owner sets root N+1 WITHOUT including user A
    bytes32 rootN1 = buildMerkleRoot([(index=2, userB, 50e18)]);
    distributor.setMerkleRoot(rootN1);

    // 3. User A attempts to claim with their valid proof from root N
    bytes32[] memory proofA = buildProof(rootN, index=1, userA, 100e18);
    vm.prank(userA);
    vm.expectRevert(IMerkleDistributor.InvalidMerkleProof.selector);
    distributor.claim(1, userA, 100e18, proofA);
    // => reverts: proof valid for rootN but currentMerkleRoot is now rootN1

    // 4. No recovery path exists — userA's 100e18 is permanently unclaimable
    assertEq(IERC20(token).balanceOf(userA), 0);
}
``` [1](#0-0) [3](#0-2)

### Citations

**File:** contracts/utils/MerkleDistributor/MerkleDistributor.sol (L53-56)
```text
    uint256 public currentMerkleRootIndex;
    bytes32 public currentMerkleRoot;

    uint256 public currentIndex;
```

**File:** contracts/utils/MerkleDistributor/MerkleDistributor.sol (L111-113)
```text
        if (index == 0 || index > currentIndex) {
            revert InvalidIndex();
        }
```

**File:** contracts/utils/MerkleDistributor/MerkleDistributor.sol (L119-123)
```text
        // Verify the merkle proof.
        bytes32 node = keccak256(abi.encodePacked(index, account, cumulativeAmount));
        if (!MerkleProofUpgradeable.verify(merkleProof, currentMerkleRoot, node)) {
            revert InvalidMerkleProof();
        }
```

**File:** contracts/utils/MerkleDistributor/MerkleDistributor.sol (L126-131)
```text
        uint256 claimableAmount = cumulativeAmount - userClaims[account].cumulativeAmount;

        // Ensure there is something to claim
        if (claimableAmount == 0) {
            revert NoTokensToClaim();
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
