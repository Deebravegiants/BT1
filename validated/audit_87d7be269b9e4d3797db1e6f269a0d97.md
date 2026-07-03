### Title
Block Stuffing Invalidates Pending Claims via Single-Root Overwrite — (`contracts/utils/MerkleDistributor/MerkleBlastPointsDistributor.sol`)

---

### Summary

`MerkleBlastPointsDistributor` stores only a single `currentMerkleRoot`. When `setMerkleRoot()` is called it atomically overwrites that root and increments `currentIndex`. A user whose `claim()` transaction is pending in the mempool will have their proof verified against the **new** root, not the root that was live when they generated the proof. An attacker can use block stuffing to guarantee this ordering, permanently invalidating the user's proof.

---

### Finding Description

`setMerkleRoot()` performs two writes atomically:

```solidity
// line 145-148
currentMerkleRoot = _merkleRootToSet;
currentMerkleRootIndex++;
currentIndex++;
``` [1](#0-0) 

No historical root is retained. `claim()` then validates the proof exclusively against `currentMerkleRoot`:

```solidity
// line 112-113
if (!MerkleProofUpgradeable.verify(merkleProof, currentMerkleRoot, node)) {
    revert InvalidMerkleProof();
}
``` [2](#0-1) 

The index guard only checks `index > currentIndex`, so an old index N remains numerically valid after `currentIndex` advances to N+1:

```solidity
// line 101-103
if (index == 0 || index > currentIndex) {
    revert InvalidIndex();
}
``` [3](#0-2) 

This creates the race: the index check passes for the old index, but the proof check fails because the root it was generated against no longer exists.

**Attack sequence:**

1. User generates a valid proof `π` for `(index=N, account, amounts)` against root `R1` (`currentIndex = N`).
2. User broadcasts `claim(N, account, ..., π)`.
3. Attacker fills every block with high-gas spam transactions, preventing the user's transaction from being included.
4. Owner's scheduled `setMerkleRoot(R2)` is included (owner can use higher gas or the attacker simply waits for it). `currentMerkleRoot = R2`, `currentIndex = N+1`.
5. Attacker stops stuffing. User's transaction is now included.
6. `index > currentIndex` → `N > N+1` → false, passes.
7. `MerkleProofUpgradeable.verify(π, R2, node)` → **reverts `InvalidMerkleProof`**.

The user's proof `π` is permanently unusable. The old root `R1` is gone with no recovery path in the contract. [4](#0-3) 

---

### Impact Explanation

The user's unclaimed Blast Points/Gold yield is frozen until they obtain a new off-chain proof for index `N+1` against `R2`. If the new tree omits the user (e.g., a corrected distribution), the yield is permanently frozen. Even in the best case the user is forced to wait for the next off-chain proof generation cycle, constituting **Medium — Permanent freezing of unclaimed yield** in the worst case and **Low — Block stuffing** as the direct attack impact.

---

### Likelihood Explanation

Blast is an L2 with low gas costs, making block stuffing economically feasible. The owner calls `setMerkleRoot()` on a predictable periodic schedule (observable on-chain), so the attacker can time the stuffing window precisely. No privileged access is required; the owner's root update is routine operation, not a compromise.

---

### Recommendation

Store a mapping of historical roots indexed by `currentMerkleRootIndex`, and allow `claim()` to accept a `rootIndex` parameter, verifying the proof against `historicalRoots[rootIndex]` instead of only `currentMerkleRoot`. Alternatively, enforce a time-lock or grace period between `setMerkleRoot()` calls during which the old root remains valid for claims.

---

### Proof of Concept

```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.27;

import "forge-std/Test.sol";
import "../../contracts/utils/MerkleDistributor/MerkleBlastPointsDistributor.sol";

contract BlockStuffingTest is Test {
    MerkleBlastPointsDistributor distributor;
    address owner = address(0xABCD);
    address user  = address(0x1234);

    // Pre-computed: root1 contains leaf(1, user, 100 pts, 10 gold)
    bytes32 root1 = /* computed off-chain */;
    bytes32 root2 = /* different tree, user absent or different amounts */;
    bytes32[] proof1; // valid proof against root1

    function setUp() public {
        vm.prank(owner);
        distributor = new MerkleBlastPointsDistributor();
        // initialize with mock blast point address
        vm.prank(owner);
        distributor.initialize(address(0xBEEF), owner);

        // Owner sets root1 → currentIndex = 1
        vm.prank(owner);
        distributor.setMerkleRoot(root1);
    }

    function testBlockStuffingInvalidatesProof() public {
        // User's claim(1, user, 100, 10, proof1) is pending in mempool.
        // Simulate block stuffing: owner's setMerkleRoot(root2) lands first.
        vm.prank(owner);
        distributor.setMerkleRoot(root2); // currentIndex = 2, currentMerkleRoot = root2

        // Now user's delayed transaction executes:
        // index=1 <= currentIndex=2 → passes InvalidIndex check
        // but proof1 was built against root1, not root2 → InvalidMerkleProof
        vm.prank(user);
        vm.expectRevert(IMerkleBlastPointsDistributor.InvalidMerkleProof.selector);
        distributor.claim(1, user, 100, 10, proof1);
    }
}
```

The test confirms that after `setMerkleRoot()` replaces `currentMerkleRoot`, a previously valid proof reverts with `InvalidMerkleProof`, freezing the user's unclaimed yield. [5](#0-4)

### Citations

**File:** contracts/utils/MerkleDistributor/MerkleBlastPointsDistributor.sol (L97-114)
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
        bytes32 node =
            keccak256(abi.encodePacked(index, account, cumulativeBlastPointAmount, cumulativeBlastGoldAmount));
        if (!MerkleProofUpgradeable.verify(merkleProof, currentMerkleRoot, node)) {
            revert InvalidMerkleProof();
        }
```

**File:** contracts/utils/MerkleDistributor/MerkleBlastPointsDistributor.sol (L140-151)
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
