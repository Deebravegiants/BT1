### Title
Aave v3 Pool Pause Causes Permanent DOS of `completeWithdrawal` for ETH Withdrawers - (File: contracts/LRTWithdrawalManager.sol)

### Summary

`LRTWithdrawalManager._processWithdrawalCompletion` unconditionally calls `_withdrawFromAave` when the Aave integration is enabled and the contract's ETH balance is insufficient to cover a user's withdrawal. `_withdrawFromAave` calls `aaveWETHGateway.withdrawETH` with no error handling. Aave v3 pools can be paused by Aave governance, and when paused, `withdrawETH` reverts. This DOS's `completeWithdrawal` for all ETH withdrawers whose funds are held in Aave, at a point when their rsETH has already been burned.

### Finding Description

The `LRTWithdrawalManager` integrates with Aave v3 to earn yield on idle ETH held between `unlockQueue` and `completeWithdrawal`. The lifecycle is:

1. User calls `initiateWithdrawal` — rsETH is transferred to the contract.
2. Operator calls `unlockQueue` — rsETH is burned, ETH is pulled from `LRTUnstakingVault`, then deposited to Aave via `try this.depositToAaveExternal(assetAmountUnlocked)`.
3. User calls `completeWithdrawal` — must retrieve ETH from Aave to pay the user.

In step 3, `_processWithdrawalCompletion` checks whether the contract's native ETH balance covers the request. If not (the common case when Aave integration is active), it calls `_withdrawFromAave`:

```solidity
// LRTWithdrawalManager.sol lines 720-731
if (isAaveIntegrationEnabled && asset == LRTConstants.ETH_TOKEN) {
    uint256 contractBalance = address(this).balance;
    if (contractBalance < request.expectedAssetAmount) {
        uint256 amountNeeded = request.expectedAssetAmount - contractBalance;
        _withdrawFromAave(amountNeeded);   // <-- no try/catch
        ...
    }
}
```

`_withdrawFromAave` calls:

```solidity
// LRTWithdrawalManager.sol line 917
aaveWETHGateway.withdrawETH(aavePool, withdrawnAmount, address(this));
```

Aave v3 enforces a pool-level pause. When the pool is paused, `withdrawETH` reverts unconditionally. There is no `try/catch` around this call, so the revert propagates all the way up through `completeWithdrawal`.

**Critical asymmetry**: The deposit path in `unlockQueue` (line 311) wraps `depositToAaveExternal` in a `try/catch` and silently continues on failure. The withdrawal path has no equivalent protection.

**No admin escape hatch works while Aave is paused**:
- `emergencyWithdrawFromAave` (line 551-563) also calls `_withdrawFromAave` → reverts.
- `setAaveIntegrationEnabled(false)` (lines 486-497) also calls `_withdrawFromAave` before disabling → reverts.
- `configureAaveIntegration` (lines 438-453) also calls `_withdrawFromAave` → reverts.

There is no code path that allows the protocol to bypass the Aave withdrawal and pay users from an alternative source while Aave is paused.

### Impact Explanation

**Medium — Temporary freezing of funds.**

Users whose rsETH has already been burned by `unlockQueue` cannot complete their ETH withdrawals for the duration of the Aave pause. Their rsETH is gone and their ETH is locked in Aave with no protocol-level fallback. If the Aave pause is extended or the market is deprecated, this becomes a permanent freeze.

### Likelihood Explanation

Aave v3 has a well-documented pool-level and reserve-level pause mechanism exercised by Aave governance and the Aave Guardian. The WETH market on Aave v3 Ethereum is one of the largest markets and has been subject to emergency pauses in the past (e.g., during the Euler hack contagion period). The Aave integration is an opt-in feature that, once enabled, routes all unlocked ETH into Aave, making the scenario realistic whenever the integration is active.

### Recommendation

Wrap the `_withdrawFromAave` call inside `_processWithdrawalCompletion` in a `try/catch` (or equivalent low-level call pattern). On failure, fall back to paying the user from whatever native ETH balance is available, and record the shortfall for later settlement. Alternatively, add a separate admin function that can force-set `isAaveIntegrationEnabled = false` **without** attempting to withdraw from Aave first, so that the protocol can degrade gracefully when Aave is paused and users can be paid once ETH is manually recovered.

### Proof of Concept

1. Aave integration is enabled; ETH is deposited to Aave via `unlockQueue`.
2. Aave governance pauses the WETH pool (a realistic, documented event).
3. User calls `completeWithdrawal(ETH_TOKEN, ...)`.
4. `_processWithdrawalCompletion` sees `address(this).balance < request.expectedAssetAmount` and calls `_withdrawFromAave`.
5. `_withdrawFromAave` calls `aaveWETHGateway.withdrawETH(aavePool, ...)` at line 917.
6. Aave's pool reverts because the pool is paused.
7. The entire `completeWithdrawal` transaction reverts.
8. The user's rsETH is already burned (step 1 of the lifecycle). They cannot recover their ETH.
9. `emergencyWithdrawFromAave` (line 551) and `setAaveIntegrationEnabled(false)` (line 469) both also call `_withdrawFromAave` and also revert — no admin escape hatch is available.

**Relevant code locations:** [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

### Citations

**File:** contracts/LRTWithdrawalManager.sol (L309-316)
```text
        // If Aave integration is enabled and asset is ETH, deposit to Aave
        if (isAaveIntegrationEnabled && asset == LRTConstants.ETH_TOKEN && assetAmountUnlocked > 0) {
            try this.depositToAaveExternal(assetAmountUnlocked) { }
            catch (bytes memory reason) {
                emit AaveDepositFailed(assetAmountUnlocked, reason);
                // Silently fail if Aave deposit fails (e.g., pool at max capacity)
                // Funds remain in contract for withdrawals
            }
```

**File:** contracts/LRTWithdrawalManager.sol (L486-497)
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

**File:** contracts/LRTWithdrawalManager.sol (L905-921)
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
        totalETHDepositedToAave -= withdrawnAmount;

        emit ETHWithdrawnFromAave(withdrawnAmount, totalETHDepositedToAave);
    }
```
