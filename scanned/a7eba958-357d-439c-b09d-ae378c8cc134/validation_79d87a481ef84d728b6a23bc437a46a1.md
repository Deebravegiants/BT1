### Title
`setKernelDepositPool` Does Not Validate `STAKE_FOR_ROLE` on the New Pool, Breaking `claimAndStake` for All Users - (File: contracts/KERNEL/KernelMerkleDistributor.sol, contracts/KERNEL/KernelTop100MerkleDistributor.sol)

### Summary
`KernelMerkleDistributor.setKernelDepositPool` and `KernelTop100MerkleDistributor.setKernelDepositPool` update the `kernelDepositPool` reference and correctly rotate the ERC-20 approval, but neither function verifies that the new `KernelDepositPool` has already granted `STAKE_FOR_ROLE` to the distributor. Because `KernelDepositPool.stakeFor` is gated by `onlyRole(STAKE_FOR_ROLE)`, any call to `claimAndStake` will revert for every user until the role is separately configured on the new pool.

### Finding Description
Both distributor contracts expose a `claimAndStake` path that internally calls `IKernelDepositPool(kernelDepositPool).stakeFor(account, amountToStake)`.

`KernelDepositPool.stakeFor` enforces:

```solidity
function stakeFor(address _account, uint256 _amount)
    external nonReentrant onlyRole(STAKE_FOR_ROLE) updateReward(_account)
```

The `STAKE_FOR_ROLE` is not set automatically; it must be explicitly granted by the new pool's admin to the distributor address.

`setKernelDepositPool` in `KernelMerkleDistributor`:

```solidity
function setKernelDepositPool(address _kernelDepositPool) external onlyOwner {
    UtilLib.checkNonZeroAddress(_kernelDepositPool);
    address oldKernelDepositPool = address(kernelDepositPool);
    kernelDepositPool = IKernelDepositPool(_kernelDepositPool);
    kernel.forceApprove(oldKernelDepositPool, 0);
    kernel.forceApprove(_kernelDepositPool, type(uint256).max);
    emit KernelDepositPoolUpdated(_kernelDepositPool);
}
```

And in `KernelTop100MerkleDistributor`:

```solidity
function setKernelDepositPool(address _kernelDepositPool) external onlyOwner {
    UtilLib.checkNonZeroAddress(_kernelDepositPool);
    address oldKernelDepositPool = address(kernelDepositPool);
    kernel.forceApprove(oldKernelDepositPool, 0);
    kernel.forceApprove(_kernelDepositPool, type(uint256).max);
    kernelDepositPool = IKernelDepositPool(_kernelDepositPool);
    emit KernelDepositPoolUpdated(_kernelDepositPool);
}
```

Neither setter checks that `newPool.hasRole(STAKE_FOR_ROLE, address(this))`. The ERC-20 approval is correctly rotated, but the access-control relationship is silently absent. This is structurally identical to the FlywheelCore pattern: the setter updates a contract reference without verifying the back-permission that the new contract must hold toward the caller.

### Impact Explanation
After `setKernelDepositPool` is called with a new pool that has not yet granted `STAKE_FOR_ROLE` to the distributor, every invocation of `claimAndStake` reverts at the `stakeFor` call. Because the revert unwinds the entire transaction, no state is mutated and no funds are lost; however, the `claimAndStake` feature — a core advertised function of both distributor contracts — is completely non-operational for all users. Users must fall back to `claim` and stake manually, defeating the atomic convenience guarantee. This maps to **Low: contract fails to deliver promised returns, but doesn't lose value**.

### Likelihood Explanation
The operational window is realistic. Deploying a new `KernelDepositPool`, calling `setKernelDepositPool`, and separately granting `STAKE_FOR_ROLE` are three independent transactions. Forgetting or delaying the role grant — especially under time pressure or during an upgrade — leaves `claimAndStake` silently broken with no on-chain signal. The original FlywheelCore report explicitly cited this class of operational mistake as a meaningful risk factor.

### Recommendation
Add a role-existence check inside `setKernelDepositPool` in both contracts before accepting the new address:

```solidity
require(
    IKernelDepositPool(_kernelDepositPool).hasRole(
        IKernelDepositPool(_kernelDepositPool).STAKE_FOR_ROLE(),
        address(this)
    ),
    "Distributor lacks STAKE_FOR_ROLE on new pool"
);
```

This mirrors the recommended fix in the original report: validate the back-reference (here, the role grant) before committing the pointer update.

### Proof of Concept

1. Owner deploys a new `KernelDepositPool` but does **not** call `grantRole(STAKE_FOR_ROLE, address(distributor))` on it.
2. Owner calls `KernelMerkleDistributor.setKernelDepositPool(newPool)`. The function succeeds; `kernelDepositPool` is updated and the ERC-20 approval is rotated.
3. Any user calls `claimAndStake(index, account, cumulativeAmount, proof)`.
4. `_processClaim` succeeds; execution reaches `IKernelDepositPool(kernelDepositPool).stakeFor(account, amountToStake)`.
5. `KernelDepositPool.stakeFor` reverts with `AccessControl: account … is missing role …` because the distributor was never granted `STAKE_FOR_ROLE` on the new pool.
6. The entire transaction reverts. `claimAndStake` is broken for every user until the role is manually granted.

Affected functions and lines:

- `KernelMerkleDistributor.setKernelDepositPool` — no role validation [1](#0-0) 

- `KernelMerkleDistributor.claimAndStake` — calls `stakeFor` which requires `STAKE_FOR_ROLE` [2](#0-1) 

- `KernelTop100MerkleDistributor.setKernelDepositPool` — same missing check [3](#0-2) 

- `KernelTop100MerkleDistributor.claimAndStake` — calls `stakeFor` [4](#0-3) 

- `KernelDepositPool.stakeFor` — enforces `onlyRole(STAKE_FOR_ROLE)` on the caller [5](#0-4)

### Citations

**File:** contracts/KERNEL/KernelMerkleDistributor.sol (L270-285)
```text
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

**File:** contracts/KERNEL/KernelTop100MerkleDistributor.sol (L345-374)
```text
    function claimAndStake(uint256 amount, bytes32[] calldata merkleProof) external nonReentrant whenNotPaused {
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
        uint256 amountToStake = claimableAmount - fee;

        // Transfer fee and stake tokens
        if (fee > 0) {
            kernel.safeTransfer(protocolTreasury, fee);
        }

        kernelDepositPool.stakeFor(user, amountToStake);

        emit ClaimedAndStaked(user, amountToStake);
    }
```

**File:** contracts/KERNEL/KernelTop100MerkleDistributor.sol (L398-410)
```text
    function setKernelDepositPool(address _kernelDepositPool) external onlyOwner {
        UtilLib.checkNonZeroAddress(_kernelDepositPool);

        address oldKernelDepositPool = address(kernelDepositPool);

        // Revoke old approval and set new one
        kernel.forceApprove(oldKernelDepositPool, 0);
        kernel.forceApprove(_kernelDepositPool, type(uint256).max);

        kernelDepositPool = IKernelDepositPool(_kernelDepositPool);

        emit KernelDepositPoolUpdated(_kernelDepositPool);
    }
```

**File:** contracts/KERNEL/KernelDepositPool.sol (L296-314)
```text
    function stakeFor(
        address _account,
        uint256 _amount
    )
        external
        nonReentrant
        onlyRole(STAKE_FOR_ROLE)
        updateReward(_account)
    {
        UtilLib.checkNonZeroAddress(_account);

        if (_amount == 0) revert AmountZero();

        balanceOf[_account] += _amount;
        totalKernelStaked += _amount;
        kernelToken.safeTransferFrom(msg.sender, address(this), _amount);

        emit StakedFor(msg.sender, _account, _amount);
    }
```
