### Title
No Recovery Mechanism for Unclaimed KERNEL Tokens - (File: contracts/KERNEL/KernelMerkleDistributor.sol)

### Summary
`KernelMerkleDistributor` holds KERNEL tokens for distribution to users via merkle proofs, but provides no function for the owner to recover unclaimed tokens. Any KERNEL tokens not claimed by users will be permanently locked in the contract.

### Finding Description
`KernelMerkleDistributor` is funded with KERNEL tokens and allows eligible users to call `claim()` or `claimAndStake()` to receive their allocation. The contract's admin functions are limited to `setKernelDepositPool`, `setProtocolTreasury`, `setFeeInBPS`, `setMerkleRoot`, `pause`, and `unpause`. [1](#0-0) 

There is no `withdrawTokens`, `recoverTokens`, or equivalent function that would allow the owner to retrieve the `kernel` token balance. By contrast, the sibling contract `KernelTop100MerkleDistributor` explicitly includes a `withdrawTokens` function that accepts any token address including `kernel`: [2](#0-1) 

`KernelMerkleDistributor` has no such function.

### Impact Explanation
**Medium — Permanent freezing of unclaimed yield.**

KERNEL tokens allocated to users who never claim (lost keys, abandoned wallets, users who miss the distribution window) will remain locked in `KernelMerkleDistributor` indefinitely. The owner has no path to reclaim or redirect these tokens. The contract's `kernel` balance can only decrease via user `claim`/`claimAndStake` calls; there is no administrative drain path. [3](#0-2) 

### Likelihood Explanation
**Low.** In any real-world token distribution, a non-trivial fraction of eligible addresses never claim (lost keys, inactive wallets, users unaware of the airdrop). This is a near-certain outcome over a long enough time horizon, making the freeze of some portion of the KERNEL supply a practical certainty, not merely theoretical.

### Recommendation
Add a time-gated recovery function analogous to the one already present in `KernelTop100MerkleDistributor`:

```solidity
function withdrawTokens(address _token, uint256 _amount, address _recipient) external onlyOwner {
    UtilLib.checkNonZeroAddress(_token);
    UtilLib.checkNonZeroAddress(_recipient);
    if (_amount == 0) revert ZeroValueProvided();
    IERC20(_token).safeTransfer(_recipient, _amount);
    emit TokensWithdrawn(_token, _amount, _recipient);
}
```

Optionally gate it behind a time-lock (e.g., callable only after the distribution window closes) to preserve user trust.

### Proof of Concept

1. Protocol deploys `KernelMerkleDistributor` and funds it with 1,000,000 KERNEL.
2. Owner calls `setMerkleRoot(root)` to open the distribution.
3. 80% of eligible users claim their tokens over the distribution period.
4. The remaining 20% (200,000 KERNEL) is never claimed.
5. Owner attempts to recover the 200,000 KERNEL — no function exists to do so.
6. The 200,000 KERNEL is permanently locked in the contract. [4](#0-3)

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

**File:** contracts/KERNEL/KernelMerkleDistributor.sol (L352-424)
```text
    /**
     * @notice Sets the KernelDepositPool contract address
     * @param _kernelDepositPool The address of the new KernelDepositPool contract
     */
    function setKernelDepositPool(address _kernelDepositPool) external onlyOwner {
        UtilLib.checkNonZeroAddress(_kernelDepositPool);

        address oldKernelDepositPool = address(kernelDepositPool);
        kernelDepositPool = IKernelDepositPool(_kernelDepositPool);

        // Revoke the approval of the old KernelDepositPool contract to spend KERNEL tokens on behalf of this contract
        kernel.forceApprove(oldKernelDepositPool, 0);

        // Approve the KernelDepositPool contract to spend an unlimited amount of KERNEL tokens on behalf of this
        // contract
        kernel.forceApprove(_kernelDepositPool, type(uint256).max);

        emit KernelDepositPoolUpdated(_kernelDepositPool);
    }

    /**
     * @notice Sets the protocol treasury address
     * @param _protocolTreasury The address of the new protocol treasury
     */
    function setProtocolTreasury(address _protocolTreasury) external onlyOwner {
        UtilLib.checkNonZeroAddress(_protocolTreasury);

        protocolTreasury = _protocolTreasury;

        emit ProtocolTreasuryUpdated(protocolTreasury);
    }

    /**
     * @notice Sets the fee in basis points
     * @param _feeInBPS The new fee in basis points
     */
    function setFeeInBPS(uint256 _feeInBPS) external onlyOwner {
        if (_feeInBPS > MAX_FEE_IN_BPS) {
            revert InvalidFeeInBPS();
        }

        feeInBPS = _feeInBPS;

        emit FeeInBPSUpdated(feeInBPS);
    }

    /**
     * @notice Sets the new merkle root
     * @param _merkleRootToSet The new merkle root to be set
     */
    function setMerkleRoot(bytes32 _merkleRootToSet) external onlyOwner {
        if (_merkleRootToSet == bytes32(0)) {
            revert ZeroValueProvided();
        }

        currentMerkleRoot = _merkleRootToSet;

        currentMerkleRootIndex++;
        currentIndex++;

        emit MerkleRootSet(currentMerkleRootIndex, currentMerkleRoot);
    }

    /// @dev Pauses the contract
    function pause() external onlyOwner {
        _pause();
    }

    /// @dev Unpauses the contract
    function unpause() external onlyOwner {
        _unpause();
    }
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
