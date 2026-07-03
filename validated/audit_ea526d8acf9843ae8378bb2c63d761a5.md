### Title
Missing `msg.sender == account` Authorization in `claim()` Allows Anyone to Force-Claim on Behalf of Any User, Stealing Their Fee-Exempt Yield - (File: contracts/utils/MerkleDistributor/MerkleDistributor.sol)

---

### Summary

`MerkleDistributor.claim()` accepts an arbitrary `account` address parameter but never verifies that `msg.sender == account`. Any unprivileged caller can trigger a claim for any user at any time, forcing an immediate fee deduction from that user's allocation. The sister contract `KernelMerkleDistributor` correctly guards against this with an explicit `account != msg.sender` revert, confirming the omission is a defect.

---

### Finding Description

`MerkleDistributor.sol` exposes a public `claim` function:

```solidity
function claim(
    uint256 index,
    address account,
    uint256 cumulativeAmount,
    bytes32[] calldata merkleProof
)
    external
    override
    whenNotPaused
{
    // ... merkle proof verified against (index, account, cumulativeAmount) ...

    uint256 fee = (claimableAmount * feeInBPS) / 10_000;
    uint256 amountToSend = claimableAmount - fee;

    IERC20(token).safeTransfer(account, amountToSend);          // victim receives less
    IERC20(token).safeTransfer(protocolTreasury, fee);          // fee taken immediately
}
```

There is no check that `msg.sender == account`. [1](#0-0) 

By contrast, `KernelMerkleDistributor._processClaim()` explicitly enforces caller identity:

```solidity
if (account != msg.sender) {
    revert Unauthorized();
}
``` [2](#0-1) 

The Merkle proof only proves that `(index, account, cumulativeAmount)` is a valid leaf — it does not prove that the caller is `account`. Any third party who observes the Merkle tree (which is public) can reconstruct a valid proof for any leaf and call `claim` on behalf of any user. [3](#0-2) 

---

### Impact Explanation

**High — Theft of unclaimed yield.**

A user's rational strategy may be to defer claiming until `feeInBPS` is reduced to zero (the owner can set it to 0 via `setFeeInBPS`), or until a more tax-efficient moment. An attacker can front-run that window by force-claiming for the user at the current non-zero fee rate, permanently diverting the fee portion of the user's allocation to `protocolTreasury` instead of to the user. The user receives `claimableAmount - fee` rather than `claimableAmount`. The fee is irrecoverable — once the claim state is updated (`userClaims[account].cumulativeAmount = cumulativeAmount`) the user can never re-claim that epoch. [4](#0-3) 

---

### Likelihood Explanation

**High.** The Merkle tree leaves are public (the root is set on-chain and the full tree is published off-chain for users to generate proofs). Any attacker can enumerate all leaves, build proofs for every user, and batch-call `claim` for all of them in a single block. No special privilege, capital, or oracle access is required. The only gate is `whenNotPaused`, which is a normal operating state. [5](#0-4) 

---

### Recommendation

Add a caller-identity check identical to the one in `KernelMerkleDistributor`:

```solidity
if (account != msg.sender) {
    revert Unauthorized();
}
```

Insert this check immediately after the `isClaimed` guard, before any state mutation or token transfer. [2](#0-1) 

---

### Proof of Concept

1. Owner sets `feeInBPS = 500` (5 %) and publishes a Merkle root where `alice` is entitled to `1000e18` tokens.
2. Alice intends to wait until the owner sets `feeInBPS = 0` before claiming.
3. Attacker observes the Merkle tree, reconstructs Alice's proof `(index=1, account=alice, cumulativeAmount=1000e18, proof=[...])`.
4. Attacker calls `MerkleDistributor.claim(1, alice, 1000e18, proof)`.
5. Contract executes:
   - `fee = 1000e18 * 500 / 10_000 = 50e18`
   - `amountToSend = 950e18`
   - Transfers `950e18` to Alice, `50e18` to `protocolTreasury`.
   - Marks `userClaims[alice].cumulativeAmount = 1000e18`.
6. Alice can never reclaim the `50e18` fee — her epoch is permanently consumed. [4](#0-3)

### Citations

**File:** contracts/utils/MerkleDistributor/MerkleDistributor.sol (L97-147)
```text
    function claim(
        uint256 index,
        address account,
        uint256 cumulativeAmount,
        bytes32[] calldata merkleProof
    )
        external
        override
        whenNotPaused
    {
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

        // Calculate the claimable amount
        uint256 claimableAmount = cumulativeAmount - userClaims[account].cumulativeAmount;

        // Ensure there is something to claim
        if (claimableAmount == 0) {
            revert NoTokensToClaim();
        }

        // Update user claim info, and send the token.
        userClaims[account].lastClaimedIndex = index;
        userClaims[account].cumulativeAmount = cumulativeAmount;

        // Send the claimable amount to the user - deducting the fee
        uint256 fee = (claimableAmount * feeInBPS) / 10_000;
        uint256 amountToSend = claimableAmount - fee;

        IERC20(token).safeTransfer(account, amountToSend);

        // Send the fee to the protocol treasury
        IERC20(token).safeTransfer(protocolTreasury, fee);

        emit Claimed(index, account, claimableAmount);
    }
```

**File:** contracts/KERNEL/KernelMerkleDistributor.sol (L311-313)
```text
        if (account != msg.sender) {
            revert Unauthorized();
        }
```
