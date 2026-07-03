### Title
Missing `msg.sender == account` Validation Allows Forced Fee Extraction from Any Claimant - (File: contracts/utils/MerkleDistributor/MerkleDistributor.sol)

---

### Summary

The `claim` function in `MerkleDistributor.sol` does not verify that `msg.sender == account`. Any external caller who possesses a valid Merkle proof for a victim can trigger the victim's claim, forcing the protocol fee to be deducted from the victim's entitled tokens. This is the direct analog to the external report's non-context-aware injection: just as the NEAR contract accepted and processed attacker-injected data as legitimate, this contract accepts and processes an attacker-submitted claim on behalf of any account as legitimate, causing unintended financial consequences for the victim.

---

### Finding Description

`MerkleDistributor.claim` accepts an arbitrary `account` parameter and processes the full claim lifecycle — Merkle proof verification, fee deduction, and token transfer — without ever checking that `msg.sender == account`. [1](#0-0) 

The fee is computed and sent to `protocolTreasury` before the remainder reaches `account`: [2](#0-1) 

The sibling contract `KernelMerkleDistributor` explicitly guards against this with:

```solidity
if (account != msg.sender) {
    revert Unauthorized();
}
``` [3](#0-2) 

`MerkleDistributor.sol` has no equivalent guard. Merkle proofs for all eligible accounts are typically published off-chain (required for users to claim), making every eligible account's proof publicly available to an attacker.

---

### Impact Explanation

An attacker calls `claim(index, victimAddress, cumulativeAmount, victimProof)` for any eligible account. The contract deducts up to `MAX_FEE_IN_BPS = 1000` basis points (10%) of the victim's claimable amount and routes it to `protocolTreasury`. The victim receives fewer tokens than their full entitlement. This constitutes **theft of unclaimed yield** — the victim permanently loses up to 10% of their entitled distribution with no recourse, as the claim state is updated and the index is marked claimed. [4](#0-3) 

---

### Likelihood Explanation

The attack requires only:
1. A valid Merkle proof for the target account — these are public by design (users need them to claim).
2. A single transaction with no special privileges.

The attacker bears only gas cost and gains nothing directly, but can systematically drain the fee entitlement of every eligible account in one sweep. The attack is trivially scriptable against all leaves in the published Merkle tree.

---

### Recommendation

Add the same caller restriction present in `KernelMerkleDistributor._processClaim`:

```solidity
if (account != msg.sender) {
    revert Unauthorized();
}
```

Insert this check at the top of the `claim` function in `MerkleDistributor.sol`, before the Merkle proof verification. [5](#0-4) 

---

### Proof of Concept

1. Owner sets `feeInBPS = 1000` (10%) and publishes a Merkle root. Alice is entitled to 1000 tokens; her leaf is `keccak256(abi.encodePacked(1, alice, 1000))` and her proof is public.
2. Attacker calls `MerkleDistributor.claim(1, alice, 1000, aliceProof)`.
3. Contract verifies the proof (valid), computes `fee = 100`, `amountToSend = 900`.
4. 100 tokens are transferred to `protocolTreasury`; 900 tokens are transferred to Alice.
5. `userClaims[alice].lastClaimedIndex = 1` — Alice's claim is permanently consumed.
6. Alice loses 100 tokens she would have received in full had she claimed herself. The attacker can repeat this for every account in the tree. [6](#0-5)

### Citations

**File:** contracts/utils/MerkleDistributor/MerkleDistributor.sol (L47-47)
```text
    uint256 public constant MAX_FEE_IN_BPS = 1000;
```

**File:** contracts/utils/MerkleDistributor/MerkleDistributor.sol (L96-146)
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
```

**File:** contracts/KERNEL/KernelMerkleDistributor.sol (L311-313)
```text
        if (account != msg.sender) {
            revert Unauthorized();
        }
```
