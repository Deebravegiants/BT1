### Title
Missing `msg.sender == account` Authorization in `MerkleDistributor.claim()` Allows Forced Claims with Involuntary Fee Deduction - (File: `contracts/utils/MerkleDistributor/MerkleDistributor.sol`)

---

### Summary

`MerkleDistributor.claim()` accepts an arbitrary `account` parameter but never verifies that `msg.sender == account`. Any external caller can trigger a valid claim on behalf of any account, forcing an immediate fee deduction from the victim's claimable yield. The analogous root cause from the reference report is a cryptographic commitment not being tied to the committer's identity — here, the claim action is not tied to the claimer's identity.

---

### Finding Description

In `contracts/utils/MerkleDistributor/MerkleDistributor.sol`, the `claim` function accepts `account` as a caller-supplied parameter and verifies the Merkle proof against `(index, account, cumulativeAmount)`. However, there is no check that `msg.sender == account`. The function then transfers tokens to `account` after deducting a protocol fee (up to 10%, controlled by the owner via `feeInBPS`).

```solidity
function claim(
    uint256 index,
    address account,       // ← caller-supplied, never verified against msg.sender
    uint256 cumulativeAmount,
    bytes32[] calldata merkleProof
) external override whenNotPaused {
    ...
    bytes32 node = keccak256(abi.encodePacked(index, account, cumulativeAmount));
    if (!MerkleProofUpgradeable.verify(merkleProof, currentMerkleRoot, node)) {
        revert InvalidMerkleProof();
    }
    ...
    uint256 fee = (claimableAmount * feeInBPS) / 10_000;
    uint256 amountToSend = claimableAmount - fee;

    IERC20(token).safeTransfer(account, amountToSend);       // tokens go to victim
    IERC20(token).safeTransfer(protocolTreasury, fee);       // fee extracted
}
``` [1](#0-0) 

By contrast, `KernelMerkleDistributor._processClaim()` correctly enforces `account != msg.sender → revert Unauthorized()`: [2](#0-1) 

`MerkleDistributor` has no equivalent guard.

---

### Impact Explanation

When `feeInBPS > 0` (up to 1000 BPS = 10%), an attacker who forces a claim on behalf of a victim causes the victim to permanently lose the fee portion of their claimable tokens. The victim receives `claimableAmount * (1 - feeInBPS/10000)` instead of the full `claimableAmount` they would have received had they waited for a fee reduction or elimination. The fee is irrecoverably sent to `protocolTreasury`. This constitutes **theft of unclaimed yield** — the victim's entitled distribution is permanently reduced without their consent. [3](#0-2) 

---

### Likelihood Explanation

- Merkle proofs and claim parameters are either emitted in events or derivable from off-chain distribution data, making them publicly observable.
- Any unprivileged external account can call `claim()` with a victim's valid parameters.
- The fee is configurable up to 10% (`MAX_FEE_IN_BPS = 1000`). When non-zero, every forced claim extracts yield from the victim.
- No special role, key, or oracle access is required. [4](#0-3) 

---

### Recommendation

Add a caller authorization check identical to the one in `KernelMerkleDistributor`:

```solidity
if (account != msg.sender) {
    revert Unauthorized();
}
```

Insert this check at the top of `claim()`, before the Merkle proof verification, mirroring the pattern already established in `KernelMerkleDistributor._processClaim()`. [2](#0-1) 

---

### Proof of Concept

1. Owner sets `feeInBPS = 1000` (10%) and publishes a new Merkle root.
2. Victim (`0xVICTIM`) has a valid leaf `(index=1, account=0xVICTIM, cumulativeAmount=1000e18)` and is waiting for the fee to be reduced before claiming.
3. Attacker observes the Merkle proof from off-chain distribution data or on-chain events.
4. Attacker calls:
   ```solidity
   merkleDistributor.claim(1, 0xVICTIM, 1000e18, victimProof);
   ```
5. Contract verifies the proof (valid), computes `fee = 100e18`, transfers `900e18` to `0xVICTIM` and `100e18` to `protocolTreasury`.
6. `userClaims[0xVICTIM].lastClaimedIndex` is updated; the victim can never reclaim the 100e18 fee that was extracted without their consent. [5](#0-4)

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
