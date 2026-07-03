### Title
Permissionless `claim` Enables Forced Fee Extraction from Any Reward Claimant - (File: contracts/utils/MerkleDistributor/MerkleDistributor.sol)

### Summary
`MerkleDistributor.claim` accepts an arbitrary `account` parameter with no `msg.sender` restriction. Any external caller who possesses a valid Merkle proof (all proofs are published off-chain by the protocol) can trigger a claim on behalf of any user. When `feeInBPS > 0`, this forces the victim to immediately pay the protocol fee, permanently reducing their claimable yield without their consent.

### Finding Description
The `claim` function in `MerkleDistributor` takes `account` as a caller-supplied parameter and performs no check that `account == msg.sender`:

```solidity
function claim(
    uint256 index,
    address account,          // ← attacker-controlled
    uint256 cumulativeAmount,
    bytes32[] calldata merkleProof
)
    external
    override
    whenNotPaused
{
    // No account == msg.sender guard
    ...
    uint256 fee = (claimableAmount * feeInBPS) / 10_000;
    uint256 amountToSend = claimableAmount - fee;

    IERC20(token).safeTransfer(account, amountToSend);       // victim gets reduced amount
    IERC20(token).safeTransfer(protocolTreasury, fee);       // fee extracted immediately
``` [1](#0-0) 

By contrast, `KernelMerkleDistributor._processClaim` explicitly enforces `account != msg.sender` revert, showing the protocol is aware this guard is necessary in analogous contracts: [2](#0-1) 

The Merkle proof for any `(index, account, cumulativeAmount)` tuple is public — it is distributed by the protocol's off-chain service so users can self-claim. An attacker can replay any published proof against `MerkleDistributor.claim` at will.

### Impact Explanation
**High — Theft of unclaimed yield.**

When `feeInBPS > 0` (up to `MAX_FEE_IN_BPS = 1000`, i.e. 10%), an attacker forces a claim for a victim, permanently extracting the fee from the victim's entitlement. The victim receives `claimableAmount - fee` instead of the full `claimableAmount` they would have received had they chosen their own claim timing (e.g., after the owner reduces the fee to 0). The fee is irrecoverably transferred to `protocolTreasury`; the victim cannot reclaim it. [3](#0-2) 

### Likelihood Explanation
**Medium.** All inputs required to execute the attack — `index`, `account`, `cumulativeAmount`, and `merkleProof` — are published by the protocol's off-chain distribution service and are visible on-chain once any legitimate user submits a transaction. No privileged access, key compromise, or brute force is required. The attacker only needs to monitor the mempool or the protocol's claim API and replay the data before the victim claims.

### Recommendation
Add an `account == msg.sender` guard to `MerkleDistributor.claim`, mirroring the pattern already used in `KernelMerkleDistributor._processClaim`:

```solidity
if (account != msg.sender) revert Unauthorized();
``` [4](#0-3) 

### Proof of Concept
1. Protocol publishes Merkle tree. Alice's leaf: `(index=3, account=Alice, cumulativeAmount=1000e18)`. Proof is public.
2. Owner sets `feeInBPS = 500` (5%).
3. Alice intends to wait until the owner reduces the fee to 0 before claiming.
4. Attacker calls `MerkleDistributor.claim(3, Alice, 1000e18, aliceProof)`.
5. Contract verifies the proof (valid), computes `fee = 50e18`, transfers `950e18` to Alice and `50e18` to `protocolTreasury`.
6. Alice's `userClaims[Alice].cumulativeAmount` is now `1000e18`; she can never reclaim the 50e18 fee.
7. Net loss to Alice: 50e18 tokens (5% of her full entitlement), stolen without her consent. [5](#0-4)

### Citations

**File:** contracts/utils/MerkleDistributor/MerkleDistributor.sol (L96-147)
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
    }
```

**File:** contracts/KERNEL/KernelMerkleDistributor.sol (L311-313)
```text
        if (account != msg.sender) {
            revert Unauthorized();
        }
```
