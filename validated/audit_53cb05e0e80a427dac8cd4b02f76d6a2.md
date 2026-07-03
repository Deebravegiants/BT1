Audit Report

## Title
Aave Pool Pause Causes Temporary Freezing of User ETH Withdrawals — (`contracts/LRTWithdrawalManager.sol`)

## Summary
When the Aave V3 pool is paused, `_withdrawFromAave` and `_collectInterestToTreasury` both call `aaveWETHGateway.withdrawETH` without any try/catch or pause-check guard, causing them to revert unconditionally. This blocks `completeWithdrawal` for ETH users whose requests require pulling funds from Aave, temporarily freezing their withdrawals for the entire duration of the Aave pause. The same revert also prevents `setAaveIntegrationEnabled(false)` and `emergencyWithdrawFromAave` from executing, leaving no admin-accessible bypass short of a proxy upgrade.

## Finding Description

**`_withdrawFromAave` — unconditional external call with no guard:** [1](#0-0) 
`_withdrawFromAave` calls `aaveWETHGateway.withdrawETH(aavePool, withdrawnAmount, address(this))` at L917 with no try/catch and no check for whether the Aave pool is paused. If the pool is paused, Aave's `withdraw` reverts, propagating the revert to every caller.

**`_collectInterestToTreasury` — same failure mode:** [2](#0-1) 
`_collectInterestToTreasury` also calls `aaveWETHGateway.withdrawETH` directly at L954 with no protection. It is called before `_withdrawFromAave` in both the disable and emergency paths, meaning even a zero-interest scenario still hits this call first.

**`completeWithdrawal` / `_processWithdrawalCompletion` — user ETH withdrawals freeze:** [3](#0-2) 
When `isAaveIntegrationEnabled == true` and the contract's idle ETH balance is less than `request.expectedAssetAmount`, `_withdrawFromAave` is called at L724. With Aave paused, this reverts the entire transaction. Because `delete withdrawalRequests[requestId]` at L712 is part of the same transaction, the state rolls back and the user's request is preserved — but the withdrawal cannot complete until Aave unpauses.

**`setAaveIntegrationEnabled(false)` — disable path is blocked:** [4](#0-3) 
The `isAaveIntegrationEnabled = enabled` assignment at L503 is only reached after `_collectInterestToTreasury()` and `_withdrawFromAave(aaveBalance)` both succeed. With Aave paused, neither succeeds, so `isAaveIntegrationEnabled` remains `true`.

**`emergencyWithdrawFromAave` — designated emergency exit is equally blocked:** [5](#0-4) 
The function requires `isAaveIntegrationEnabled == true` (which it is, since the disable path is blocked), then calls `_collectInterestToTreasury()` and `_withdrawFromAave(amount)` — both of which revert when Aave is paused.

**Contrast with deposit path — try/catch is used there but not here:** [6](#0-5) 
`depositToAaveExternal` exists specifically to enable try/catch wrapping in `unlockQueue`, demonstrating the protocol already recognizes that Aave calls can fail. No equivalent protection exists for any withdrawal-direction Aave call.

## Impact Explanation
**Medium — Temporary freezing of user ETH withdrawal funds.** Any ETH withdrawal request that requires pulling funds from Aave cannot be completed while the Aave pool is paused. The user's request is not destroyed (the transaction reverts atomically), but the funds are inaccessible for the full duration of the pause. This matches the allowed impact "Medium. Temporary freezing of funds." The freeze is bounded by the Aave pause duration and does not result in permanent loss, ruling out Critical.

## Likelihood Explanation
Aave V3 has a documented `EMERGENCY_ADMIN` / guardian role that can call `setPoolPause(true)` on the pool contract. Pool-level pauses have occurred historically during exploit responses. The protocol has no control over when or for how long Aave is paused. The preconditions are: (1) `isAaveIntegrationEnabled == true`, (2) ETH has been deposited to Aave (`aaveBalance > 0`), (3) Aave pool is paused, (4) contract idle ETH balance < user withdrawal amount. All four are realistic and can occur simultaneously. No attacker action is required — the freeze is triggered by any user calling `completeWithdrawal` under these conditions.

## Recommendation
1. Add a `forceDisableAaveIntegration()` function callable by `PAUSER_ROLE` that sets `isAaveIntegrationEnabled = false` and revokes approvals without attempting any withdrawal — mirroring the pattern already used for deposits. This provides an immediate admin bypass when Aave is paused.
2. Wrap `aaveWETHGateway.withdrawETH` calls in `setAaveIntegrationEnabled(false)` and `emergencyWithdrawFromAave` with try/catch. On failure, allow the disable to proceed (set `isAaveIntegrationEnabled = false`, revoke approvals), leaving the aWETH balance in place to be recovered once Aave unpauses.
3. Apply the same try/catch pattern to `_collectInterestToTreasury()` when called from the disable/emergency paths, since it also calls `withdrawETH` and is invoked before `_withdrawFromAave`.
4. In `_processWithdrawalCompletion`, consider checking whether the Aave pool is paused before calling `_withdrawFromAave`, and if so, reverting with a more informative error or skipping the Aave pull when possible.

## Proof of Concept
```solidity
// Foundry fork test (mainnet fork)
// 1. Deploy/configure LRTWithdrawalManager with live Aave V3 addresses
// 2. Operator calls depositIdleETHToAave() → aaveBalance > 0
// 3. User queues and unlocks an ETH withdrawal request
// 4. Simulate Aave guardian pausing the pool:
//    vm.prank(AAVE_EMERGENCY_ADMIN);
//    IPool(AAVE_POOL).setPoolPause(true);
// 5. Set contract idle ETH balance < request.expectedAssetAmount
//    (e.g., drain idle ETH or use a request larger than idle balance)
// 6. User calls completeWithdrawal(ETH, referralId) → assert revert
// 7. LRT manager calls setAaveIntegrationEnabled(false) → assert revert
// 8. PAUSER_ROLE calls emergencyWithdrawFromAave(type(uint256).max) → assert revert
// 9. Confirm no unblocking path exists without Aave unpausing or proxy upgrade
//    vm.prank(AAVE_EMERGENCY_ADMIN);
//    IPool(AAVE_POOL).setPoolPause(false);
// 10. User retries completeWithdrawal → succeeds, confirming temporary (not permanent) freeze
```

### Citations

**File:** contracts/LRTWithdrawalManager.sol (L486-503)
```text
        if (!enabled) {
            uint256 aaveBalance = aaveAWETH.balanceOf(address(this));
            if (aaveBalance > 0) {
                // First collect any accrued interest to treasury
                _collectInterestToTreasury();

                // Then withdraw remaining principal from Aave back to contract
                aaveBalance = aaveAWETH.balanceOf(address(this));
                if (aaveBalance > 0) {
                    _withdrawFromAave(aaveBalance);
                }
            }

            // Revoke approval for aWETH token to Aave WETH Gateway
            _revokeApprovalToAaveWETHGateway();
        }

        isAaveIntegrationEnabled = enabled;
```

**File:** contracts/LRTWithdrawalManager.sol (L507-516)
```text
    /// @notice External wrapper for depositing to Aave (used for try/catch in `unlockQueue`)
    /// @param amount Amount of ETH to deposit
    /// @dev Intentionally NOT `nonReentrant`. `unlockQueue()` is `nonReentrant` and calls this via an external
    ///      self-call (`this.depositToAaveExternal`) to enable try/catch. Marking this as `nonReentrant` would
    ///      make that path always revert due to the shared ReentrancyGuard status. Safety is enforced by
    ///     `msg.sender == address(this)` check.
    function depositToAaveExternal(uint256 amount) external {
        if (msg.sender != address(this)) revert UnauthorizedCaller();
        _depositToAave(amount);
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L551-563)
```text
    function emergencyWithdrawFromAave(uint256 amount) external nonReentrant onlyRole(LRTConstants.PAUSER_ROLE) {
        if (!isAaveIntegrationEnabled) revert AaveIntegrationNotEnabled();

        uint256 aaveBalance = aaveAWETH.balanceOf(address(this));
        if (aaveBalance == 0) revert InsufficientAaveBalance();

        // First collect any accrued interest to treasury
        _collectInterestToTreasury();

        uint256 withdrawnAmount = _withdrawFromAave(amount);

        emit EmergencyWithdrawFromAave(withdrawnAmount, address(this));
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L719-731)
```text
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
```

**File:** contracts/LRTWithdrawalManager.sol (L905-917)
```text
    function _withdrawFromAave(uint256 amount) internal returns (uint256 withdrawnAmount) {
        if (amount == 0) return 0;

        uint256 aaveBalance = aaveAWETH.balanceOf(address(this));
        if (aaveBalance == 0) revert InsufficientAaveBalance();

        // Only withdraw up to the principal amount (don't use accrued interest for user withdrawals)
        uint256 withdrawablePrincipal = aaveBalance < totalETHDepositedToAave ? aaveBalance : totalETHDepositedToAave;

        withdrawnAmount = amount > withdrawablePrincipal ? withdrawablePrincipal : amount;
        if (withdrawnAmount == 0) return 0;

        aaveWETHGateway.withdrawETH(aavePool, withdrawnAmount, address(this));
```

**File:** contracts/LRTWithdrawalManager.sol (L945-954)
```text
    function _collectInterestToTreasury() internal returns (uint256 interestAmount) {
        uint256 aaveBalance = aaveAWETH.balanceOf(address(this));
        uint256 principal = totalETHDepositedToAave;

        // Return 0 if no interest or balance is less than principal (accounting for rounding)
        if (aaveBalance <= principal) return 0;

        interestAmount = aaveBalance - principal;

        aaveWETHGateway.withdrawETH(aavePool, interestAmount, address(this));
```
