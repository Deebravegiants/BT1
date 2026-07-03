### Title
Lack of Caller Validation in `MerkleDistributor.claim()` Allows Anyone to Force Fee-Deducting Claims on Behalf of Any User - (File: contracts/utils/MerkleDistributor/MerkleDistributor.sol)

### Summary
`MerkleDistributor.claim()` accepts an arbitrary `account` parameter but never validates that `msg.sender == account`. Any unprivileged caller can trigger a claim on behalf of any user, forcing the protocol to deduct a fee from the user's allocation and send it to the treasury — without the user's consent. The user permanently loses the fee portion of their unclaimed tokens.

### Finding Description
`MerkleDistributor.claim()` takes `account` as a caller-supplied parameter and transfers tokens directly to that address after deducting a fee. There is no check that `msg.sender` equals `account`.

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
    // ... merkle proof validation ...
    uint256 fee = (claimableAmount * feeInBPS) / 10_000;
    uint256 amountToSend = claimableAmount - fee;

    IERC20(token).safeTransfer(account, amountToSend);
    IERC20(token).safeTransfer(protocolTreasury, fee);
``` [1](#0-0) 

The sibling contract `KernelMerkleDistributor` explicitly guards against this exact pattern in its shared `_processClaim()` helper:

```solidity
if (account != msg.sender) {
    revert Unauthorized();
}
``` [2](#0-1) 

`MerkleDistributor` has no equivalent guard. The fee ceiling is `MAX_FEE_IN_BPS = 1000` (10%). [3](#0-2) 

### Impact Explanation
An attacker calls `claim(index, victim, cumulativeAmount, proof)` with a valid merkle proof for the victim. The contract:
1. Marks the victim's claim as consumed (`userClaims[victim].lastClaimedIndex = index`).
2. Deducts `feeInBPS / 10_000` of the claimable amount and sends it to `protocolTreasury`.
3. Sends the remainder to `victim`.

The victim permanently loses the fee portion of their tokens — up to 10% of their allocation — without ever consenting to the claim. They cannot reclaim the fee. This constitutes **theft of unclaimed yield** (High severity).

### Likelihood Explanation
The function is public, requires no special role, and the only input needed is a valid merkle proof for the target account — which is fully public on-chain or derivable from the merkle tree data published off-chain. Any unprivileged external caller can execute this attack against any eligible user at any time while the contract is unpaused.

### Recommendation
Add a caller-identity check identical to the one already present in `KernelMerkleDistributor._processClaim()`:

```solidity
if (account != msg.sender) {
    revert Unauthorized();
}
```

This should be inserted in `MerkleDistributor.claim()` before the merkle proof verification, mirroring the pattern at `KernelMerkleDistributor.sol` lines 311–313.

### Proof of Concept
1. Alice has an unclaimed allocation of 1000 tokens in the merkle tree. `feeInBPS = 500` (5%).
2. Bob (attacker) obtains Alice's merkle proof from the published tree data.
3. Bob calls `MerkleDistributor.claim(index, alice, 1000, aliceProof)`.
4. The contract transfers 950 tokens to Alice and 50 tokens to `protocolTreasury`.
5. Alice's claim is marked consumed. She can never reclaim the 50 tokens.
6. Bob spent only gas; Alice lost 50 tokens without consent. [4](#0-3) [5](#0-4)

### Citations

**File:** contracts/utils/MerkleDistributor/MerkleDistributor.sol (L47-47)
```text
    uint256 public constant MAX_FEE_IN_BPS = 1000;
```

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

**File:** contracts/KERNEL/KernelMerkleDistributor.sol (L292-313)
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
```
