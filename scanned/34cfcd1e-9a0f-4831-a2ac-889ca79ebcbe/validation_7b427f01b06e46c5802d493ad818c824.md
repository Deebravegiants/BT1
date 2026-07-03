Looking at the full `claim` function in `MerkleBlastPointsDistributor.sol`, the critical check is whether `msg.sender` must equal `account`.

The analysis is complete. Here is the finding:

---

### Title
Missing `msg.sender == account` Guard Allows Anyone to Consume Any User's Epoch Claim — (`contracts/utils/MerkleDistributor/MerkleBlastPointsDistributor.sol`)

### Summary
`MerkleBlastPointsDistributor.claim()` accepts an arbitrary `account` parameter with no check that `msg.sender == account`. Any third party — including an MEV bot — can call `claim` on behalf of any user, permanently consuming that user's claim slot for the current epoch and preventing them from ever claiming it themselves.

### Finding Description
The `claim` function in `MerkleBlastPointsDistributor` performs no caller-identity check: [1](#0-0) 

The only guards are: root non-zero, valid index range, not-already-claimed, and valid merkle proof. There is no `require(msg.sender == account)` or equivalent.

Compare this to `KernelMerkleDistributor._processClaim()`, which explicitly enforces self-claim: [2](#0-1) 

The developers applied this guard in the token distributor but omitted it in the Blast Points distributor.

After a successful third-party call, the victim's state is permanently updated: [3](#0-2) 

`isClaimed` returns `true` for that index because it checks `userClaims[account].lastClaimedIndex >= index`: [4](#0-3) 

Any subsequent `claim()` call by the victim for the same index reverts with `AlreadyClaimed`.

### Impact Explanation
The `claim` function emits `Claimed` and updates on-chain state but does **not** call any Blast Points transfer function on `IBlastPoints`. The actual Blast Points distribution is off-chain/operator-driven. By front-running the victim's claim, the attacker permanently marks the victim's epoch as claimed. The victim's allocation for that epoch is frozen — they can never claim it. Across all epochs and all users, a systematic MEV bot can freeze every user's unclaimed yield every epoch.

The attacker does not receive the yield themselves, so the precise impact is **Medium — Permanent freezing of unclaimed yield**, not High theft (no value flows to the attacker).

### Likelihood Explanation
The attack requires only:
1. Monitoring the mempool for `setMerkleRoot` transactions (trivial).
2. Reading the new Merkle tree off-chain data (publicly available when the owner publishes it).
3. Pre-computing the victim's proof and bundling `claim(newIndex, victim, ...)` in the same block.

No privileged access, no key compromise, no governance capture. The attack is fully permissionless and automatable.

### Recommendation
Add a self-claim guard identical to the one in `KernelMerkleDistributor`:

```solidity
if (account != msg.sender) {
    revert Unauthorized();
}
```

Insert this check immediately after the `InvalidIndex` check in `claim()`. [5](#0-4) 

### Proof of Concept

```solidity
// Foundry test — two-tx block sequence
function testAttackerConsumesVictimClaim() public {
    // 1. Owner sets new merkle root (epoch 1)
    bytes32 newRoot = ...; // computed from off-chain tree
    vm.prank(owner);
    distributor.setMerkleRoot(newRoot);
    // currentIndex is now 1

    // 2. Attacker (not victim) calls claim for victim using victim's valid proof
    bytes32[] memory proof = ...; // pre-computed from new tree
    vm.prank(attacker);
    distributor.claim(1, victim, victimPoints, victimGold, proof);
    // succeeds — no msg.sender check

    // 3. Victim tries to claim — reverts
    vm.prank(victim);
    vm.expectRevert(IMerkleBlastPointsDistributor.AlreadyClaimed.selector);
    distributor.claim(1, victim, victimPoints, victimGold, proof);
}
``` [6](#0-5)

### Citations

**File:** contracts/utils/MerkleDistributor/MerkleBlastPointsDistributor.sol (L79-83)
```text
    function isClaimed(uint256 index, address account) public view override returns (bool) {
        if (index == 0) revert ZeroValueProvided();

        return userClaims[account].lastClaimedIndex >= index;
    }
```

**File:** contracts/utils/MerkleDistributor/MerkleBlastPointsDistributor.sol (L86-96)
```text
    function claim(
        uint256 index,
        address account,
        uint256 cumulativeBlastPointAmount,
        uint256 cumulativeBlastGoldAmount,
        bytes32[] calldata merkleProof
    )
        external
        override
        whenNotPaused
    {
```

**File:** contracts/utils/MerkleDistributor/MerkleBlastPointsDistributor.sol (L101-107)
```text
        if (index == 0 || index > currentIndex) {
            revert InvalidIndex();
        }

        if (isClaimed(index, account)) {
            revert AlreadyClaimed();
        }
```

**File:** contracts/utils/MerkleDistributor/MerkleBlastPointsDistributor.sol (L126-128)
```text
        userClaims[account].lastClaimedIndex = index;
        userClaims[account].cumulativeBlastPointAmount = cumulativeBlastPointAmount;
        userClaims[account].cumulativeBlastGoldAmount = cumulativeBlastGoldAmount;
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

**File:** contracts/KERNEL/KernelMerkleDistributor.sol (L311-313)
```text
        if (account != msg.sender) {
            revert Unauthorized();
        }
```
