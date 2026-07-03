### Title
Missing Token Recovery Function Permanently Locks Surplus KERNEL — (`contracts/KERNEL/KernelMerkleDistributor.sol`)

---

### Summary

`KernelMerkleDistributor` has no `withdrawTokens` or equivalent recovery function. Any KERNEL balance exceeding the sum of all `cumulativeAmounts` encoded in the active merkle tree is permanently frozen in the contract with no callable path to recover it.

---

### Finding Description

The entire set of admin functions in `KernelMerkleDistributor` is:

- `setKernelDepositPool`
- `setProtocolTreasury`
- `setFeeInBPS`
- `setMerkleRoot`
- `pause` / `unpause` [1](#0-0) 

None of these move tokens out of the contract. The only token-outflow paths are `claim` and `claimAndStake`, both of which route through `_processClaim`: [2](#0-1) 

`_processClaim` pays out at most `cumulativeAmount - userClaims[account].cumulativeAmount` per user. Once every leaf in the merkle tree has been claimed, the maximum claimable amount is exactly the sum of all `cumulativeAmounts`. Any KERNEL held by the contract above that sum has no exit path.

By contrast, the sibling contract `KernelTop100MerkleDistributor` explicitly provides this safety valve: [3](#0-2) 

`KernelMerkleDistributor` omits this function entirely.

---

### Impact Explanation

Any surplus KERNEL — whether from over-funding, a merkle root update that reduces the total allocation, or tokens sent directly to the contract — is permanently frozen. The owner cannot recover it; no user can claim it. This matches the **Medium — Permanent freezing of unclaimed yield** impact scope.

---

### Likelihood Explanation

This is a realistic operational scenario, not a theoretical one:

1. The owner funds the contract with `N` KERNEL and later sets a merkle root whose `cumulativeAmounts` sum to `N - k` (e.g., due to a revised distribution, a rounding decision, or a simple miscalculation).
2. All valid claims are exhausted.
3. `k` KERNEL remain locked forever.

No attacker action is required. The owner themselves cannot undo it.

---

### Recommendation

Add a `withdrawTokens` function restricted to `onlyOwner`, identical to the one already present in `KernelTop100MerkleDistributor`:

```solidity
function withdrawTokens(address _token, uint256 _amount, address _recipient) external onlyOwner {
    UtilLib.checkNonZeroAddress(_token);
    UtilLib.checkNonZeroAddress(_recipient);
    if (_amount == 0) revert ZeroValueProvided();
    IERC20(_token).safeTransfer(_recipient, _amount);
    emit TokensWithdrawn(_token, _amount, _recipient);
}
```

---

### Proof of Concept

```solidity
// 1. Deploy KernelMerkleDistributor
// 2. Transfer 1000e18 KERNEL to the distributor
// 3. Build a merkle tree with 3 leaves summing to 900e18 total cumulativeAmounts
// 4. Call setMerkleRoot(root)
// 5. All 3 users call claim() — exhausting all valid leaves
// 6. Assert:
assertEq(kernel.balanceOf(address(distributor)), 100e18); // surplus locked
// 7. Attempt any recovery — no function exists, all calls revert
// => 100e18 KERNEL permanently frozen
``` [4](#0-3) [5](#0-4)

### Citations

**File:** contracts/KERNEL/KernelMerkleDistributor.sol (L250-266)
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
```

**File:** contracts/KERNEL/KernelMerkleDistributor.sol (L325-345)
```text
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
```

**File:** contracts/KERNEL/KernelMerkleDistributor.sol (L348-424)
```text
    /*//////////////////////////////////////////////////////////////
                            ADMIN FUNCTIONS
    //////////////////////////////////////////////////////////////*/

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
