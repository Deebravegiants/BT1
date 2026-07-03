### Title
KERNEL Staking Token Permanently Stuck When Sent Directly via ERC20 Transfer - (File: contracts/KERNEL/KernelDepositPool.sol)

### Summary
`KernelDepositPool` is a staking contract where users stake `kernelToken` (KERNEL) to earn `rewardsToken` rewards. The contract has no token recovery mechanism of any kind. If a user accidentally sends KERNEL tokens directly via a plain ERC20 `transfer()` call instead of calling `stake()`, those tokens are permanently frozen in the contract with no path to recovery.

### Finding Description
`KernelDepositPool` accepts KERNEL tokens exclusively through the `stake()` function, which uses `safeTransferFrom` and credits the depositor's `balanceOf` mapping and `totalKernelStaked`. [1](#0-0) 

However, the contract has no `recoverTokens`, `rescue`, `sweep`, or any equivalent admin function. It does not inherit from `Recoverable` (which provides `recoverTokens`). Any KERNEL tokens sent directly to the contract address via a raw ERC20 `transfer()` are not credited to any user's `balanceOf`, are not included in `totalKernelStaked`, and cannot be withdrawn by any path. [2](#0-1) 

The `claimWithdrawal` function only transfers amounts tracked in the `withdrawals` mapping, which is populated only through `initiateWithdrawal`, which itself requires a prior `stake()` call. [3](#0-2) 

The `notifyRewardAmount` function uses a balance-before/after pattern to measure received reward tokens, so directly-sent reward tokens are also not counted in reward distribution and remain stuck. [4](#0-3) 

By contrast, the `Recoverable` utility contract used elsewhere in the codebase provides exactly this capability, but `KernelDepositPool` does not use it. [5](#0-4) 

### Impact Explanation
Any KERNEL tokens sent directly to `KernelDepositPool` via ERC20 `transfer()` are permanently frozen. There is no admin function, no sweep function, and no upgrade path that can recover them without a contract upgrade. This constitutes permanent freezing of user funds.

**Impact: Medium — Permanent freezing of funds (KERNEL tokens irretrievably locked).**

### Likelihood Explanation
Users interacting with staking contracts frequently confuse a direct ERC20 `transfer()` to the contract address with the `stake()` call, especially when using block explorers, hardware wallets, or custom scripts. This is a well-documented pattern in DeFi. The `KernelDepositPool` is a publicly accessible staking contract, making this a realistic scenario.

**Likelihood: Low** (accidental, not attacker-controlled, but a known recurring pattern in production).

### Recommendation
Add a token recovery function restricted to the admin role, similar to the existing `Recoverable` contract already present in the codebase. The function should allow recovery of any token **except** the amount currently tracked as staked (`totalKernelStaked`) to avoid allowing the admin to drain legitimate user stakes. Alternatively, inherit from `Recoverable` and add a guard that prevents recovering more than `IERC20(kernelToken).balanceOf(address(this)) - totalKernelStaked`.

### Proof of Concept
1. Alice intends to stake 1000 KERNEL. She calls `kernelToken.transfer(address(kernelDepositPool), 1000e18)` directly instead of `kernelDepositPool.stake(1000e18)`.
2. The 1000 KERNEL tokens are now held by `KernelDepositPool`, but `balanceOf[Alice] == 0` and `totalKernelStaked` is unchanged.
3. Alice cannot call `initiateWithdrawal` (her `balanceOf` is 0, so it reverts with `InsufficientStakedBalance`).
4. No admin function exists to recover the tokens — `KernelDepositPool` has no `recoverTokens`, `rescue`, or sweep function and does not inherit `Recoverable`.
5. The 1000 KERNEL tokens are permanently locked in the contract. [6](#0-5)

### Citations

**File:** contracts/KERNEL/KernelDepositPool.sol (L90-93)
```text
    uint256 public totalKernelStaked;

    /// @notice The balance of staked KERNEL tokens for each user
    mapping(address user => uint256 stakedBalance) public balanceOf;
```

**File:** contracts/KERNEL/KernelDepositPool.sol (L281-289)
```text
    function stake(uint256 _amount) external nonReentrant updateReward(msg.sender) {
        if (_amount == 0) revert AmountZero();

        balanceOf[msg.sender] += _amount;
        totalKernelStaked += _amount;
        kernelToken.safeTransferFrom(msg.sender, address(this), _amount);

        emit Staked(msg.sender, _amount);
    }
```

**File:** contracts/KERNEL/KernelDepositPool.sol (L320-323)
```text
    function initiateWithdrawal(uint256 _amount) external nonReentrant updateReward(msg.sender) {
        if (_amount == 0) revert AmountZero();
        if (balanceOf[msg.sender] < _amount) revert InsufficientStakedBalance();
        if (userWithdrawalIds[msg.sender].length >= maxNumberOfWithdrawalsPerUser) revert WithdrawalLimitReached();
```

**File:** contracts/KERNEL/KernelDepositPool.sol (L375-377)
```text
        // Transfer the KERNEL tokens from contract to user
        kernelToken.safeTransfer(msg.sender, withdrawal.amount);

```

**File:** contracts/KERNEL/KernelDepositPool.sol (L572-577)
```text
        // Transfer reward tokens into the contract
        uint256 balanceBefore = rewardsToken.balanceOf(address(this));
        rewardsToken.safeTransferFrom(msg.sender, address(this), _amount);
        uint256 balanceAfter = rewardsToken.balanceOf(address(this));
        // Calculate the actual amount of tokens received in case of a transfer fee (tax)
        uint256 receivedAmount = balanceAfter - balanceBefore;
```

**File:** contracts/utils/Recoverable.sol (L41-57)
```text
    function recoverTokens(
        address tokenAddress,
        address recipient,
        uint256 amount
    )
        external
        onlyRole(DEFAULT_ADMIN_ROLE)
    {
        UtilLib.checkNonZeroAddress(tokenAddress);
        UtilLib.checkNonZeroAddress(recipient);
        if (amount == 0) revert ZeroAmount();
        if (IERC20(tokenAddress).balanceOf(address(this)) < amount) revert InsufficientBalance();

        IERC20(tokenAddress).safeTransfer(recipient, amount);

        emit TokensRecovered(tokenAddress, recipient, amount);
    }
```
