### Title
Merkle Proof Replay Across Multiple Distributor Instances Due to Missing Contract Address in Leaf Encoding - (File: contracts/utils/MerkleDistributor/MerkleDistributor.sol)

---

### Summary

The merkle leaf in every distributor contract in the LRT-rsETH codebase is computed without including the verifying contract's address. This is the direct analog of the reported vulnerability: just as BLS signatures that omit the wallet address can be replayed on any wallet that adopts the same public key, merkle proofs that omit the contract address can be replayed on any distributor contract that sets the same merkle root.

---

### Finding Description

Every merkle distributor in the codebase computes its leaf without binding it to the specific contract address:

**`MerkleDistributor.sol` and `KernelMerkleDistributor.sol`:**
```solidity
bytes32 node = keccak256(abi.encodePacked(index, account, cumulativeAmount));
```

**`KernelTop100MerkleDistributor.sol`** (even weaker — no index either):
```solidity
bytes32 leaf = keccak256(abi.encodePacked(user, amount));
```

**`MerkleBlastPointsDistributor.sol`:**
```solidity
bytes32 node = keccak256(abi.encodePacked(index, account, cumulativeBlastPointAmount, cumulativeBlastGoldAmount));
```

None of these include `address(this)` or `block.chainid` in the leaf. The `MerkleDistributor` is explicitly described as a **generic** contract intended to be deployed multiple times for different tokens. The `KernelMerkleDistributor` and `KernelTop100MerkleDistributor` are also independently deployable.

When the same merkle root is set on two distributor instances — a realistic scenario in a multi-chain protocol that deploys the same reward distribution on multiple chains simultaneously, or when two same-chain distributor instances share the same off-chain reward snapshot — a proof that is valid for Contract A is mathematically identical to a proof valid for Contract B. The `isClaimed` state is stored per-contract, so claiming on Contract A does not mark the claim as used on Contract B.

The root cause is identical to the reported vulnerability: the committed data (the leaf) does not bind to the specific contract context in which it is being verified.

---

### Impact Explanation

An attacker (or any user) who holds a valid merkle proof for Distributor A can submit the same proof to Distributor B (which holds the same root at the same index) and receive a second payout of reward tokens they are not entitled to. This drains tokens from Distributor B that belong to other users' allocations.

- For `MerkleDistributor` (generic, holds any ERC-20): **theft of unclaimed yield / reward tokens** — High impact.
- For `KernelTop100MerkleDistributor` (no index in leaf): the replay surface is even broader since the leaf has fewer distinguishing fields.

The `isClaimed` check only prevents double-claiming within the same contract instance; it provides no cross-contract protection.

---

### Likelihood Explanation

The LRT-rsETH protocol is explicitly multi-chain (L1 + multiple L2s). Deploying the same reward distribution contract with the same merkle root on multiple chains is a standard operational pattern. Both `MerkleDistributor` (generic) and `KernelMerkleDistributor` are designed to be deployed multiple times. The off-chain system that generates roots is shared across deployments. Any time the same root appears on two instances — whether by design (same snapshot, different chains) or by operational coincidence — the replay path is open to any user who has a valid proof, requiring no privilege escalation.

---

### Recommendation

Include `address(this)` (and optionally `block.chainid`) in the leaf hash computation so that a proof is cryptographically bound to the specific contract instance for which it was generated:

```solidity
// MerkleDistributor.sol
bytes32 node = keccak256(abi.encodePacked(address(this), index, account, cumulativeAmount));

// KernelTop100MerkleDistributor.sol
bytes32 leaf = keccak256(abi.encodePacked(address(this), user, amount));
```

The off-chain merkle tree generation must be updated to include the contract address when building leaves. This mirrors the EIP-712 domain separator pattern, which binds signed data to a specific `verifyingContract`.

---

### Proof of Concept

1. Protocol deploys `MerkleDistributor` on Arbitrum (`DistA`) and Optimism (`DistB`), both funded with KERNEL rewards, both with the same merkle root set at `currentIndex = 1`.
2. Alice has a valid proof: `(index=1, account=Alice, cumulativeAmount=1000e18)`.
3. Alice calls `DistA.claim(1, Alice, 1000e18, proof)` on Arbitrum → receives 1000 KERNEL.
4. Alice calls `DistB.claim(1, Alice, 1000e18, proof)` on Optimism → the leaf `keccak256(abi.encodePacked(1, Alice, 1000e18))` is identical; `isClaimed` on `DistB` returns false; proof verifies against the same root → Alice receives another 1000 KERNEL she is not entitled to.
5. Alice has stolen 1000 KERNEL from other users' allocations in `DistB`.

The same attack applies on a single chain if two `MerkleDistributor` instances share the same root (e.g., two reward campaigns with the same eligible set). [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

### Citations

**File:** contracts/utils/MerkleDistributor/MerkleDistributor.sol (L89-94)
```text
    /// @inheritdoc IMerkleDistributor
    function isClaimed(uint256 index, address account) public view override returns (bool) {
        if (index == 0) revert ZeroValueProvided();

        return userClaims[account].lastClaimedIndex >= index;
    }
```

**File:** contracts/utils/MerkleDistributor/MerkleDistributor.sol (L119-121)
```text
        // Verify the merkle proof.
        bytes32 node = keccak256(abi.encodePacked(index, account, cumulativeAmount));
        if (!MerkleProofUpgradeable.verify(merkleProof, currentMerkleRoot, node)) {
```

**File:** contracts/KERNEL/KernelMerkleDistributor.sol (L319-322)
```text
        // Verify the merkle proof
        bytes32 node = keccak256(abi.encodePacked(index, account, cumulativeAmount));
        if (!MerkleProofUpgradeable.verify(merkleProof, currentMerkleRoot, node)) {
            revert InvalidMerkleProof();
```

**File:** contracts/KERNEL/KernelTop100MerkleDistributor.sol (L292-295)
```text
        // Verify the merkle proof
        bytes32 leaf = keccak256(abi.encodePacked(user, amount));
        bool isValid = MerkleProofUpgradeable.verify(merkleProof, merkleRoot, leaf);

```

**File:** contracts/utils/MerkleDistributor/MerkleBlastPointsDistributor.sol (L109-113)
```text
        // Verify the merkle proof.
        bytes32 node =
            keccak256(abi.encodePacked(index, account, cumulativeBlastPointAmount, cumulativeBlastGoldAmount));
        if (!MerkleProofUpgradeable.verify(merkleProof, currentMerkleRoot, node)) {
            revert InvalidMerkleProof();
```
