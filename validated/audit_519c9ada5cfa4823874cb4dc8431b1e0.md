### Title
`feeInBPS` Can Change Without User Consent Between Merkle Root Publication and Claim - (File: `contracts/KERNEL/KernelMerkleDistributor.sol`)

---

### Summary

`KernelMerkleDistributor` applies `feeInBPS` at the moment a user calls `claim()` or `claimAndStake()`, not at the moment the merkle root encoding their reward entitlement was published. Because the owner can call `setFeeInBPS()` at any time, users who have earned rewards (committed in the merkle tree) can silently receive fewer KERNEL tokens than they were entitled to when the root was set.

---

### Finding Description

In `_processClaim`, the fee deducted from a user's claimable KERNEL amount is computed using the **current** `feeInBPS` state variable: [1](#0-0) 

```solidity
uint256 fee = (claimableAmount * feeInBPS) / FEE_DENOMINATOR;
uint256 amountToSend = claimableAmount - fee;
```

The owner can update `feeInBPS` at any time (up to `MAX_FEE_IN_BPS = 1000`, i.e. 10%) via: [2](#0-1) 

```solidity
function setFeeInBPS(uint256 _feeInBPS) external onlyOwner {
    if (_feeInBPS > MAX_FEE_IN_BPS) revert InvalidFeeInBPS();
    feeInBPS = _feeInBPS;
    emit FeeInBPSUpdated(feeInBPS);
}
```

The merkle root, which encodes each user's `cumulativeAmount`, is set independently: [3](#0-2) 

There is no mechanism to snapshot or lock the fee at the time the root is published. The fee applied at claim time is entirely decoupled from the fee in effect when the user's entitlement was committed.

---

### Impact Explanation

**High — Theft of unclaimed yield.**

A user's claimable KERNEL amount is determined by the merkle root. The fee deducted from that amount is determined by `feeInBPS` at claim time. If the owner raises `feeInBPS` from 0% to 10% after a root is published but before users claim, every pending claimant loses up to 10% of their entitled KERNEL rewards to the protocol treasury — without any on-chain signal or consent mechanism. The lost tokens flow to `protocolTreasury`, constituting a direct transfer of unclaimed yield away from rightful recipients. [4](#0-3) 

---

### Likelihood Explanation

**Medium.** The owner has the unilateral, unconstrained ability to raise `feeInBPS` at any time. There is no timelock, no cap on the rate of change, and no notification mechanism for pending claimants. Merkle roots are published periodically; between publication and the time all users claim, the fee can be changed. Users who delay claiming (e.g., waiting for gas prices, unaware of the new root, or using `claimAndStake` in a later epoch) are silently affected.

---

### Recommendation

Lock the fee at the time the merkle root is published. One approach: store a `feeInBPS` snapshot alongside each merkle root index, and use that snapshot in `_processClaim` rather than the live `feeInBPS` value.

```solidity
mapping(uint256 rootIndex => uint256 feeInBPS) public rootFeeInBPS;

function setMerkleRoot(bytes32 _merkleRootToSet) external onlyOwner {
    ...
    currentIndex++;
    rootFeeInBPS[currentIndex] = feeInBPS; // snapshot fee at root publication
    ...
}

// In _processClaim, use rootFeeInBPS[userClaims[account].lastClaimedIndex + 1]
// (or the index corresponding to the root being claimed against)
```

Alternatively, apply a timelock to `setFeeInBPS` so users have advance notice before any fee change takes effect.

---

### Proof of Concept

1. Owner publishes a merkle root. At this time `feeInBPS = 0`. Alice's `cumulativeAmount` in the tree is `1000e18` KERNEL.
2. Owner calls `setFeeInBPS(1000)` (10%), raising the fee to the maximum.
3. Alice calls `claim(index, alice, 1000e18, proof)`.
4. `_processClaim` computes `fee = (1000e18 * 1000) / 10_000 = 100e18`.
5. Alice receives `900e18` KERNEL instead of the `1000e18` she was entitled to when the root was set.
6. `100e18` KERNEL is transferred to `protocolTreasury`.

Alice had no way to consent to or avoid this fee increase — her only option would have been to claim before the owner changed the fee, but there is no on-chain mechanism guaranteeing she could do so. [5](#0-4)

### Citations

**File:** contracts/KERNEL/KernelMerkleDistributor.sol (L292-346)
```text
    function _processClaim(
        uint256 index,
        address account,
        uint256 cumulativeAmount,
        bytes32[] calldata merkleProof
    )
        internal
        returns (uint256)
    {
        UtilLib.checkNonZeroAddress(account);

        if (currentMerkleRoot == bytes32(0)) {
            revert ZeroValueProvided();
        }

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

        // Calculate the claimable amount
        uint256 claimableAmount = cumulativeAmount - userClaims[account].cumulativeAmount;

        // Ensure there is something to claim
        if (claimableAmount == 0) {
            revert NoTokensToClaim();
        }

        // Update user claim info
        userClaims[account].lastClaimedIndex = index;
        userClaims[account].cumulativeAmount = cumulativeAmount;

        // Calculate the fee and the amount to send
        uint256 fee = (claimableAmount * feeInBPS) / FEE_DENOMINATOR;
        uint256 amountToSend = claimableAmount - fee;

        if (fee > 0) {
            kernel.safeTransfer(protocolTreasury, fee);
        }

        return amountToSend;
    }
```

**File:** contracts/KERNEL/KernelMerkleDistributor.sol (L388-396)
```text
    function setFeeInBPS(uint256 _feeInBPS) external onlyOwner {
        if (_feeInBPS > MAX_FEE_IN_BPS) {
            revert InvalidFeeInBPS();
        }

        feeInBPS = _feeInBPS;

        emit FeeInBPSUpdated(feeInBPS);
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
