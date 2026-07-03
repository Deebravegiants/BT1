### Title
Single-Owner Pause/Unpause with No Role Separation Enables Permanent Freezing of Unclaimed KERNEL Yield — (File: contracts/KERNEL/KernelMerkleDistributor.sol)

### Summary
`KernelMerkleDistributor`, `KernelTop100MerkleDistributor`, and `MerkleDistributor` gate both `pause()` and `unpause()` behind `onlyOwner` with no role separation. The `claim()` and `claimAndStake()` functions are blocked by `whenNotPaused`. If the owner renounces ownership while the contract is paused — a callable, non-malicious operational action — users' unclaimed KERNEL yield is permanently frozen with no recovery path.

### Finding Description
The pool contracts in this codebase correctly separate pause authority from unpause authority:

- `RSETHPoolV3`: `pause()` → `onlyRole(PAUSER_ROLE)`, `unpause()` → `onlyRole(DEFAULT_ADMIN_ROLE)`

But the distributor contracts collapse both into a single `onlyOwner` check:

```solidity
// contracts/KERNEL/KernelMerkleDistributor.sol
function pause() external onlyOwner { _pause(); }
function unpause() external onlyOwner { _unpause(); }
```

`OwnableUpgradeable` exposes a public `renounceOwnership()` function. If the owner calls `renounceOwnership()` while the contract is paused (e.g., as part of a planned decentralization step, or by mistake), `owner()` becomes `address(0)`. Since `unpause()` requires `onlyOwner`, it can never be called again. The contract is permanently paused.

The user-facing functions blocked by `whenNotPaused` are:

```solidity
function claim(...) external override nonReentrant whenNotPaused { ... }
function claimAndStake(...) external nonReentrant whenNotPaused { ... }
```

All KERNEL tokens held in the contract for distribution become permanently inaccessible to users.

### Impact Explanation
**Medium — Permanent freezing of unclaimed yield.**

All KERNEL tokens allocated to users via the merkle distribution are locked in the contract forever. Users who have not yet claimed their entitled KERNEL rewards lose access to them permanently. The `claim()` and `claimAndStake()` paths are the only withdrawal routes for users, and both are blocked by `whenNotPaused`.

### Likelihood Explanation
Low-to-medium. `renounceOwnership()` is a standard, intentionally callable function on `OwnableUpgradeable`. Protocol teams routinely call it as part of decentralization. The risk is that this is done while the contract happens to be paused (e.g., paused for a merkle root update, a routine maintenance window, or an emergency). There is no on-chain guard preventing this sequence.

### Recommendation
1. Replace `OwnableUpgradeable` with `AccessControlUpgradeable` in `KernelMerkleDistributor`, `KernelTop100MerkleDistributor`, and `MerkleDistributor`.
2. Assign `pause()` to a dedicated `PAUSER_ROLE` and `unpause()` to `DEFAULT_ADMIN_ROLE`, matching the pattern already used in the pool contracts.
3. Override `renounceOwnership()` to revert, or remove it entirely, to prevent accidental permanent lockout.

### Proof of Concept

1. Owner calls `pause()` on `KernelMerkleDistributor` (e.g., during a merkle root rotation).
2. Owner calls `renounceOwnership()` (standard decentralization step).
3. `owner()` is now `address(0)`.
4. Any call to `unpause()` reverts with `"Ownable: caller is not the owner"`.
5. Any user calling `claim(index, account, cumulativeAmount, merkleProof)` reverts with `"Pausable: paused"`.
6. All KERNEL tokens in the contract are permanently inaccessible.

**Affected files and lines:** [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5)

### Citations

**File:** contracts/KERNEL/KernelMerkleDistributor.sol (L250-285)
```text
    function claim(
        uint256 index,
        address account,
        uint256 cumulativeAmount,
        bytes32[] calldata merkleProof
    )
        external
        override
        nonReentrant
        whenNotPaused
    {
        uint256 amountToSend = _processClaim(index, account, cumulativeAmount, merkleProof);

        kernel.safeTransfer(account, amountToSend);

        emit Claimed(index, account, amountToSend);
    }

    /// @notice Claims the given amount of the tokens for a given address and automatically stakes them in the
    /// KernelDepositPool contract as part of the same transaction
    function claimAndStake(
        uint256 index,
        address account,
        uint256 cumulativeAmount,
        bytes32[] calldata merkleProof
    )
        external
        nonReentrant
        whenNotPaused
    {
        uint256 amountToStake = _processClaim(index, account, cumulativeAmount, merkleProof);

        IKernelDepositPool(kernelDepositPool).stakeFor(account, amountToStake);

        emit ClaimedAndStaked(index, account, amountToStake);
    }
```

**File:** contracts/KERNEL/KernelMerkleDistributor.sol (L415-423)
```text
    /// @dev Pauses the contract
    function pause() external onlyOwner {
        _pause();
    }

    /// @dev Unpauses the contract
    function unpause() external onlyOwner {
        _unpause();
    }
```

**File:** contracts/KERNEL/KernelTop100MerkleDistributor.sol (L310-345)
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

    /**
     * @notice Claims tokens and stakes them in the KernelDepositPool contract
     * @param amount The amount eligible to be claimed
     * @param merkleProof The merkle proof to verify
     */
    function claimAndStake(uint256 amount, bytes32[] calldata merkleProof) external nonReentrant whenNotPaused {
```

**File:** contracts/KERNEL/KernelTop100MerkleDistributor.sol (L474-482)
```text
    /// @notice Pauses the contract
    function pause() external onlyOwner {
        _pause();
    }

    /// @notice Unpauses the contract
    function unpause() external onlyOwner {
        _unpause();
    }
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

**File:** contracts/utils/MerkleDistributor/MerkleDistributor.sol (L208-216)
```text
    /// @dev Pause the contract
    function pause() external onlyOwner {
        _pause();
    }

    /// @dev Unpause the contract
    function unpause() external onlyOwner {
        _unpause();
    }
```
