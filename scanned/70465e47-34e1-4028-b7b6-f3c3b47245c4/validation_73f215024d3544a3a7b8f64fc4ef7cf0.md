### Title
`claimAndStake()` Always Reverts Because Distributor Contracts Are Never Granted `STAKE_FOR_ROLE` in `KernelDepositPool` - (`contracts/KERNEL/KernelMerkleDistributor.sol`, `contracts/KERNEL/KernelTop100MerkleDistributor.sol`)

---

### Summary

Both `KernelMerkleDistributor` and `KernelTop100MerkleDistributor` expose a `claimAndStake()` function that is supposed to let users atomically claim their KERNEL token allocation and have it staked in `KernelDepositPool` in a single transaction. However, the internal call to `KernelDepositPool.stakeFor()` is guarded by `onlyRole(STAKE_FOR_ROLE)`, and no code anywhere in the production contracts ever grants either distributor contract that role. As a result, every call to `claimAndStake()` reverts unconditionally.

---

### Finding Description

`KernelDepositPool.stakeFor()` is the only entry point for staking on behalf of another account:

```solidity
// KernelDepositPool.sol L296-L302
function stakeFor(address _account, uint256 _amount)
    external
    nonReentrant
    onlyRole(STAKE_FOR_ROLE)   // ← role guard
    updateReward(_account)
{ ... }
```

`KernelMerkleDistributor.claimAndStake()` calls this function directly:

```solidity
// KernelMerkleDistributor.sol L280-L284
uint256 amountToStake = _processClaim(index, account, cumulativeAmount, merkleProof);
IKernelDepositPool(kernelDepositPool).stakeFor(account, amountToStake);
```

`KernelTop100MerkleDistributor.claimAndStake()` does the same:

```solidity
// KernelTop100MerkleDistributor.sol L371
kernelDepositPool.stakeFor(user, amountToStake);
```

`KernelDepositPool.initialize()` only grants `DEFAULT_ADMIN_ROLE` to the admin — it never grants `STAKE_FOR_ROLE` to any distributor:

```solidity
// KernelDepositPool.sol L259-L271
function initialize(address _admin, address _kernelToken, address _rewardToken) external initializer {
    ...
    _setupRole(DEFAULT_ADMIN_ROLE, _admin);
    ...
}
```

Neither distributor's `initialize()` contains any call to grant itself `STAKE_FOR_ROLE` in the pool. A codebase-wide search for `grantRole.*STAKE_FOR` returns zero matches, confirming no production code ever assigns this role to the distributor contracts.

---

### Impact Explanation

Every invocation of `claimAndStake()` on either distributor contract reverts at the `onlyRole(STAKE_FOR_ROLE)` check inside `KernelDepositPool.stakeFor()`. The entire transaction is rolled back, so no state is corrupted, but the advertised atomic claim-and-stake feature is completely non-functional. Users are forced to call `claim()` and then manually stake in a separate transaction, defeating the purpose of the function.

**Impact:** Low — Contract fails to deliver promised returns, but no funds are lost.

---

### Likelihood Explanation

The failure is deterministic and unconditional: every call to `claimAndStake()` reverts from the moment of deployment until an admin separately calls `grantRole(STAKE_FOR_ROLE, distributorAddress)` on `KernelDepositPool`. Any user who discovers the `claimAndStake()` function and attempts to use it will experience a revert. The likelihood of the broken state being encountered is high.

---

### Recommendation

Grant `STAKE_FOR_ROLE` to each distributor contract during initialization. The cleanest fix is to add the grant inside `KernelDepositPool.initialize()` (or a dedicated setter) and call it as part of the deployment sequence, or alternatively have each distributor's `initialize()` accept the pool address and call `IAccessControl(pool).grantRole(STAKE_FOR_ROLE, address(this))` — provided the deployer holds `DEFAULT_ADMIN_ROLE` at that point.

---

### Proof of Concept

1. Deploy `KernelDepositPool` with `initialize(admin, kernelToken, rewardToken)`.
2. Deploy `KernelMerkleDistributor` with `initialize(kernel, poolAddress, treasury, fee)`.
3. Admin sets a valid merkle root via `setMerkleRoot(root)`.
4. A user with a valid proof calls `claimAndStake(index, account, amount, proof)`.
5. `_processClaim` succeeds and returns `amountToStake`.
6. `IKernelDepositPool(kernelDepositPool).stakeFor(account, amountToStake)` is called.
7. `KernelDepositPool.stakeFor()` executes `onlyRole(STAKE_FOR_ROLE)` — the distributor does not hold this role → transaction reverts.
8. The same revert occurs for every call to `KernelTop100MerkleDistributor.claimAndStake()`. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

### Citations

**File:** contracts/KERNEL/KernelDepositPool.sol (L40-41)
```text
    /// @notice The role required to stake on behalf of another user
    bytes32 public constant STAKE_FOR_ROLE = keccak256("STAKE_FOR_ROLE");
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

**File:** contracts/KERNEL/KernelDepositPool.sol (L296-303)
```text
    function stakeFor(
        address _account,
        uint256 _amount
    )
        external
        nonReentrant
        onlyRole(STAKE_FOR_ROLE)
        updateReward(_account)
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

**File:** contracts/KERNEL/KernelTop100MerkleDistributor.sol (L345-373)
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
```
