### Title
Pausable Modifier on Withdrawal Completion Functions Temporarily Freezes User Funds - (File: contracts/LRTWithdrawalManager.sol)

### Summary
`LRTWithdrawalManager.sol` applies `whenNotPaused` to both `completeWithdrawal()` and `instantWithdrawal()`. When the contract is paused, users who have already committed their rsETH via `initiateWithdrawal()` cannot retrieve their underlying assets, causing a temporary freeze of funds.

### Finding Description
`LRTWithdrawalManager` is a pausable contract that manages the two-step withdrawal process: users first call `initiateWithdrawal()`, which transfers their rsETH into the contract, then later call `completeWithdrawal()` to receive their underlying LST/ETH.

The `whenNotPaused` modifier is applied to all user-facing withdrawal functions:

- `initiateWithdrawal()` at line 158 — starts the withdrawal, locks rsETH in the contract
- `completeWithdrawal()` at line 183 — finalizes the withdrawal, returns assets to user
- `instantWithdrawal()` at line 219 — single-step withdrawal path
- `unlockQueue()` at line 279 — operator function that must run before `completeWithdrawal()` can succeed [1](#0-0) 

When the contract is paused, a user who has already called `initiateWithdrawal()` (and had their rsETH transferred to the contract) is blocked from calling `completeWithdrawal()`. Additionally, the operator cannot call `unlockQueue()` to advance the queue. The user's rsETH is held in the contract with no exit path until the admin calls `unpause()`. [2](#0-1) 

The `pause()` function is callable by any address holding `PAUSER_ROLE`, while `unpause()` requires `onlyLRTAdmin`. [3](#0-2) 

### Impact Explanation
Users who have already committed rsETH to the withdrawal queue cannot recover their assets while the contract is paused. The rsETH is held inside `LRTWithdrawalManager` and cannot be returned until the admin unpauses. This constitutes a **temporary freezing of funds** (Medium severity per the allowed impact scope).

### Likelihood Explanation
The `PAUSER_ROLE` is a separate role from admin, meaning a broader set of actors can trigger the pause. Any security incident that causes the pauser to act will simultaneously block all in-flight withdrawals. Users who initiated withdrawals just before a pause event are directly affected with no recourse until unpause. This is a realistic operational scenario.

### Recommendation
Remove `whenNotPaused` from `completeWithdrawal()`, `completeWithdrawalForUser()`, and `instantWithdrawal()`. The pause mechanism should only restrict new deposits/withdrawal initiations, not the completion of already-committed withdrawals. This mirrors the recommendation in the referenced report: only apply pausable mechanisms to deposit/initiation functions, not to withdrawal completion functions.

### Proof of Concept
1. Alice calls `initiateWithdrawal(stETH, 1e18, "ref")`. Her 1e18 rsETH is transferred to `LRTWithdrawalManager`. [4](#0-3) 
2. The operator calls `unlockQueue(stETH, ...)` — but this also requires `whenNotPaused`.
3. A security event occurs; the PAUSER_ROLE holder calls `pause()`.
4. Alice calls `completeWithdrawal(stETH, "ref")` — reverts with `ContractPaused` (via `whenNotPaused`). [5](#0-4) 
5. Alice's rsETH remains locked in the contract. She cannot use `instantWithdrawal()` either (also `whenNotPaused`). [6](#0-5) 
6. Alice must wait indefinitely for the admin to call `unpause()` before she can recover any funds.

### Citations

**File:** contracts/LRTWithdrawalManager.sol (L150-185)
```text
    function initiateWithdrawal(
        address asset,
        uint256 rsETHUnstaked,
        string calldata referralId
    )
        external
        override
        nonReentrant
        whenNotPaused
        onlySupportedAsset(asset)
        onlySupportedStrategy(asset)
    {
        if (rsETHUnstaked == 0 || rsETHUnstaked < minRsEthAmountToWithdraw[asset]) {
            revert InvalidAmountToWithdraw();
        }

        IERC20(lrtConfig.rsETH()).safeTransferFrom(msg.sender, address(this), rsETHUnstaked);

        uint256 expectedAssetAmount = getExpectedAssetAmount(asset, rsETHUnstaked);

        if (expectedAssetAmount > getAvailableAssetAmount(asset)) revert ExceedAmountToWithdraw();

        // preventing over-withdrawal.
        assetsCommitted[asset] += expectedAssetAmount;

        _addUserWithdrawalRequest(asset, rsETHUnstaked, expectedAssetAmount);

        emit ReferralIdEmitted(referralId);
    }

    /// @notice Completes a user's withdrawal process by transferring the ETH/LST amount corresponding to the rsETH
    /// unstaked.
    /// @param asset The asset address the user wishes to withdraw.
    function completeWithdrawal(address asset, string calldata referralId) external nonReentrant whenNotPaused {
        _processWithdrawalCompletion(asset, msg.sender, referralId);
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L212-222)
```text
    function instantWithdrawal(
        address asset,
        uint256 rsETHUnstaked,
        string calldata referralId
    )
        external
        nonReentrant
        whenNotPaused
        onlySupportedAsset(asset)
        onlySupportedStrategy(asset)
        onlyInstantWithdrawalAllowed(asset)
```

**File:** contracts/LRTWithdrawalManager.sol (L268-280)
```text
    function unlockQueue(
        address asset,
        uint256 firstExcludedIndex,
        uint256 minimumAssetPrice,
        uint256 minimumRsEthPrice,
        uint256 maximumAssetPrice,
        uint256 maximumRsEthPrice
    )
        external
        nonReentrant
        onlySupportedAsset(asset)
        whenNotPaused
        onlyAssetTransferOrOperatorRole
```

**File:** contracts/LRTWithdrawalManager.sol (L347-354)
```text
    function pause() external onlyRole(LRTConstants.PAUSER_ROLE) {
        _pause();
    }

    /// @dev Returns to normal state. Contract must be paused.
    function unpause() external onlyLRTAdmin {
        _unpause();
    }
```
