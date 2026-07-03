### Title
`KernelMerkleDistributor.claimAndStake` is permanently non-functional due to missing `STAKE_FOR_ROLE` registration - (File: contracts/KERNEL/KernelMerkleDistributor.sol)

### Summary

`KernelMerkleDistributor.initialize` sets up the ERC-20 token approval needed for `stakeFor` to pull KERNEL tokens, but never ensures `STAKE_FOR_ROLE` is granted to `KernelMerkleDistributor` on `KernelDepositPool`. Because `stakeFor` is gated by `onlyRole(STAKE_FOR_ROLE)`, every call to `claimAndStake` will revert unconditionally, making the function permanently broken at the code level.

### Finding Description

`KernelMerkleDistributor.initialize` performs exactly one wiring step toward enabling `claimAndStake`: it approves `KernelDepositPool` to pull KERNEL tokens from the distributor. [1](#0-0) 

This is the Solidity equivalent of registering the QueryServer — the read-side plumbing is present. However, the write-side plumbing — granting `STAKE_FOR_ROLE` to `KernelMerkleDistributor` on `KernelDepositPool` — is entirely absent from both `initialize` and `setKernelDepositPool`. [2](#0-1) 

`KernelDepositPool.stakeFor` is the only path through which `claimAndStake` can complete: [3](#0-2) 

The `onlyRole(STAKE_FOR_ROLE)` modifier will revert every invocation because `KernelMerkleDistributor` is never granted that role anywhere in the codebase. `KernelDepositPool.initialize` only grants `DEFAULT_ADMIN_ROLE`: [4](#0-3) 

The `claimAndStake` entry point: [5](#0-4) 

Because the revert happens inside `stakeFor`, the entire transaction is rolled back, including the `_processClaim` state updates. Users are not permanently locked out of their tokens — they can still call `claim` — but the `claimAndStake` path is completely dead.

### Impact Explanation

The `claimAndStake` function is a publicly advertised, user-facing feature (evidenced by the dedicated `ClaimedAndStaked` event and the `IKernelDepositPool.stakeFor` interface). It fails to execute for every caller. This matches the **Low** impact class: *"Contract fails to deliver promised returns, but doesn't lose value."* No funds are lost because the transaction reverts atomically; users retain their unclaimed KERNEL and can claim via the separate `claim` function.

### Likelihood Explanation

Any user who discovers `claimAndStake` and attempts to use it will receive a revert. The failure is deterministic and affects 100 % of `claimAndStake` calls from the moment of deployment until an admin separately grants `STAKE_FOR_ROLE` — a step that is not documented, not enforced in code, and not performed by either initializer.

### Recommendation

Grant `STAKE_FOR_ROLE` to `KernelMerkleDistributor` on `KernelDepositPool` as part of the deployment sequence, mirroring how the token approval is already wired in `initialize`. Concretely, after deploying both contracts the deployer should call:

```solidity
kernelDepositPool.grantRole(STAKE_FOR_ROLE, address(kernelMerkleDistributor));
```

Alternatively, update `KernelMerkleDistributor.initialize` to accept the `KernelDepositPool` admin as a parameter and call `grantRole` atomically, so the registration cannot be forgotten.

### Proof of Concept

1. Deploy `KernelDepositPool` (admin = `deployer`, no `STAKE_FOR_ROLE` granted to anyone).
2. Deploy `KernelMerkleDistributor` pointing at `KernelDepositPool`; `initialize` runs `kernel.forceApprove(kernelDepositPool, type(uint256).max)` but grants no role.
3. Fund `KernelMerkleDistributor` with KERNEL tokens and set a valid Merkle root.
4. Call `claimAndStake(index, account, cumulativeAmount, proof)` with a valid proof.
5. Execution reaches `KernelDepositPool.stakeFor`; the `onlyRole(STAKE_FOR_ROLE)` check reverts with `AccessControl: account 0x… is missing role 0x…`.
6. The entire transaction reverts; the user's claim state is unchanged and no tokens move.
7. Calling `claim` with the same proof succeeds, confirming the Merkle logic is correct and only the role wiring is missing.

### Citations

**File:** contracts/KERNEL/KernelMerkleDistributor.sol (L224-226)
```text
        // Approve the KernelDepositPool contract to spend an unlimited amount of KERNEL tokens on behalf of this
        // contract
        kernel.forceApprove(_kernelDepositPool, type(uint256).max);
```

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

**File:** contracts/KERNEL/KernelMerkleDistributor.sol (L356-369)
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
```

**File:** contracts/KERNEL/KernelDepositPool.sol (L259-271)
```text
    function initialize(address _admin, address _kernelToken, address _rewardToken) external initializer {
        UtilLib.checkNonZeroAddress(_admin);
        UtilLib.checkNonZeroAddress(_kernelToken);
        UtilLib.checkNonZeroAddress(_rewardToken);

        __AccessControl_init();
        __ReentrancyGuard_init();

        _setupRole(DEFAULT_ADMIN_ROLE, _admin);

        kernelToken = IERC20(_kernelToken);
        rewardsToken = IERC20(_rewardToken);
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
