### Title
Immediate Pause by `PAUSER_ROLE` Blocks Users from Completing Pending Withdrawals - (File: `contracts/LRTWithdrawalManager.sol`)

---

### Summary

The `LRTWithdrawalManager` contract allows a `PAUSER_ROLE` holder to immediately pause the contract via `pause()`. When paused, users who have already called `initiateWithdrawal` — transferring their rsETH into the contract — are blocked from calling `completeWithdrawal` due to the `whenNotPaused` modifier. This creates a temporary freeze of user funds with no recourse during the pause period.

---

### Finding Description

The withdrawal lifecycle in `LRTWithdrawalManager` is a two-step process:

1. **`initiateWithdrawal`** — the user transfers rsETH to the contract, which records a `WithdrawalRequest` and commits an expected asset amount.
2. **`completeWithdrawal`** — after the `withdrawalDelayBlocks` period, the user calls this to receive their ETH or LST.

Both functions are guarded by `whenNotPaused`: [1](#0-0) [2](#0-1) 

The `pause()` function is callable immediately by any address holding `PAUSER_ROLE`, with no time delay: [3](#0-2) 

When a user calls `initiateWithdrawal`, their rsETH is immediately transferred into the contract: [4](#0-3) 

If the contract is paused at any point after `initiateWithdrawal` but before `completeWithdrawal`, the user's rsETH is held by the contract and the user cannot retrieve their underlying ETH/LST. The `withdrawalDelayBlocks` default is `8 days / 12 seconds`, meaning users routinely have funds in-flight for days. [5](#0-4) 

There is no emergency withdrawal path for users with pending requests during a pause. The `instantWithdrawal` path is also blocked by `whenNotPaused`: [6](#0-5) 

---

### Impact Explanation

**Medium — Temporary freezing of funds.**

A user who has submitted `initiateWithdrawal` has already surrendered their rsETH to the contract. If the contract is paused before they can call `completeWithdrawal`, their rsETH is locked in the contract and their expected ETH/LST is inaccessible for the duration of the pause. Given the 8-day default delay window, many users will have funds in-flight at any given time. The freeze is temporary (until unpause), but the user has no recourse during the pause period.

---

### Likelihood Explanation

The `PAUSER_ROLE` is a dedicated operational role (separate from `LRTAdmin`) designed to be used in security incidents. Pausing for legitimate reasons (e.g., oracle manipulation, bridge exploit) is a realistic and expected scenario. At any point during a pause, all users with pending withdrawal requests — which can number in the hundreds given the 8-day delay — are simultaneously frozen. The likelihood of at least one user being affected during any pause event is high.

---

### Recommendation

Allow `completeWithdrawal` (and optionally `completeWithdrawalForUser`) to execute even when the contract is paused, since these functions only disburse already-committed assets to users who have already surrendered their rsETH. Alternatively, introduce a time-delayed pause mechanism (e.g., a timelock) so users have advance notice to complete pending withdrawals before the pause takes effect.

---

### Proof of Concept

1. Alice calls `initiateWithdrawal(ETH, 1e18, "")`. Her rsETH is transferred to `LRTWithdrawalManager`. A `WithdrawalRequest` is recorded with `withdrawalStartBlock = block.number`.
2. The `PAUSER_ROLE` holder calls `pause()` for a legitimate security reason. The pause takes effect immediately.
3. After `withdrawalDelayBlocks` blocks pass, Alice calls `completeWithdrawal(ETH, "")`. The call reverts with `Pausable: paused`.
4. Alice's rsETH remains locked in the contract. She cannot access her ETH/LST for the duration of the pause. [7](#0-6)

### Citations

**File:** contracts/LRTWithdrawalManager.sol (L94-94)
```text
        withdrawalDelayBlocks = 8 days / 12 seconds;
```

**File:** contracts/LRTWithdrawalManager.sol (L150-158)
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
```

**File:** contracts/LRTWithdrawalManager.sol (L166-166)
```text
        IERC20(lrtConfig.rsETH()).safeTransferFrom(msg.sender, address(this), rsETHUnstaked);
```

**File:** contracts/LRTWithdrawalManager.sol (L183-185)
```text
    function completeWithdrawal(address asset, string calldata referralId) external nonReentrant whenNotPaused {
        _processWithdrawalCompletion(asset, msg.sender, referralId);
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L212-220)
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
```

**File:** contracts/LRTWithdrawalManager.sol (L347-349)
```text
    function pause() external onlyRole(LRTConstants.PAUSER_ROLE) {
        _pause();
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L699-738)
```text
    function _processWithdrawalCompletion(address asset, address user, string calldata referralId) internal {
        if (userAssociatedNonces[asset][user].empty()) {
            revert NoWithdrawalRequests(user, asset);
        }

        // Retrieve and remove the oldest withdrawal request for the user.
        uint256 usersFirstWithdrawalRequestNonce = userAssociatedNonces[asset][user].popFront();
        // Ensure the request is already unlocked.
        if (usersFirstWithdrawalRequestNonce >= nextLockedNonce[asset]) revert WithdrawalLocked();

        bytes32 requestId = getRequestId(asset, usersFirstWithdrawalRequestNonce);
        WithdrawalRequest memory request = withdrawalRequests[requestId];

        delete withdrawalRequests[requestId];

        // Check that the withdrawal delay has passed since the request's initiation.
        if (block.number < request.withdrawalStartBlock + withdrawalDelayBlocks) revert WithdrawalDelayNotPassed();

        unlockedWithdrawalsCount[asset]--;

        // If Aave integration is enabled and asset is ETH, withdraw from Aave if needed
        if (isAaveIntegrationEnabled && asset == LRTConstants.ETH_TOKEN) {
            uint256 contractBalance = address(this).balance;
            if (contractBalance < request.expectedAssetAmount) {
                uint256 amountNeeded = request.expectedAssetAmount - contractBalance;
                _withdrawFromAave(amountNeeded);

                // Verify we have sufficient balance after withdrawal
                uint256 balanceAfter = address(this).balance;
                if (balanceAfter < request.expectedAssetAmount) {
                    revert InsufficientLiquidityForWithdrawal();
                }
            }
        }

        _transferAsset(asset, user, request.expectedAssetAmount);

        emit ReferralIdEmitted(referralId);
        emit AssetWithdrawalFinalized(user, asset, request.rsETHUnstaked, request.expectedAssetAmount);
    }
```
