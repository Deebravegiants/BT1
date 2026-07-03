### Title
No Token Recovery Mechanism in `KernelMerkleDistributor` Permanently Freezes Unclaimed KERNEL Tokens - (File: contracts/KERNEL/KernelMerkleDistributor.sol)

---

### Summary

`KernelMerkleDistributor` holds KERNEL tokens that users must actively claim. The contract enforces that only the account holder can trigger a claim, and unlike its sibling `KernelTop100MerkleDistributor`, it contains no admin rescue or token-withdrawal function. Any KERNEL tokens that go unclaimed — due to lost keys, user inactivity, or a permanently paused contract — are irretrievably frozen.

---

### Finding Description

KERNEL tokens are pre-loaded into `KernelMerkleDistributor` and distributed via a pull-based claim mechanic. The `_processClaim()` internal function enforces a strict `account == msg.sender` check, meaning no third party (including the owner) can claim on behalf of a user: [1](#0-0) 

This means if a user loses their private key, their allocated KERNEL tokens are permanently stranded in the contract. The full admin function set of `KernelMerkleDistributor` consists only of:

- `setKernelDepositPool` [2](#0-1) 
- `setProtocolTreasury` [3](#0-2) 
- `setFeeInBPS` [4](#0-3) 
- `setMerkleRoot` [5](#0-4) 
- `pause` / `unpause` [6](#0-5) 

None of these allow token recovery. By direct contrast, the sibling contract `KernelTop100MerkleDistributor` explicitly includes a `withdrawTokens()` admin rescue function: [7](#0-6) 

The asymmetry is a clear design gap: the same protocol, same token, same claim pattern — but one contract can recover stranded tokens and the other cannot.

---

### Impact Explanation

**Medium — Permanent freezing of unclaimed yield.**

KERNEL tokens deposited into `KernelMerkleDistributor` that are never claimed are permanently locked. There is no function path — for the user, the owner, or any other actor — to move those tokens out of the contract. The tokens exist on-chain but are functionally destroyed.

---

### Likelihood Explanation

**Medium.** In any large-scale token distribution, a non-trivial fraction of recipients will fail to claim: lost keys, wallet compromise, user inactivity, or death. Additionally, if the contract is paused (`whenNotPaused` on both `claim` and `claimAndStake`) and never unpaused, the entire undistributed balance is frozen with no recourse. [8](#0-7) 

---

### Recommendation

Add a `withdrawTokens()` function to `KernelMerkleDistributor` mirroring the one already present in `KernelTop100MerkleDistributor`:

```solidity
function withdrawTokens(address _token, uint256 _amount, address _recipient) external onlyOwner {
    UtilLib.checkNonZeroAddress(_token);
    UtilLib.checkNonZeroAddress(_recipient);
    if (_amount == 0) revert ZeroValueProvided();
    IERC20(_token).safeTransfer(_recipient, _amount);
    emit TokensWithdrawn(_token, _amount, _recipient);
}
```

This allows the protocol to recover unclaimed KERNEL tokens and redistribute or return them, preventing permanent loss.

---

### Proof of Concept

1. Protocol loads `KernelMerkleDistributor` with 1,000,000 KERNEL tokens and sets a merkle root covering 1,000 users.
2. 950 users successfully call `claim()` and receive their tokens.
3. 50 users have lost their private keys. Their allocated tokens remain in the contract.
4. The owner calls `pause()` to halt the contract for an upgrade that never completes.
5. All remaining KERNEL tokens — both the 50 unclaimed user allocations and any operational buffer — are permanently frozen.
6. No function in `KernelMerkleDistributor` can move these tokens. The `_processClaim` path is blocked by `whenNotPaused`, and no rescue path exists. [9](#0-8)

### Citations

**File:** contracts/KERNEL/KernelMerkleDistributor.sol (L258-266)
```text
        nonReentrant
        whenNotPaused
    {
        uint256 amountToSend = _processClaim(index, account, cumulativeAmount, merkleProof);

        kernel.safeTransfer(account, amountToSend);

        emit Claimed(index, account, amountToSend);
    }
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

**File:** contracts/KERNEL/KernelMerkleDistributor.sol (L356-370)
```text
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
```

**File:** contracts/KERNEL/KernelMerkleDistributor.sol (L376-382)
```text
    function setProtocolTreasury(address _protocolTreasury) external onlyOwner {
        UtilLib.checkNonZeroAddress(_protocolTreasury);

        protocolTreasury = _protocolTreasury;

        emit ProtocolTreasuryUpdated(protocolTreasury);
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

**File:** contracts/KERNEL/KernelMerkleDistributor.sol (L402-413)
```text
    function setMerkleRoot(bytes32 _merkleRootToSet) external onlyOwner {
        if (_merkleRootToSet == bytes32(0)) {
            revert ZeroValueProvided();
        }

        currentMerkleRoot = _merkleRootToSet;

        currentMerkleRootIndex++;
        currentIndex++;

        emit MerkleRootSet(currentMerkleRootIndex, currentMerkleRoot);
    }
```

**File:** contracts/KERNEL/KernelMerkleDistributor.sol (L416-423)
```text
    function pause() external onlyOwner {
        _pause();
    }

    /// @dev Unpauses the contract
    function unpause() external onlyOwner {
        _unpause();
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
