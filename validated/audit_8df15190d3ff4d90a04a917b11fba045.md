### Title
Cross-contract Merkle proof replay allows users to drain tokens from multiple distributor contracts - (File: contracts/utils/MerkleDistributor/MerkleDistributor.sol / contracts/KERNEL/KernelMerkleDistributor.sol)

### Summary
Both `MerkleDistributor` and `KernelMerkleDistributor` compute their Merkle leaf hashes using an identical format that omits the contract address. If the same Merkle root is ever set on both contracts — a realistic operational scenario when a single off-chain distribution system services multiple reward programs — a user can replay a valid proof from one contract on the other, claiming tokens they are not entitled to.

### Finding Description

`MerkleDistributor.claim()` computes the leaf as:

```solidity
bytes32 node = keccak256(abi.encodePacked(index, account, cumulativeAmount));
```

`KernelMerkleDistributor._processClaim()` computes the leaf identically:

```solidity
bytes32 node = keccak256(abi.encodePacked(index, account, cumulativeAmount));
```

Neither includes `address(this)` in the hash. The leaf encoding is byte-for-byte identical across both contracts. Any Merkle proof `(index, account, cumulativeAmount, proof[])` that verifies against a root on one contract will also verify against the same root on the other contract.

The `setMerkleRoot` admin function on both contracts accepts any `bytes32` root with no binding to the contract's own address:

```solidity
function setMerkleRoot(bytes32 _merkleRootToSet) external onlyOwner {
    currentMerkleRoot = _merkleRootToSet;
    ...
}
```

When a single off-chain distribution pipeline generates one Merkle tree covering both ERC20 token rewards (served by `MerkleDistributor`) and KERNEL token rewards (served by `KernelMerkleDistributor`), the same root is pushed to both contracts. A user's proof for their ERC20 entitlement is then structurally identical to a valid proof on `KernelMerkleDistributor`, allowing them to claim KERNEL tokens they were never allocated.

### Impact Explanation

**Impact: High — Theft of unclaimed yield.**

A user who holds a valid proof `(index=N, account=user, cumulativeAmount=X)` against the shared root can call `KernelMerkleDistributor.claim()` (or `claimAndStake()`) and receive up to `X` KERNEL tokens (minus fee) that belong to other participants. The `userClaims` mappings are independent per contract, so claiming on one does not mark the claim as used on the other. The attacker drains KERNEL tokens from `KernelMerkleDistributor`'s balance, directly stealing yield owed to legitimate recipients.

### Likelihood Explanation

**Likelihood: Low.**

Exploitation requires the same Merkle root to be set on both contracts. This is not possible through a purely user-controlled path — it requires the owner to push the same root to both contracts, which occurs when a single off-chain rewards pipeline services multiple distributor contracts without binding roots to a specific contract address. This is an operationally plausible but not guaranteed condition.

### Recommendation

Include `address(this)` in the leaf hash in both contracts:

```solidity
// MerkleDistributor.sol line 120
bytes32 node = keccak256(abi.encodePacked(address(this), index, account, cumulativeAmount));

// KernelMerkleDistributor.sol line 320
bytes32 node = keccak256(abi.encodePacked(address(this), index, account, cumulativeAmount));
```

This ensures a proof generated for one contract is cryptographically invalid on any other contract, regardless of whether the same root is set.

### Proof of Concept

1. Owner sets the same Merkle root `R` on both `MerkleDistributor` (distributing rsETH rewards) and `KernelMerkleDistributor` (distributing KERNEL).
2. Off-chain system issues user Alice a proof `P` for leaf `(index=3, alice, 500e18)` against root `R`.
3. Alice calls `MerkleDistributor.claim(3, alice, 500e18, P)` — succeeds, receives 500 rsETH reward tokens.
4. Alice calls `KernelMerkleDistributor.claim(3, alice, 500e18, P)` — leaf hash is identical, root is identical, `isClaimed` is false on this contract → succeeds, Alice receives 500 KERNEL tokens she was never allocated.
5. Alice has now claimed from both contracts using one proof, stealing KERNEL tokens from the distributor's balance. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

### Citations

**File:** contracts/utils/MerkleDistributor/MerkleDistributor.sol (L119-122)
```text
        // Verify the merkle proof.
        bytes32 node = keccak256(abi.encodePacked(index, account, cumulativeAmount));
        if (!MerkleProofUpgradeable.verify(merkleProof, currentMerkleRoot, node)) {
            revert InvalidMerkleProof();
```

**File:** contracts/utils/MerkleDistributor/MerkleDistributor.sol (L156-166)
```text
    function setMerkleRoot(bytes32 _merkleRootToSet) external onlyOwner {
        if (_merkleRootToSet == bytes32(0)) {
            revert ZeroValueProvided();
        }

        currentMerkleRoot = _merkleRootToSet;

        currentMerkleRootIndex++;
        currentIndex++;

        emit MerkleRootSet(currentMerkleRootIndex, currentMerkleRoot);
```

**File:** contracts/KERNEL/KernelMerkleDistributor.sol (L319-322)
```text
        // Verify the merkle proof
        bytes32 node = keccak256(abi.encodePacked(index, account, cumulativeAmount));
        if (!MerkleProofUpgradeable.verify(merkleProof, currentMerkleRoot, node)) {
            revert InvalidMerkleProof();
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
