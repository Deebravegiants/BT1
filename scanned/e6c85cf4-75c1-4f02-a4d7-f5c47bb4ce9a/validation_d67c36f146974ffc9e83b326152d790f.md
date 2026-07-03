The critical finding is in `KernelTop100MerkleDistributor.sol`. The `withdrawTokens()` function allows the owner to drain the entire KERNEL token balance — including all tokens allocated to users via the merkle tree — without any restriction or accounting check against user entitlements.

---

### Title
Owner Can Drain All User-Allocated KERNEL Tokens via Unrestricted `withdrawTokens()` - (File: contracts/KERNEL/KernelTop100MerkleDistributor.sol)

### Summary
`KernelTop100MerkleDistributor` holds KERNEL tokens that users are entitled to claim over a 30-day vesting schedule, verified by a merkle root. The `withdrawTokens()` admin function imposes no restriction on the amount withdrawable and performs no accounting check against the total user-allocated balance. The owner can call it to drain the entire KERNEL balance, permanently preventing all users from claiming their vested allocations.

### Finding Description
The contract distributes KERNEL tokens to "Top 100" participants based on off-chain merkle proofs. Users call `claim()` or `claimAndStake()` to receive their vested portion over 30 days. The contract must hold the full allocation of KERNEL tokens to service these claims.

The `withdrawTokens()` function:

```solidity
function withdrawTokens(address _token, uint256 _amount, address _recipient) external onlyOwner {
    UtilLib.checkNonZeroAddress(_token);
    UtilLib.checkNonZeroAddress(_recipient);

    if (_amount == 0) {
        revert ZeroValueProvided();
    }

    IERC20(_token).safeTransfer(_recipient, _amount);

    emit TokensWithdrawn(_token, _amount, _recipient);
}
``` [1](#0-0) 

This function:
- Accepts any `_token` address, including `kernel` itself.
- Accepts any `_amount` up to the full contract balance.
- Has no check against the sum of all user-allocated amounts in the merkle tree.
- Has no check against `userClaims[user].amountClaimed` or any pending vested balance.

The merkle root is set at initialization and is immutable: [2](#0-1) 

Users' total allocations are encoded in that root, but the contract holds no on-chain accounting of the aggregate committed amount. The owner can therefore withdraw the full KERNEL balance at any time.

### Impact Explanation
**High — Theft of unclaimed yield.**

All KERNEL tokens held by the contract are user-allocated yield rewards. The owner can call `withdrawTokens(kernelAddress, kernel.balanceOf(address(this)), ownerAddress)` to transfer the entire balance to themselves. Every user who has not yet claimed their full vested allocation loses those tokens permanently. The vesting schedule becomes meaningless.

### Likelihood Explanation
The attack requires only a single owner transaction with no preconditions. The owner address is a single EOA or multisig with `onlyOwner` access. No external conditions, oracle manipulation, or user interaction is needed. The function is always callable as long as the contract holds a non-zero KERNEL balance.

### Recommendation
Track the total committed (merkle-allocated) amount on-chain and enforce that `withdrawTokens` cannot reduce the KERNEL balance below the sum of all unclaimed allocations. A simpler approach: restrict `withdrawTokens` to tokens other than `kernel`, or remove the function entirely and rely on a time-locked governance process for any emergency recovery.

```solidity
function withdrawTokens(address _token, uint256 _amount, address _recipient) external onlyOwner {
    UtilLib.checkNonZeroAddress(_token);
    UtilLib.checkNonZeroAddress(_recipient);
    if (_amount == 0) revert ZeroValueProvided();
+   require(_token != address(kernel), "Cannot withdraw KERNEL");
    IERC20(_token).safeTransfer(_recipient, _amount);
    emit TokensWithdrawn(_token, _amount, _recipient);
}
```

### Proof of Concept
1. Protocol deploys `KernelTop100MerkleDistributor` with a merkle root committing 1,000,000 KERNEL to 100 users.
2. Contract is funded with 1,000,000 KERNEL tokens.
3. Vesting starts; users begin claiming their allocations.
4. Owner calls `withdrawTokens(address(kernel), 1_000_000e18, ownerEOA)`.
5. The full KERNEL balance is transferred to the owner.
6. All subsequent `claim()` and `claimAndStake()` calls revert due to insufficient balance.
7. All remaining user allocations are permanently lost. [3](#0-2) [1](#0-0)

### Citations

**File:** contracts/KERNEL/KernelTop100MerkleDistributor.sol (L141-143)
```text
    /// @notice The merkle root
    bytes32 public merkleRoot;

```

**File:** contracts/KERNEL/KernelTop100MerkleDistributor.sol (L310-338)
```text
    function claim(uint256 amount, bytes32[] calldata merkleProof) external nonReentrant whenNotPaused {
        address user = msg.sender;

        // Verify merkle proof and update user claim data
        _verifyClaimProof(user, amount, merkleProof);

        // Get claimable amount
        uint256 claimableAmount = _getUnclaimedVestedAmount(user, amount);

        if (claimableAmount == 0) {
            revert NoTokensToClaim();
        }

        // Update user claim data
        userClaims[user].lastClaimTimestamp = block.timestamp;
        userClaims[user].amountClaimed += claimableAmount;

        // Calculate fee
        uint256 fee = (claimableAmount * feeInBPS) / FEE_DENOMINATOR;
        uint256 amountToSend = claimableAmount - fee;

        // Transfer tokens
        if (fee > 0) {
            kernel.safeTransfer(protocolTreasury, fee);
        }
        kernel.safeTransfer(user, amountToSend);

        emit Claimed(user, amountToSend);
    }
```

**File:** contracts/KERNEL/KernelTop100MerkleDistributor.sol (L461-472)
```text
    function withdrawTokens(address _token, uint256 _amount, address _recipient) external onlyOwner {
        UtilLib.checkNonZeroAddress(_token);
        UtilLib.checkNonZeroAddress(_recipient);

        if (_amount == 0) {
            revert ZeroValueProvided();
        }

        IERC20(_token).safeTransfer(_recipient, _amount);

        emit TokensWithdrawn(_token, _amount, _recipient);
    }
```
