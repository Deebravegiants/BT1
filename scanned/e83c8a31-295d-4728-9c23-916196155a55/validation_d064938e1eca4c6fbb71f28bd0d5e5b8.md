### Title
Missing Caller Restriction on `claim()` Allows Anyone to Force Token Claims on Behalf of Any Account - (File: contracts/utils/MerkleDistributor/MerkleDistributor.sol)

### Summary
`MerkleDistributor.claim()` and `MerkleBlastPointsDistributor.claim()` accept an arbitrary `account` parameter but perform no check that `msg.sender == account`. Any external caller with a valid merkle proof can force a claim on behalf of any eligible user. The sibling contract `KernelMerkleDistributor` explicitly guards against this with `if (account != msg.sender) revert Unauthorized()`, confirming the intended design is self-only claiming.

### Finding Description
`MerkleDistributor.claim()` accepts `(uint256 index, address account, uint256 cumulativeAmount, bytes32[] calldata merkleProof)` and transfers tokens directly to `account` after verifying the merkle proof. There is no check that `msg.sender == account`. [1](#0-0) 

The same pattern exists in `MerkleBlastPointsDistributor.claim()`: [2](#0-1) 

By contrast, `KernelMerkleDistributor._processClaim()` — which backs both `claim()` and `claimAndStake()` in that contract — explicitly enforces self-only claiming: [3](#0-2) 

This inconsistency across the three distributor contracts confirms the missing check in `MerkleDistributor` and `MerkleBlastPointsDistributor` is unintentional.

### Impact Explanation
Any third party can force a claim for any eligible user at any time. Tokens are sent to the correct `account`, so there is no direct theft. However:

- Users lose control over the timing of their token receipt (e.g., vesting strategy, tax-year planning, or protocol interaction sequencing).
- The fee (`feeInBPS`, up to 10% of `MAX_FEE_IN_BPS = 1000`) is deducted from the user's claimable amount and sent to `protocolTreasury` regardless of whether the user initiated the claim.
- Once forced-claimed, `userClaims[account].lastClaimedIndex` and `cumulativeAmount` are updated, preventing the user from re-claiming the same allocation. [4](#0-3) 

**Impact: Low** — Contract fails to deliver promised user autonomy over claim timing, but no funds are lost beyond the intended fee.

### Likelihood Explanation
High. The `claim()` function is public and permissionless. Any actor who can observe the merkle tree (which is public by design) can construct a valid proof for any eligible `account` and call `claim()` on their behalf. No special privileges or conditions are required.

### Recommendation
Add a caller restriction to `MerkleDistributor.claim()` and `MerkleBlastPointsDistributor.claim()`, consistent with `KernelMerkleDistributor`:

```solidity
if (account != msg.sender) {
    revert Unauthorized();
}
```

Alternatively, if permissionless claiming on behalf of others is intentional for these contracts, document the design decision explicitly and confirm that forced-claim timing has no adverse effect on users.

### Proof of Concept
1. Alice is eligible to claim 1000 tokens at `index = 5` in `MerkleDistributor`. She has not yet claimed.
2. Bob (any external address) obtains Alice's merkle proof from the public merkle tree.
3. Bob calls `MerkleDistributor.claim(5, alice, 1000e18, aliceProof)`.
4. The proof verifies. `userClaims[alice]` is updated. `1000e18 * feeInBPS / 10_000` is sent to `protocolTreasury`. The remainder is sent to `alice`.
5. Alice's claim is now marked as consumed at index 5. She cannot re-claim. She received her tokens at a time she did not choose. [5](#0-4)

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

**File:** contracts/utils/MerkleDistributor/MerkleBlastPointsDistributor.sol (L86-131)
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

        // Calculate the claimable amount
        uint256 claimableBlastPoints = cumulativeBlastPointAmount - userClaims[account].cumulativeBlastPointAmount;
        uint256 claimableBlastGold = cumulativeBlastGoldAmount - userClaims[account].cumulativeBlastGoldAmount;

        // Ensure there is something to claim
        if (claimableBlastPoints == 0 && claimableBlastGold == 0) {
            revert NoPointsToClaim();
        }

        // Update user claim info
        userClaims[account].lastClaimedIndex = index;
        userClaims[account].cumulativeBlastPointAmount = cumulativeBlastPointAmount;
        userClaims[account].cumulativeBlastGoldAmount = cumulativeBlastGoldAmount;

        emit Claimed(index, account, claimableBlastPoints, claimableBlastGold);
    }
```

**File:** contracts/KERNEL/KernelMerkleDistributor.sol (L311-313)
```text
        if (account != msg.sender) {
            revert Unauthorized();
        }
```
