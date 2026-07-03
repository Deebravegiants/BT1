### Title
Unprotected `withdrawTokens` Allows Owner to Drain Pending KERNEL Rewards, Blocking User Claims - (File: contracts/KERNEL/KernelTop100MerkleDistributor.sol)

### Summary
`KernelTop100MerkleDistributor.withdrawTokens` imposes no restriction on which token can be withdrawn. The owner can call it with the `kernel` token address and drain the entire KERNEL balance that users are entitled to claim under the vesting schedule, permanently stealing their unclaimed yield.

### Finding Description
`KernelTop100MerkleDistributor` holds KERNEL tokens that eligible users claim gradually over a 30-day vesting period via `claim()` or `claimAndStake()`. The contract's admin function `withdrawTokens` accepts an arbitrary `_token` address and transfers any amount to any recipient with no guard against withdrawing the `kernel` reward token itself:

```solidity
function withdrawTokens(address _token, uint256 _amount, address _recipient) external onlyOwner {
    UtilLib.checkNonZeroAddress(_token);
    UtilLib.checkNonZeroAddress(_recipient);
    if (_amount == 0) { revert ZeroValueProvided(); }
    IERC20(_token).safeTransfer(_recipient, _amount);   // no check: _token != address(kernel)
    emit TokensWithdrawn(_token, _amount, _recipient);
}
```

Because the function performs no check that `_token != address(kernel)`, the owner can call `withdrawTokens(address(kernel), kernel.balanceOf(address(this)), anyAddress)` and remove all KERNEL tokens from the distributor. After this call, every subsequent `claim()` or `claimAndStake()` call by a legitimate user will revert due to insufficient balance, permanently freezing their unclaimed vested yield. [1](#0-0) 

### Impact Explanation
All KERNEL tokens allocated to users but not yet claimed can be drained in a single transaction. Users who have a valid merkle proof and a non-zero vested amount will be unable to claim any tokens. This constitutes **theft of unclaimed yield** (High severity per the allowed impact scope). [2](#0-1) 

### Likelihood Explanation
The entry path is a single owner call with no preconditions. The contract holds a fixed KERNEL balance loaded at deployment; once drained, there is no recovery path for users. The vesting schedule (30 days) means a large fraction of user entitlements are always unclaimed at any given time, maximising the extractable amount. [3](#0-2) 

### Recommendation
Add an explicit guard in `withdrawTokens` that reverts when `_token == address(kernel)`:

```solidity
function withdrawTokens(address _token, uint256 _amount, address _recipient) external onlyOwner {
    if (_token == address(kernel)) revert CannotWithdrawKernel();
    ...
}
```

This mirrors the fix recommended in the reference report for CPOOL: protect the reward token from being swept. [1](#0-0) 

### Proof of Concept

1. Protocol deploys `KernelTop100MerkleDistributor` and funds it with 1,000,000 KERNEL for the top-100 airdrop recipients.
2. Vesting starts; users begin accumulating claimable amounts.
3. Owner calls:
   ```solidity
   distributor.withdrawTokens(
       address(kernel),
       kernel.balanceOf(address(distributor)),  // entire balance
       ownerControlledAddress
   );
   ```
4. Contract KERNEL balance drops to 0.
5. Any user calling `claim(amount, proof)` reaches `kernel.safeTransfer(user, amountToSend)` which reverts with `ERC20InsufficientBalance`.
6. All unclaimed vested KERNEL is permanently lost to users. [1](#0-0) [4](#0-3)

### Citations

**File:** contracts/KERNEL/KernelTop100MerkleDistributor.sol (L127-145)
```text
    uint256 public constant VESTING_DURATION = 30 days;

    /// @notice The KERNEL token distributed by this contract
    IERC20 public kernel;

    /// @notice The address of the protocol treasury
    address public protocolTreasury;

    /// @notice The fee in basis points
    uint256 public feeInBPS;

    /// @notice The KernelDepositPool contract address
    IKernelDepositPool public kernelDepositPool;

    /// @notice The merkle root
    bytes32 public merkleRoot;

    /// @notice The timestamp when vesting begins
    uint256 public vestingStartTimestamp;
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
