### Title
Missing Caller Ownership Check in `claim()` Allows Anyone to Force Fee-Deducted Claims on Behalf of Any Account - (File: contracts/utils/MerkleDistributor/MerkleDistributor.sol)

---

### Summary

`MerkleDistributor.claim()` accepts an arbitrary `account` parameter but never verifies that `msg.sender == account`. Any unprivileged caller can trigger a claim for any victim address, forcing the victim's allocation to be disbursed with the protocol fee deducted — permanently reducing the victim's received yield. The sibling contract `KernelMerkleDistributor` correctly guards against this with an explicit `account != msg.sender` revert, confirming the omission in `MerkleDistributor` is a defect.

---

### Finding Description

`MerkleDistributor.claim()` is a public, permissionless function that accepts a caller-supplied `account` address:

```solidity
function claim(
    uint256 index,
    address account,
    uint256 cumulativeAmount,
    bytes32[] calldata merkleProof
) external override whenNotPaused {
``` [1](#0-0) 

The function verifies the merkle proof against `(index, account, cumulativeAmount)` and then deducts a fee before transferring:

```solidity
uint256 fee = (claimableAmount * feeInBPS) / 10_000;
uint256 amountToSend = claimableAmount - fee;
IERC20(token).safeTransfer(account, amountToSend);
IERC20(token).safeTransfer(protocolTreasury, fee);
``` [2](#0-1) 

There is **no check** that `msg.sender == account` anywhere in the function or its callpath. Merkle proofs for any account are derivable from the off-chain distribution data (they are public inputs). An attacker can supply a victim's valid `(index, account, cumulativeAmount, merkleProof)` tuple and force the claim to execute, with the fee permanently extracted from the victim's allocation.

By contrast, `KernelMerkleDistributor._processClaim()` explicitly enforces caller identity:

```solidity
if (account != msg.sender) {
    revert Unauthorized();
}
``` [3](#0-2) 

This confirms the pattern is intentional in the newer contract and absent in `MerkleDistributor`.

---

### Impact Explanation

**High — Theft of unclaimed yield.**

The fee (`feeInBPS`, up to `MAX_FEE_IN_BPS = 1000`, i.e. 10%) is deducted from the victim's claimable amount and sent to `protocolTreasury`. The victim receives less than their full entitlement and cannot reclaim the fee. The victim's `userClaims` state is updated, preventing any future claim for the same index. The attacker does not need to own any tokens or hold any role — only a valid merkle proof for the target account is required. [4](#0-3) 

---

### Likelihood Explanation

**High.** The entry point is fully permissionless. Merkle proofs are public (derived from off-chain distribution data). The attacker needs no capital, no role, and no prior interaction with the protocol. The attack can be executed against any account that has an unclaimed allocation, at any time after the merkle root is set.

---

### Recommendation

Add a caller identity check at the top of `claim()`, mirroring the guard already present in `KernelMerkleDistributor`:

```solidity
if (account != msg.sender) {
    revert Unauthorized();
}
``` [5](#0-4) 

---

### Proof of Concept

1. The protocol sets a merkle root. Alice has a valid leaf `(index=1, account=Alice, cumulativeAmount=1000e18)` and her proof is derivable from the public distribution data.
2. Attacker Bob calls:
   ```solidity
   MerkleDistributor.claim(1, Alice, 1000e18, aliceProof);
   ```
3. The contract verifies the proof (valid), computes `fee = 1000e18 * feeInBPS / 10_000` (e.g. 100e18 at 10%), sends `900e18` to Alice and `100e18` to `protocolTreasury`.
4. `userClaims[Alice].lastClaimedIndex = 1` is set — Alice cannot claim index 1 again.
5. Alice permanently loses 100e18 tokens she was entitled to receive in full. [6](#0-5)

### Citations

**File:** contracts/utils/MerkleDistributor/MerkleDistributor.sol (L47-51)
```text
    uint256 public constant MAX_FEE_IN_BPS = 1000;

    address public override token;
    address public protocolTreasury;
    uint256 public feeInBPS;
```

**File:** contracts/utils/MerkleDistributor/MerkleDistributor.sol (L96-123)
```text
    /// @inheritdoc IMerkleDistributor
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
```

**File:** contracts/utils/MerkleDistributor/MerkleDistributor.sol (L133-146)
```text
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
```

**File:** contracts/KERNEL/KernelMerkleDistributor.sol (L311-313)
```text
        if (account != msg.sender) {
            revert Unauthorized();
        }
```
