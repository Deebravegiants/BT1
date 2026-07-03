### Title
Missing Caller Authorization in `MerkleDistributor.claim` Allows Anyone to Force Claims on Behalf of Any User - (File: contracts/utils/MerkleDistributor/MerkleDistributor.sol)

### Summary
The `claim` function in `MerkleDistributor.sol` accepts an arbitrary `account` address but never verifies that `msg.sender == account`. Any external caller who possesses a valid merkle proof for a target user can trigger that user's claim, permanently updating their on-chain claim state and transferring tokens to them without their consent. The sibling contract `KernelMerkleDistributor.sol` explicitly guards against this with `if (account != msg.sender) revert Unauthorized()`, confirming the developers recognized the requirement but omitted it here.

### Finding Description
`MerkleDistributor.claim` validates the merkle proof against the supplied `account` address, then unconditionally updates `userClaims[account]` and transfers tokens to `account`:

```solidity
// contracts/utils/MerkleDistributor/MerkleDistributor.sol  lines 97-147
function claim(
    uint256 index,
    address account,          // ← caller-supplied, never checked against msg.sender
    uint256 cumulativeAmount,
    bytes32[] calldata merkleProof
) external override whenNotPaused {
    ...
    bytes32 node = keccak256(abi.encodePacked(index, account, cumulativeAmount));
    if (!MerkleProofUpgradeable.verify(merkleProof, currentMerkleRoot, node))
        revert InvalidMerkleProof();
    ...
    userClaims[account].lastClaimedIndex = index;   // ← state written for account
    userClaims[account].cumulativeAmount = cumulativeAmount;
    ...
    IERC20(token).safeTransfer(account, amountToSend);  // ← tokens sent to account
    IERC20(token).safeTransfer(protocolTreasury, fee);
}
```

Merkle proofs for a given distribution round are derivable from the published merkle tree (they are public data). An attacker therefore needs no privileged information to construct a valid call for any victim address.

The protected sibling contract shows the intended pattern:

```solidity
// contracts/KERNEL/KernelMerkleDistributor.sol  lines 311-313
if (account != msg.sender) {
    revert Unauthorized();
}
```

`MerkleDistributor.sol` omits this guard entirely.

### Impact Explanation
**Low — Contract fails to deliver promised returns, but doesn't lose value.**

1. **Forced claim timing.** A user may deliberately defer claiming (e.g., to batch with other operations, to wait for a fee reduction, or for tax-timing reasons). An attacker can pre-empt this by calling `claim` on their behalf, permanently consuming the current-round allocation at the current `feeInBPS` rate (up to 10 %).
2. **Irreversible state mutation.** Once `userClaims[account].lastClaimedIndex` is advanced, the victim cannot re-claim for that index. The cumulative tracking means they can still claim incremental amounts in future rounds, so funds are not permanently frozen — but the victim loses control over *when* and *how* they receive their allocation.
3. **Fee extraction at attacker-chosen moment.** If the owner later lowers `feeInBPS`, a victim who intended to wait would have received more tokens. The attacker can lock in the higher fee by forcing an early claim.

Tokens are sent to the correct `account`, so there is no direct theft. The harm is loss of user autonomy over claim timing and potential excess fee payment.

### Likelihood Explanation
- The function is `external` with no role restriction.
- Merkle proofs are public (derived from the published tree).
- The attacker needs only the victim's address, the current index, the cumulative amount, and the proof — all observable on-chain or from the distribution API.
- No gas cost barrier prevents mass griefing of all pending claimants in a single block.

### Recommendation
Add the same guard present in `KernelMerkleDistributor.sol`:

```solidity
function claim(
    uint256 index,
    address account,
    uint256 cumulativeAmount,
    bytes32[] calldata merkleProof
) external override whenNotPaused {
+   if (account != msg.sender) revert Unauthorized();
    ...
}
```

Alternatively, remove the `account` parameter and derive it from `msg.sender` directly, as `KernelTop100MerkleDistributor.sol` does (`address user = msg.sender`).

### Proof of Concept
1. The protocol publishes a merkle tree. Alice's leaf is `keccak256(abi.encodePacked(index, alice, cumulativeAmount))`.
2. Bob derives Alice's merkle proof from the published tree (public data).
3. Bob calls `MerkleDistributor.claim(index, alice, cumulativeAmount, aliceProof)`.
4. The proof passes. `userClaims[alice].lastClaimedIndex` is set to `index`. Tokens are transferred to Alice minus the current fee.
5. Alice later tries to call `claim` herself — the call reverts with `AlreadyClaimed`.
6. Alice was forced to claim at Bob's chosen moment, at the current fee rate, with no recourse. [1](#0-0) [2](#0-1) [3](#0-2)

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
