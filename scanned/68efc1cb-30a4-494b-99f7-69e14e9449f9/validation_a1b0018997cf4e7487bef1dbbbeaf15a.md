### Title
Aave WETH Pool at 100% Utilization Permanently Blocks ETH `completeWithdrawal` - (File: contracts/LRTWithdrawalManager.sol)

### Summary

`LRTWithdrawalManager` deposits idle ETH into Aave v3 to earn yield. When users call `completeWithdrawal()` for ETH and the contract's direct balance is insufficient, it calls `_withdrawFromAave()`, which unconditionally calls `aaveWETHGateway.withdrawETH()`. If the Aave v3 WETH pool is at or near 100% utilization (all WETH borrowed), this external call reverts, causing the entire `completeWithdrawal()` transaction to revert. Users whose rsETH was already burned during `unlockQueue()` cannot retrieve their ETH.

### Finding Description

The `LRTWithdrawalManager` integrates with Aave v3 to earn yield on ETH held between `unlockQueue()` and `completeWithdrawal()`. During `unlockQueue()`, rsETH is burned and ETH is moved from `LRTUnstakingVault` into `LRTWithdrawalManager`, then optionally deposited into Aave via `depositToAaveExternal()`.

When a user calls `completeWithdrawal()` for ETH, `_processWithdrawalCompletion()` is invoked. If `isAaveIntegrationEnabled` is true and the contract's direct ETH balance is less than `request.expectedAssetAmount`, it calls `_withdrawFromAave(amountNeeded)`:

```solidity
// contracts/LRTWithdrawalManager.sol:720-731
if (isAaveIntegrationEnabled && asset == LRTConstants.ETH_TOKEN) {
    uint256 contractBalance = address(this).balance;
    if (contractBalance < request.expectedAssetAmount) {
        uint256 amountNeeded = request.expectedAssetAmount - contractBalance;
        _withdrawFromAave(amountNeeded);
        uint256 balanceAfter = address(this).balance;
        if (balanceAfter < request.expectedAssetAmount) {
            revert InsufficientLiquidityForWithdrawal();
        }
    }
}
```

`_withdrawFromAave()` unconditionally calls:

```solidity
// contracts/LRTWithdrawalManager.sol:917
aaveWETHGateway.withdrawETH(aavePool, withdrawnAmount, address(this));
```

Aave v3 only allows withdrawals up to the difference between total supply and total debt (available liquidity). If WETH utilization is at 100%, `withdrawETH` reverts at the Aave protocol level. There is no try/catch, no fallback to idle ETH, and no graceful degradation — the entire `completeWithdrawal()` call reverts.

This is structurally identical to the reference report: a mandatory external protocol call during a user-facing withdrawal path, with no fallback when that external protocol is at 100% utilization.

### Impact Explanation

**Medium — Temporary freezing of funds.**

Users who have already had their withdrawal requests unlocked (rsETH burned in `unlockQueue()`) cannot complete their ETH withdrawals for as long as Aave WETH utilization remains at or near 100%. Their rsETH is already gone (burned), and their ETH is locked in Aave. The freeze persists until Aave utilization drops below 100%, which can be delayed intentionally by an attacker.

### Likelihood Explanation

**Medium likelihood.** Two scenarios:

1. **Organic:** Aave v3 WETH utilization has historically spiked to near 100% during periods of high demand (e.g., ETH staking yield spikes, market volatility). This can occur without any attacker.
2. **Intentional attack:** An attacker deposits collateral into Aave v3 and borrows all available WETH, driving utilization to 100%. The cost is the borrow interest rate, which is economically feasible for a griefing attack. The attacker need not profit directly — they may be a competing protocol or a large position holder wanting to delay withdrawals.

Pre-conditions:
- `isAaveIntegrationEnabled == true`
- `totalETHDepositedToAave > 0`
- Contract's direct ETH balance < user's `expectedAssetAmount`
- Aave WETH pool utilization at ~100%

### Recommendation

Wrap the `_withdrawFromAave()` call in `_processWithdrawalCompletion()` with a try/catch or a pre-check of available Aave liquidity before attempting withdrawal. If Aave liquidity is insufficient, the function should either:
1. Transfer whatever ETH is available directly from the contract balance and defer the remainder, or
2. Revert with a specific error that does **not** consume the user's nonce (i.e., restore `userAssociatedNonces` before reverting), so the user can retry later.

Additionally, the `_collectInterestToTreasury()` function at line 954 also calls `aaveWETHGateway.withdrawETH()` without a try/catch, which would block `emergencyWithdrawFromAave()` and `setAaveIntegrationEnabled(false)` under the same conditions.

### Proof of Concept

1. Protocol operator enables Aave integration and deposits ETH into Aave via `unlockQueue()` → `depositToAaveExternal()`.
2. User calls `initiateWithdrawal(ETH, rsETHAmount, ...)` — rsETH is transferred to the contract.
3. Operator calls `unlockQueue(ETH, ...)` — rsETH is burned, ETH is redeemed from `LRTUnstakingVault` into `LRTWithdrawalManager`, then deposited into Aave.
4. Attacker deposits collateral into Aave v3 and borrows all available WETH, bringing utilization to ~100%.
5. User calls `completeWithdrawal(ETH, ...)`.
6. `_processWithdrawalCompletion()` detects `address(this).balance < request.expectedAssetAmount` and calls `_withdrawFromAave(amountNeeded)`.
7. `aaveWETHGateway.withdrawETH(aavePool, withdrawnAmount, address(this))` reverts because Aave has no available WETH liquidity.
8. The entire `completeWithdrawal()` transaction reverts. The user's nonce was already popped from `userAssociatedNonces` at line 705 — **the request is deleted but ETH is not transferred**, permanently losing the user's place in the queue and blocking their withdrawal. [1](#0-0) [2](#0-1) [3](#0-2)

### Citations

**File:** contracts/LRTWithdrawalManager.sol (L700-712)
```text
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
