### Title
Unrestricted `claim()` Caller Allows Forced Fee Extraction Against Any Account - (File: contracts/utils/MerkleDistributor/MerkleDistributor.sol)

---

### Summary
`MerkleDistributor.claim()` contains no `msg.sender == account` guard, so any external caller can force a token claim on behalf of any eligible account. Because a protocol fee is deducted at claim time, an attacker can trigger a claim for a victim precisely when the fee is highest — including front-running a pending fee reduction — permanently destroying a portion of the victim's unclaimed yield.

---

### Finding Description

In `contracts/utils/MerkleDistributor/MerkleDistributor.sol`, the public `claim` function accepts an arbitrary `account` address and transfers tokens to it after deducting `feeInBPS`. There is no check that `msg.sender == account`:

```solidity
// L97-L147 — no caller restriction
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
    // ...merkle proof verified against `account`...
    uint256 fee = (claimableAmount * feeInBPS) / 10_000;
    uint256 amountToSend = claimableAmount - fee;
    IERC20(token).safeTransfer(account, amountToSend);       // tokens to victim
    IERC20(token).safeTransfer(protocolTreasury, fee);       // fee to treasury
}
```

The sibling contract `KernelMerkleDistributor._processClaim()` explicitly closes this gap:

```solidity
// KernelMerkleDistributor.sol L311-L313
if (account != msg.sender) {
    revert Unauthorized();
}
```

`MerkleDistributor` has no equivalent guard, making it callable by any third party for any eligible `account`.

---

### Impact Explanation

**High — Theft of unclaimed yield.**

When `feeInBPS > 0`, any caller can force a claim for a victim and cause the fee to be permanently extracted from the victim's allocation. The victim receives `claimableAmount - fee` instead of the full `claimableAmount` they would have received had they claimed after a fee reduction. The lost tokens flow to `protocolTreasury` and are irrecoverable by the victim. The attacker's cost is only gas; the victim's loss scales with both their allocation size and the current fee rate (up to `MAX_FEE_IN_BPS = 1000`, i.e. 10%).

---

### Likelihood Explanation

**Medium.** All merkle-eligible accounts and their proofs are public (off-chain distribution data). Any attacker can:

1. Enumerate eligible accounts from the published merkle tree.
2. Watch the mempool for a `setFeeInBPS` transaction that lowers the fee.
3. Front-run it by calling `claim(index, victim, cumulativeAmount, proof)` at the current higher fee rate.

Even without a pending fee reduction, an attacker can force claims at the current fee rate at any time, denying victims the ability to time their own claims (e.g., waiting for a fee-free window). No special role or capital is required beyond gas.

---

### Recommendation

Add a caller restriction identical to `KernelMerkleDistributor`:

```solidity
function claim(...) external override whenNotPaused {
    if (account != msg.sender) revert Unauthorized();
    // ...
}
```

Alternatively, if third-party claiming is intentional (e.g., for gas relayers), introduce an explicit allowlist or a per-account opt-in delegation mechanism.

---

### Proof of Concept

1. Protocol deploys `MerkleDistributor` with `feeInBPS = 500` (5%).
2. Alice has a valid merkle proof entitling her to 1,000 tokens; she intends to wait for a fee reduction.
3. Admin submits `setFeeInBPS(0)` to the mempool.
4. Attacker sees the pending transaction and front-runs it by calling:
   ```solidity
   merkleDistributor.claim(aliceIndex, alice, 1000e18, aliceProof);
   ```
5. Alice's claim executes at 5% fee: she receives 950 tokens; 50 tokens go to `protocolTreasury`.
6. Admin's `setFeeInBPS(0)` lands — but Alice's claim is already marked as processed (`userClaims[alice].lastClaimedIndex >= index`), so she cannot re-claim.
7. Alice permanently loses 50 tokens she would have received under the zero-fee regime. [1](#0-0) [2](#0-1) [3](#0-2)

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
