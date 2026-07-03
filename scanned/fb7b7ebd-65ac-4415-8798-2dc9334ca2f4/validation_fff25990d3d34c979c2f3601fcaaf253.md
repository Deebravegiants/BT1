### Title
Merkle Proof Leaf Does Not Bind to Contract Address, Enabling Cross-Instance Double-Claim - (File: contracts/KERNEL/KernelTop100MerkleDistributor.sol)

---

### Summary

`KernelTop100MerkleDistributor._verifyClaimProof()` constructs the merkle leaf without including the contract address or any distributor-specific identifier. If multiple instances of this contract are deployed sharing the same merkle root — a realistic scenario for successive vesting rounds or replacement deployments — any eligible user can replay the same proof across every instance and claim their full allocation from each one.

---

### Finding Description

In `_verifyClaimProof()`, the leaf is computed as:

```solidity
bytes32 leaf = keccak256(abi.encodePacked(user, amount));
``` [1](#0-0) 

No contract address, chain ID, or distributor-specific salt is included in the preimage. The merkle root is fixed at initialization and is never updated:

```solidity
merkleRoot = _merkleRoot;
``` [2](#0-1) 

Claim state is tracked per-instance in `userClaims[user]`:

```solidity
userClaims[user].lastClaimTimestamp = block.timestamp;
userClaims[user].amountClaimed += claimableAmount;
``` [3](#0-2) 

Because the leaf does not commit to `address(this)`, a proof `(user, amount, merkleProof)` that is valid against root `R` on instance A is equally valid against root `R` on instance B. Each instance's `userClaims` mapping is independent, so a user who has fully claimed from instance A can replay the identical proof on instance B and receive a second full allocation.

This is structurally identical to the reported vulnerability: just as `allowedDiscriminator1` (the open, network-level discriminator) allows the same withdrawal snapshot to be accepted by any bridge on the network, the contract-address-free leaf allows the same merkle proof to be accepted by any distributor instance sharing the same root.

---

### Impact Explanation

An eligible user can drain KERNEL tokens from every deployed instance of `KernelTop100MerkleDistributor` that shares the same merkle root, receiving a multiple of their legitimate allocation. This is direct theft of unclaimed yield (KERNEL tokens) from the protocol's distributor contracts.

**Impact: High** — theft of unclaimed yield.

---

### Likelihood Explanation

`KernelTop100MerkleDistributor` is an upgradeable contract initialized with a fixed merkle root. The protocol is likely to deploy multiple instances over time (e.g., for successive vesting tranches, for different reward seasons, or as a replacement when reconfiguring parameters). Any two instances initialized with the same root — which is a natural operational pattern when the same eligible-user set is reused — immediately expose the full balance of the second instance to replay claims. No privileged access is required; any address present in the merkle tree can execute the attack.

**Likelihood: Medium.**

---

### Recommendation

Bind the leaf to the specific contract instance by including `address(this)` (and optionally `block.chainid`) in the preimage:

```solidity
bytes32 leaf = keccak256(abi.encodePacked(address(this), block.chainid, user, amount));
```

This ensures a proof generated for one distributor instance is cryptographically invalid on any other instance, even if both share the same root.

---

### Proof of Concept

1. Protocol deploys `KernelTop100MerkleDistributor` **instance A** with `merkleRoot = R`, funded with 1 000 KERNEL.
2. Protocol later deploys **instance B** with the same `merkleRoot = R` for a second vesting tranche, funded with another 1 000 KERNEL.
3. Alice is in the merkle tree with `amount = 100`. She holds a valid proof `π` such that `MerkleProof.verify(π, R, keccak256(abi.encodePacked(alice, 100))) == true`.
4. Alice calls `claim(100, π)` on **instance A** → `_verifyClaimProof` passes; Alice receives ≈100 KERNEL (minus fee). `userClaims[alice].amountClaimed = 100` on instance A.
5. Alice calls `claim(100, π)` on **instance B** → `_verifyClaimProof` passes again (same leaf, same root); `userClaims[alice].amountClaimed` on instance B starts at 0, so Alice receives another ≈100 KERNEL.
6. Alice has claimed ≈200 KERNEL instead of the intended ≈100, draining instance B's allocation for her entry. [4](#0-3) [5](#0-4)

### Citations

**File:** contracts/KERNEL/KernelTop100MerkleDistributor.sol (L216-217)
```text
        merkleRoot = _merkleRoot;
        vestingStartTimestamp = _vestingStartTimestamp;
```

**File:** contracts/KERNEL/KernelTop100MerkleDistributor.sol (L281-298)
```text
    function _verifyClaimProof(address user, uint256 amount, bytes32[] calldata merkleProof) internal view {
        UtilLib.checkNonZeroAddress(user);

        if (merkleRoot == bytes32(0)) {
            revert ZeroValueProvided();
        }

        if (amount == 0) {
            revert ZeroValueProvided();
        }

        // Verify the merkle proof
        bytes32 leaf = keccak256(abi.encodePacked(user, amount));
        bool isValid = MerkleProofUpgradeable.verify(merkleProof, merkleRoot, leaf);

        if (!isValid) {
            revert InvalidMerkleProof();
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
