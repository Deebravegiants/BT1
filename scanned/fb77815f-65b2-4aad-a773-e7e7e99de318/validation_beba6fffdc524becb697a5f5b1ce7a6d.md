### Title
Unauthorized Force-Claim Enables Fee Theft from Any Merkle Claimant - (File: contracts/utils/MerkleDistributor/MerkleDistributor.sol)

### Summary
`MerkleDistributor.claim()` accepts an arbitrary `account` parameter with no check that `msg.sender == account`. Any external caller who possesses a valid merkle proof (which is public off-chain data) can force-trigger a claim on behalf of any eligible address. Because the contract deducts a protocol fee (up to 10%) before transferring tokens to `account`, the victim permanently loses a portion of their unclaimed yield without ever consenting to claim.

### Finding Description
`MerkleDistributor.claim()` is a public, permissionless function that accepts `(index, account, cumulativeAmount, merkleProof)`. It verifies the proof against `currentMerkleRoot`, deducts `feeInBPS` from `claimableAmount`, sends the remainder to `account`, and sends the fee to `protocolTreasury`. [1](#0-0) 

There is no `require(msg.sender == account)` guard anywhere in the function or in the internal path it calls. The sibling contract `KernelMerkleDistributor` explicitly added this guard in `_processClaim`: [2](#0-1) 

`MerkleDistributor` never received the same fix. The fee ceiling is 10% (`MAX_FEE_IN_BPS = 1000`): [3](#0-2) 

The fee is computed and transferred unconditionally on every claim: [4](#0-3) 

### Impact Explanation
An attacker who reads the public merkle tree data can enumerate every eligible claimant and their proofs, then call `claim()` for each one before the legitimate users do. Each forced claim deducts up to 10% of the claimant's allocation as a fee and marks the index as claimed, permanently preventing the user from ever claiming without the fee deduction. This constitutes **theft of unclaimed yield** for every participant in the distribution.

**Impact: High** — Theft of unclaimed yield (up to 10% of every eligible user's token allocation).

### Likelihood Explanation
Merkle distribution trees are published off-chain (typically via IPFS or a public API) so that users can construct their own proofs. Any attacker can read this data, enumerate all `(index, account, cumulativeAmount, proof)` tuples, and submit forced claims in a single script or bot. No privileged access, no governance capture, and no oracle manipulation is required. The only cost is gas.

**Likelihood: Medium** — Requires no special access; only public merkle tree data and gas.

### Recommendation
Add a caller-identity check at the top of `claim()`, mirroring the fix already present in `KernelMerkleDistributor._processClaim()`:

```solidity
if (account != msg.sender) {
    revert Unauthorized();
}
```

Alternatively, remove the `account` parameter entirely and derive it from `msg.sender`, as `KernelTop100MerkleDistributor` does. [2](#0-1) 

### Proof of Concept

1. Protocol deploys `MerkleDistributor` with `feeInBPS = 500` (5%) and publishes the merkle tree.
2. Alice is a valid claimant: `index=1, account=alice, cumulativeAmount=1000e18`.
3. Attacker reads the public tree, obtains Alice's proof, and calls:
   ```solidity
   merkleDistributor.claim(1, alice, 1000e18, aliceProof);
   ```
4. The contract executes without reverting — no `msg.sender` check exists.
5. `claimableAmount = 1000e18`, `fee = 50e18`, `amountToSend = 950e18`.
6. Alice receives `950e18` tokens; `50e18` tokens go to `protocolTreasury`.
7. `userClaims[alice].lastClaimedIndex = 1` — Alice's slot is permanently consumed.
8. Alice can never reclaim the 50 tokens she lost to the forced fee.
9. Attacker repeats for every address in the merkle tree, draining unclaimed yield from all participants. [5](#0-4)

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
