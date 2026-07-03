### Title
Missing `msg.sender == account` Caller Authentication in `MerkleDistributor.claim()` Enables Forced Fee Extraction from Any User - (File: contracts/utils/MerkleDistributor/MerkleDistributor.sol)

### Summary
`MerkleDistributor.claim()` accepts an arbitrary `account` parameter but never verifies that `msg.sender == account`. Any unprivileged caller who possesses a valid merkle proof (which is public off-chain data) can trigger a claim on behalf of any user, forcing that user to pay up to 10% in protocol fees without their consent. The sibling contract `KernelMerkleDistributor` explicitly guards against this with `if (account != msg.sender) revert Unauthorized()`, confirming the omission is unintentional.

### Finding Description
`MerkleDistributor.claim()` takes `account` as a caller-supplied parameter and performs no check that `msg.sender == account`:

```solidity
// contracts/utils/MerkleDistributor/MerkleDistributor.sol L97-L147
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
    // ← no msg.sender == account check
    ...
    uint256 fee = (claimableAmount * feeInBPS) / 10_000;   // up to 10%
    uint256 amountToSend = claimableAmount - fee;
    IERC20(token).safeTransfer(account, amountToSend);
    IERC20(token).safeTransfer(protocolTreasury, fee);     // fee extracted
``` [1](#0-0) 

`MAX_FEE_IN_BPS = 1000` (10%) is the ceiling for `feeInBPS`, set at initialization and adjustable by the owner via `setFeeInBPS()`. [2](#0-1) 

By contrast, `KernelMerkleDistributor._processClaim()` explicitly enforces caller identity:

```solidity
// contracts/KERNEL/KernelMerkleDistributor.sol L311-L313
if (account != msg.sender) {
    revert Unauthorized();
}
``` [3](#0-2) 

The inconsistency between the two contracts confirms the missing check in `MerkleDistributor` is a defect, not an intentional design choice.

### Impact Explanation
An attacker who obtains the public merkle proof for any user (proofs are published off-chain as part of the distribution) can call `claim()` on that user's behalf at any time. The tokens are sent to `account` (not the attacker), but the fee — up to 10% of the claimable amount — is irrevocably transferred to `protocolTreasury`. The victim:

1. Loses the fee portion of their yield without consent.
2. Has their `lastClaimedIndex` and `cumulativeAmount` updated, preventing a re-claim until the next merkle root is published.
3. Cannot recover the fee.

If the attacker sweeps all eligible accounts at every root update, every user in every distribution epoch loses up to 10% of their yield. This maps to **High — Theft of unclaimed yield**.

### Likelihood Explanation
- Merkle proofs are public by design (published off-chain for users to self-claim).
- No access control, no rate limiting, and no gas cost barrier prevents mass forced-claiming.
- The attacker needs only to iterate over the published distribution list and submit one transaction per user.
- Likelihood is **High**.

### Recommendation
Add a caller identity check identical to the one already present in `KernelMerkleDistributor`:

```solidity
function claim(...) external override whenNotPaused {
    if (account != msg.sender) revert Unauthorized();
    ...
}
```

Alternatively, if claiming on behalf of others is intentionally supported, remove the fee when `msg.sender != account`, or require explicit on-chain delegation.

### Proof of Concept
1. Protocol publishes merkle root with Alice's leaf: `(index=1, account=Alice, cumulativeAmount=1000e18)` and the corresponding proof `P`.
2. `feeInBPS = 1000` (10%).
3. Attacker calls:
   ```solidity
   merkleDistributor.claim(1, Alice, 1000e18, P);
   ```
4. Contract verifies proof (valid), computes `claimableAmount = 1000e18`, `fee = 100e18`, `amountToSend = 900e18`.
5. `900e18` tokens transferred to Alice; `100e18` tokens transferred to `protocolTreasury`.
6. Alice's `lastClaimedIndex` is set to `1`; she cannot claim again until the next root.
7. Alice loses `100e18` tokens (10%) she never consented to pay as a fee. [4](#0-3)

### Citations

**File:** contracts/utils/MerkleDistributor/MerkleDistributor.sol (L47-51)
```text
    uint256 public constant MAX_FEE_IN_BPS = 1000;

    address public override token;
    address public protocolTreasury;
    uint256 public feeInBPS;
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
