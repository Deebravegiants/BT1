### Title
Unauthorized Forced Claim Causes Fee Theft from Any User in `MerkleDistributor.claim` - (File: contracts/utils/MerkleDistributor/MerkleDistributor.sol)

### Summary

`MerkleDistributor.claim` accepts an arbitrary `account` parameter with no check that `msg.sender == account`. Any caller who possesses a valid merkle proof for a victim can force-claim on the victim's behalf, triggering the fee deduction at the current `feeInBPS` rate and sending the fee to `protocolTreasury` — permanently reducing the victim's claimable yield. The sister contract `KernelMerkleDistributor` explicitly guards against this with `if (account != msg.sender) { revert Unauthorized(); }`, confirming the protocol team recognizes the requirement but omitted it from the generic distributor.

### Finding Description

`MerkleDistributor.claim` at line 97 takes `account` as a caller-supplied parameter and performs no authorization check:

```solidity
function claim(
    uint256 index,
    address account,          // ← any caller can supply any address
    uint256 cumulativeAmount,
    bytes32[] calldata merkleProof
) external override whenNotPaused {
    // ...no msg.sender == account check...
    uint256 fee = (claimableAmount * feeInBPS) / 10_000;
    uint256 amountToSend = claimableAmount - fee;
    IERC20(token).safeTransfer(account, amountToSend);       // tokens go to victim
    IERC20(token).safeTransfer(protocolTreasury, fee);       // fee permanently lost
}
``` [1](#0-0) 

Merkle proofs are public data (published off-chain for users to self-claim). An attacker reads the proof for any victim, calls `claim` with the victim's `account`, and the fee is deducted at whatever `feeInBPS` is set at that moment. The victim receives `claimableAmount - fee` instead of the full `claimableAmount` they would have received had they waited for the fee to be lowered or zeroed.

`feeInBPS` is mutable up to `MAX_FEE_IN_BPS = 1000` (10%): [2](#0-1) 

By contrast, `KernelMerkleDistributor._processClaim` explicitly blocks this:

```solidity
if (account != msg.sender) {
    revert Unauthorized();
}
``` [3](#0-2) 

### Impact Explanation

Any user's unclaimed token allocation can be force-claimed by an attacker at any time, permanently diverting up to 10% of the claimable amount to `protocolTreasury`. Users who deliberately defer claiming (e.g., waiting for the owner to reduce `feeInBPS` to zero) are robbed of that yield. This is direct, irreversible theft of unclaimed yield — **High** severity per the allowed impact scope.

### Likelihood Explanation

Merkle proofs are public. The attacker needs only: (1) the victim's `index`, `account`, and `cumulativeAmount` from the published merkle tree, and (2) the corresponding proof. No privileged access is required. The attack is trivially scriptable and can be applied to every eligible account in the tree simultaneously.

### Recommendation

Add the same guard present in `KernelMerkleDistributor`:

```solidity
if (account != msg.sender) {
    revert Unauthorized();
}
```

at the top of `MerkleDistributor.claim`, or alternatively accept only `msg.sender` as the recipient and remove the `account` parameter entirely.

### Proof of Concept

1. Owner publishes merkle root; `feeInBPS = 500` (5%).
2. Victim holds a valid leaf `(index=1, account=victim, cumulativeAmount=1000e18)` and is waiting for the owner to call `setFeeInBPS(0)`.
3. Attacker reads the published proof and calls:
   ```solidity
   merkleDistributor.claim(1, victim, 1000e18, victimProof);
   ```
4. Contract executes: `fee = 50e18`, `amountToSend = 950e18`.
5. Victim receives `950e18` tokens; `50e18` tokens are permanently sent to `protocolTreasury`.
6. `userClaims[victim].lastClaimedIndex = 1` — the victim can never re-claim; the 50 tokens are gone.

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
