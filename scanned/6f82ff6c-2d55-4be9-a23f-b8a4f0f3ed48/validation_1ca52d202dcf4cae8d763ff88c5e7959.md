### Title
`MerkleDistributor::claim` unconditionally transfers zero-fee to `protocolTreasury`, permanently freezing unclaimed yield for tokens that revert on zero-value transfers — (File: `contracts/utils/MerkleDistributor/MerkleDistributor.sol`)

### Summary
`MerkleDistributor::claim` always calls `IERC20(token).safeTransfer(protocolTreasury, fee)` regardless of whether `fee` is zero. When `feeInBPS` is set to `0`, this results in an unconditional zero-value ERC20 transfer. For tokens that revert on zero-value transfers, every `claim` call reverts, permanently freezing all users' unclaimed yield in the contract.

### Finding Description
In `contracts/utils/MerkleDistributor/MerkleDistributor.sol`, the `claim` function computes a fee and then unconditionally transfers it to `protocolTreasury`:

```solidity
uint256 fee = (claimableAmount * feeInBPS) / 10_000;
uint256 amountToSend = claimableAmount - fee;

IERC20(token).safeTransfer(account, amountToSend);

// Send the fee to the protocol treasury
IERC20(token).safeTransfer(protocolTreasury, fee);  // ← always called, even when fee == 0
``` [1](#0-0) 

When `feeInBPS == 0`, `fee` evaluates to `0`, and `safeTransfer(protocolTreasury, 0)` is called unconditionally. Several ERC20 tokens (e.g., LIDO stETH, BNB, and others) revert on zero-value transfers. Since `MerkleDistributor` is a generic distributor that accepts any token (the token address can even be set post-initialization), this is a realistic deployment scenario. [2](#0-1) 

The sibling contracts `KernelMerkleDistributor` and `KernelTop100MerkleDistributor` correctly guard the fee transfer:

```solidity
if (fee > 0) {
    kernel.safeTransfer(protocolTreasury, fee);
}
``` [3](#0-2) 

`MerkleDistributor` lacks this guard entirely.

### Impact Explanation
When `feeInBPS` is `0` and the distributed token reverts on zero-value transfers, every call to `claim` reverts after the user's claim state has already been updated (lines 134–135). The user's `lastClaimedIndex` and `cumulativeAmount` are written before the transfer, so the claim is marked as consumed but no tokens are ever sent. All users' unclaimed yield is permanently frozen in the contract with no recovery path.

**Impact: Medium — Permanent freezing of unclaimed yield.** [4](#0-3) 

### Likelihood Explanation
- `feeInBPS` is initialized to `0` if the deployer passes `0` (no lower-bound check), and can be set to `0` at any time via `setFeeInBPS`.
- The contract is explicitly designed as a generic distributor for any ERC20 token.
- A non-trivial set of production ERC20 tokens revert on zero-value transfers.
- No privileged action is required from an attacker; any user calling `claim` triggers the revert.

### Recommendation
Add a zero-check guard before the fee transfer, matching the pattern already used in `KernelMerkleDistributor` and `KernelTop100MerkleDistributor`:

```solidity
if (fee > 0) {
    IERC20(token).safeTransfer(protocolTreasury, fee);
}
``` [5](#0-4) 

### Proof of Concept
1. Deploy `MerkleDistributor` with a token that reverts on zero-value transfers (e.g., a standard stETH-like token) and `feeInBPS = 0`.
2. Owner calls `setMerkleRoot(root)` with a valid merkle root containing user allocations.
3. User calls `claim(index, account, cumulativeAmount, merkleProof)` with a valid proof.
4. Execution reaches line 138: `fee = (claimableAmount * 0) / 10_000 = 0`.
5. Line 141: `safeTransfer(account, claimableAmount)` succeeds.
6. Line 144: `safeTransfer(protocolTreasury, 0)` reverts because the token disallows zero-value transfers.
7. The entire transaction reverts. The user's claim state was not yet committed (state update is at lines 134–135, before the transfers), so the user can retry — but every retry will hit the same revert. The yield is permanently unclaimable. [4](#0-3)

### Citations

**File:** contracts/utils/MerkleDistributor/MerkleDistributor.sol (L71-87)
```text
    function initialize(address token_, address _protocolTreasury, uint256 _feeInBPS) external initializer {
        // token can be set later but not the protocol treasury
        if (_protocolTreasury == address(0)) {
            revert ZeroValueProvided();
        }

        if (_feeInBPS > MAX_FEE_IN_BPS) {
            revert InvalidFeeInBPS();
        }

        __Ownable_init();
        __Pausable_init();

        token = token_;
        protocolTreasury = _protocolTreasury;
        feeInBPS = _feeInBPS;
    }
```

**File:** contracts/utils/MerkleDistributor/MerkleDistributor.sol (L133-146)
```text
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
```

**File:** contracts/KERNEL/KernelMerkleDistributor.sol (L341-343)
```text
        if (fee > 0) {
            kernel.safeTransfer(protocolTreasury, fee);
        }
```
