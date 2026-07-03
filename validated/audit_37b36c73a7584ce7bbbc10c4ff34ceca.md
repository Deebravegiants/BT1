### Title
Live `feeInBPS` Applied at Claim Time Silently Reduces User KERNEL Yield When Fee Changes After Merkle Root Publication - (`contracts/KERNEL/KernelMerkleDistributor.sol`)

### Summary
`KernelMerkleDistributor` reads the global `feeInBPS` at the moment a user calls `claim` or `claimAndStake`, rather than caching the fee at the time the merkle root is published. Because the owner can update `feeInBPS` at any time via `setFeeInBPS`, users who claim after a fee increase silently receive fewer KERNEL tokens than the merkle allocation implies, with the difference redirected to the protocol treasury.

### Finding Description
The merkle root commits to each user's `cumulativeAmount` — the total KERNEL they are entitled to. However, the fee deducted from that entitlement is not fixed at root-publication time; it is read live from `feeInBPS` inside `_processClaim`:

```solidity
// L338-339
uint256 fee = (claimableAmount * feeInBPS) / FEE_DENOMINATOR;
uint256 amountToSend = claimableAmount - fee;
``` [1](#0-0) 

The owner can raise `feeInBPS` (up to 10%) at any time with no time-lock or per-epoch guard:

```solidity
function setFeeInBPS(uint256 _feeInBPS) external onlyOwner {
    if (_feeInBPS > MAX_FEE_IN_BPS) { revert InvalidFeeInBPS(); }
    feeInBPS = _feeInBPS;
    emit FeeInBPSUpdated(feeInBPS);
}
``` [2](#0-1) 

There is no mechanism to lock the fee for a given merkle epoch. The merkle proof only verifies `(index, account, cumulativeAmount)` — the fee is entirely outside the commitment: [3](#0-2) 

So users who claim after a fee change receive a materially different amount than what the published allocation implied. The same pattern exists in `KernelTop100MerkleDistributor`, which additionally spans a 30-day vesting window, making mid-vesting fee changes even more impactful. [4](#0-3) 

### Impact Explanation
Users receive fewer KERNEL tokens than their merkle-proven entitlement implies. The shortfall flows directly to `protocolTreasury`. This constitutes **theft of unclaimed yield** — classified as **High** in the allowed impact scope. With `MAX_FEE_IN_BPS = 1000` (10%), up to 10% of every user's allocation can be silently redirected. [5](#0-4) [6](#0-5) 

### Likelihood Explanation
`feeInBPS` is a routine protocol parameter updated by the owner with no time-lock. Merkle distributions are announced off-chain and users claim over days or weeks. Any fee update during that window silently reduces user yield. The `KernelTop100MerkleDistributor` vesting window of 30 days makes the exposure window even longer. [7](#0-6) 

### Recommendation
Cache `feeInBPS` at the time each merkle root is set (e.g., store it alongside `currentMerkleRoot` in a per-epoch struct). Apply only the cached fee to claims against that epoch's root, so users can verify their expected net amount before claiming and are protected from post-publication fee changes.

### Proof of Concept
1. Owner publishes merkle root with `feeInBPS = 0`; off-chain announcement tells users they will receive 100% of their allocation.
2. Owner calls `setFeeInBPS(1000)` (10%) before users claim.
3. User calls `claim(index, account, 1000e18, proof)`.
4. `_processClaim` computes `fee = 1000e18 * 1000 / 10_000 = 100e18` and transfers only `900e18` to the user.
5. User receives 10% fewer tokens than the published allocation promised, with no on-chain protection or warning. [8](#0-7)

### Citations

**File:** contracts/KERNEL/KernelMerkleDistributor.sol (L143-146)
```text
    uint256 public constant FEE_DENOMINATOR = 10_000;

    /// @notice The maximum fee in basis points that can be set by the owner (10%)
    uint256 public constant MAX_FEE_IN_BPS = 1000;
```

**File:** contracts/KERNEL/KernelMerkleDistributor.sol (L292-346)
```text
    function _processClaim(
        uint256 index,
        address account,
        uint256 cumulativeAmount,
        bytes32[] calldata merkleProof
    )
        internal
        returns (uint256)
    {
        UtilLib.checkNonZeroAddress(account);

        if (currentMerkleRoot == bytes32(0)) {
            revert ZeroValueProvided();
        }

        if (index == 0 || index > currentIndex) {
            revert InvalidIndex();
        }

        if (account != msg.sender) {
            revert Unauthorized();
        }

        if (isClaimed(index, account)) {
            revert AlreadyClaimed();
        }

        // Verify the merkle proof
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

        // Update user claim info
        userClaims[account].lastClaimedIndex = index;
        userClaims[account].cumulativeAmount = cumulativeAmount;

        // Calculate the fee and the amount to send
        uint256 fee = (claimableAmount * feeInBPS) / FEE_DENOMINATOR;
        uint256 amountToSend = claimableAmount - fee;

        if (fee > 0) {
            kernel.safeTransfer(protocolTreasury, fee);
        }

        return amountToSend;
    }
```

**File:** contracts/KERNEL/KernelMerkleDistributor.sol (L388-396)
```text
    function setFeeInBPS(uint256 _feeInBPS) external onlyOwner {
        if (_feeInBPS > MAX_FEE_IN_BPS) {
            revert InvalidFeeInBPS();
        }

        feeInBPS = _feeInBPS;

        emit FeeInBPSUpdated(feeInBPS);
    }
```

**File:** contracts/KERNEL/KernelTop100MerkleDistributor.sol (L120-136)
```text
    /// @notice The fee denominator constant used to calculate the fee
    uint256 public constant FEE_DENOMINATOR = 10_000;

    /// @notice The maximum fee in basis points that can be set by the owner (10%)
    uint256 public constant MAX_FEE_IN_BPS = 1000;

    /// @notice The vesting duration in seconds (30 days)
    uint256 public constant VESTING_DURATION = 30 days;

    /// @notice The KERNEL token distributed by this contract
    IERC20 public kernel;

    /// @notice The address of the protocol treasury
    address public protocolTreasury;

    /// @notice The fee in basis points
    uint256 public feeInBPS;
```
