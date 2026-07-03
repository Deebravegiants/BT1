### Title
Unauthorized Claim Triggering Causes Forced Fee Extraction from Users - (File: contracts/utils/MerkleDistributor/MerkleDistributor.sol)

### Summary
The `claim` function in `MerkleDistributor.sol` lacks a `msg.sender == account` validation, allowing any external caller to trigger a claim on behalf of any user. This forces the protocol fee deduction on the victim's unclaimed rewards and permanently reduces the user's claimable yield without their consent.

### Finding Description
In `MerkleDistributor.sol`, the public `claim` function accepts an arbitrary `account` parameter but never validates that `msg.sender == account`:

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
    // No msg.sender == account check
    ...
    uint256 fee = (claimableAmount * feeInBPS) / 10_000;
    uint256 amountToSend = claimableAmount - fee;

    IERC20(token).safeTransfer(account, amountToSend);
    IERC20(token).safeTransfer(protocolTreasury, fee);
    ...
}
``` [1](#0-0) 

Any caller who possesses a valid merkle proof for a target user can invoke `claim(index, victimAddress, cumulativeAmount, proof)` on behalf of that user. The function then marks the claim as processed for `account`, deducts a fee (up to `MAX_FEE_IN_BPS = 1000`, i.e. 10%) from the claimable amount, sends the fee to `protocolTreasury`, and sends the remainder to `account`. [2](#0-1) 

By contrast, `KernelMerkleDistributor.sol` explicitly enforces `account == msg.sender`:

```solidity
if (account != msg.sender) {
    revert Unauthorized();
}
``` [3](#0-2) 

This confirms the intended design is for only the account owner to trigger their own claim. `MerkleDistributor.sol` omits this check entirely, creating a directly exploitable discrepancy.

### Impact Explanation
An attacker can force any user's pending rewards to be claimed prematurely, causing the fee to be extracted from the user's unclaimed yield. The user receives less than they would have if they had claimed at a time of their choosing (e.g., after a fee reduction or fee waiver). The fee — up to 10% of the claimable amount — is permanently diverted from the user to `protocolTreasury`. This constitutes **theft of unclaimed yield (High)**.

### Likelihood Explanation
The attack requires only a valid merkle proof for the target user. Merkle proofs are typically published off-chain for users to claim, making them publicly accessible. Any unprivileged external caller can execute this attack against any user at any time, with no capital requirement and no special role.

### Recommendation
Add a caller validation check in `MerkleDistributor.sol`'s `claim` function, consistent with `KernelMerkleDistributor.sol`:

```solidity
if (account != msg.sender) {
    revert Unauthorized();
}
```

### Proof of Concept
1. Alice has unclaimed rewards in a `MerkleDistributor` deployment with `feeInBPS = 1000` (10%).
2. Attacker obtains Alice's merkle proof from the publicly available off-chain distribution data.
3. Attacker calls `claim(index, alice, cumulativeAmount, proof)`.
4. The contract deducts 10% of Alice's claimable amount and sends it to `protocolTreasury`.
5. Alice receives only 90% of her entitled rewards, with no recourse — the claim is now marked as processed at the current `cumulativeAmount`, and the fee cannot be recovered.

### Citations

**File:** contracts/utils/MerkleDistributor/MerkleDistributor.sol (L47-47)
```text
    uint256 public constant MAX_FEE_IN_BPS = 1000;
```

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
