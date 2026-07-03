### Title
Single-Slot Merkle Root Overwrites Discard All Prior Unclaimed Yield — (`contracts/KERNEL/KernelMerkleDistributor.sol`)

---

### Summary

`setMerkleRoot` stores only one root at a time. Every call silently discards the previous root. Because `_processClaim` verifies proofs exclusively against `currentMerkleRoot`, any user who has not yet claimed before the root is rotated can never prove entitlement from the superseded root, permanently freezing their unclaimed yield.

---

### Finding Description

`setMerkleRoot` unconditionally overwrites `currentMerkleRoot` and increments `currentIndex`: [1](#0-0) 

No historical root is retained anywhere in storage. `_processClaim` then validates the caller's proof against the single live root: [2](#0-1) 

The index guard only checks `index > currentIndex`, so a claim index from a prior epoch passes that check: [3](#0-2) 

But the proof, which was constructed against the old root, will always fail `MerkleProofUpgradeable.verify` against the new root, reverting with `InvalidMerkleProof`. There is no fallback path and no way to recover the old root on-chain.

The cumulative-amount design (line 326) implies the owner is expected to carry forward every user's entitlement into each new root: [4](#0-3) 

The contract provides zero enforcement of this invariant. A root rotation that omits even one user — whether by mistake or by design — permanently destroys that user's claimable yield with no recovery mechanism.

---

### Impact Explanation

**Medium — Permanent freezing of unclaimed yield.**

Any yield provable under a superseded root becomes permanently unclaimable. The tokens remain locked in the contract with no on-chain path to retrieve them. This matches the allowed impact scope exactly.

---

### Likelihood Explanation

The owner is expected to call `setMerkleRoot` periodically (each distribution epoch). A single omission — a user address missing from the new leaf set, a recomputation error, or a deliberate exclusion — triggers the freeze. No attacker capability beyond the normal owner key is required; the flaw activates through ordinary operational use.

---

### Recommendation

Store a mapping of all historical roots indexed by `currentMerkleRootIndex`, and allow `_processClaim` to verify a proof against any stored root whose index matches the caller-supplied `index`. Alternatively, enforce on-chain that every new root's cumulative amounts are ≥ those of the previous root for all users (though this is impractical with Merkle trees). At minimum, emit the full root in `MerkleRootSet` and document that operators must never omit a previously included leaf.

---

### Proof of Concept

```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.27;

// Pseudocode — run on a local fork or Foundry test

// 1. Deploy KernelMerkleDistributor with owner = attacker/operator
// 2. Build root-1 containing leaf: keccak256(abi.encodePacked(1, user, 100e18))
distributor.setMerkleRoot(root1);
// currentIndex == 1, currentMerkleRoot == root1

// 3. Build root-2 that does NOT contain any leaf for `user`
distributor.setMerkleRoot(root2);
// currentIndex == 2, currentMerkleRoot == root2

// 4. User attempts to claim their epoch-1 entitlement
// index=1 passes the guard (1 <= currentIndex=2)
// proof1 was valid against root1, NOT root2
vm.prank(user);
vm.expectRevert(IMerkleDistributor.InvalidMerkleProof.selector);
distributor.claim(1, user, 100e18, proof1);

// 5. No other claim path exists. User's 100e18 KERNEL is permanently frozen.
```

### Citations

**File:** contracts/KERNEL/KernelMerkleDistributor.sol (L307-309)
```text
        if (index == 0 || index > currentIndex) {
            revert InvalidIndex();
        }
```

**File:** contracts/KERNEL/KernelMerkleDistributor.sol (L320-323)
```text
        bytes32 node = keccak256(abi.encodePacked(index, account, cumulativeAmount));
        if (!MerkleProofUpgradeable.verify(merkleProof, currentMerkleRoot, node)) {
            revert InvalidMerkleProof();
        }
```

**File:** contracts/KERNEL/KernelMerkleDistributor.sol (L326-326)
```text
        uint256 claimableAmount = cumulativeAmount - userClaims[account].cumulativeAmount;
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
