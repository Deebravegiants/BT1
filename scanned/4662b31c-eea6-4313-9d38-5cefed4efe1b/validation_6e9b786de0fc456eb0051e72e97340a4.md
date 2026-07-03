### Title
DoS on `completeWithdrawal` When Aave Pool Is Paused or Has Insufficient Liquidity - (File: `contracts/LRTWithdrawalManager.sol`)

### Summary
When the Aave integration is enabled in `LRTWithdrawalManager`, the user-callable `completeWithdrawal` function internally calls `_withdrawFromAave` to retrieve ETH from Aave if the contract's own balance is insufficient. Unlike `unlockQueue`, which wraps its Aave deposit call in a try/catch, `_processWithdrawalCompletion` has no such protection for the Aave withdrawal call. If Aave's pool is paused or has insufficient liquidity, `aaveWETHGateway.withdrawETH` reverts, causing `completeWithdrawal` to revert and temporarily freezing user ETH withdrawals.

### Finding Description
In `_processWithdrawalCompletion`, when Aave integration is enabled and the contract's ETH balance is below the user's expected withdrawal amount, the code calls `_withdrawFromAave` to cover the shortfall:

```solidity
// LRTWithdrawalManager.sol lines 720–732
if (isAaveIntegrationEnabled && asset == LRTConstants.ETH_TOKEN) {
    uint256 contractBalance = address(this).balance;
    if (contractBalance < request.expectedAssetAmount) {
        uint256 amountNeeded = request.expectedAssetAmount - contractBalance;
        _withdrawFromAave(amountNeeded);          // <-- no try/catch
        uint256 balanceAfter = address(this).balance;
        if (balanceAfter < request.expectedAssetAmount) {
            revert InsufficientLiquidityForWithdrawal();
        }
    }
}
```

`_withdrawFromAave` calls `aaveWETHGateway.withdrawETH` directly:

```solidity
// LRTWithdrawalManager.sol lines 905–921
function _withdrawFromAave(uint256 amount) internal returns (uint256 withdrawnAmount) {
    ...
    aaveWETHGateway.withdrawETH(aavePool, withdrawnAmount, address(this)); // reverts if Aave paused
    ...
}
```

Aave v3 enforces a global pause on its pool; any withdrawal call while the pool is paused reverts. High WETH utilization can also cause `withdrawETH` to revert due to insufficient liquidity.

The developers already recognized this class of failure for Aave *deposits* in `unlockQueue` and wrapped that call in a try/catch:

```solidity
// LRTWithdrawalManager.sol lines 310–317
try this.depositToAaveExternal(assetAmountUnlocked) { }
catch (bytes memory reason) {
    emit AaveDepositFailed(assetAmountUnlocked, reason);
    // Silently fail if Aave deposit fails (e.g., pool at max capacity)
}
```

No equivalent protection exists for the withdrawal path in `_processWithdrawalCompletion`. When Aave integration is active, most idle ETH is deposited to Aave, so the contract's own ETH balance is typically low, making the Aave withdrawal path the critical dependency for every user completing an ETH withdrawal.

### Impact Explanation
Users who have already initiated an ETH withdrawal (burning rsETH via `initiateWithdrawal`) cannot complete their withdrawal via `completeWithdrawal` while Aave is paused or illiquid. Their ETH is temporarily frozen in the protocol until Aave's state normalises. This matches **Medium — Temporary freezing of funds**.

### Likelihood Explanation
Aave v3 has a guardian-controlled pause mechanism that has been exercised historically. Additionally, during market stress events, WETH utilization in Aave can spike to near 100%, making withdrawals impossible. When `isAaveIntegrationEnabled` is true, the `unlockQueue` flow deposits unlocked ETH into Aave, making the contract structurally dependent on Aave for every subsequent `completeWithdrawal` call. Likelihood is **Medium**.

### Recommendation
Wrap the `_withdrawFromAave` call inside `_processWithdrawalCompletion` in a try/catch, mirroring the pattern already used in `unlockQueue`. If the Aave withdrawal fails, revert with a descriptive error (e.g., `AaveWithdrawalFailed`) so users and operators know to retry once Aave is operational, rather than silently blocking all ETH withdrawal completions.

```solidity
try this.withdrawFromAaveExternal(amountNeeded) {
} catch {
    revert AaveWithdrawalFailed();
}
```

Alternatively, add a view function that checks Aave's pause status and available liquidity before attempting the withdrawal, and surface a clear revert reason.

### Proof of Concept
1. `isAaveIntegrationEnabled` is `true`; most idle ETH has been deposited to Aave via `unlockQueue` / `depositIdleETHToAave`.
2. User calls `initiateWithdrawal(ETH_TOKEN, rsETHAmount, ...)`, burning rsETH; withdrawal is queued.
3. Operator calls `unlockQueue` to unlock the request; ETH is redeemed from `LRTUnstakingVault` and deposited to Aave.
4. Aave's pool is paused (or WETH utilization is ~100%).
5. User calls `completeWithdrawal(ETH_TOKEN, ...)`.
6. `_processWithdrawalCompletion` detects `address(this).balance < request.expectedAssetAmount`.
7. `_withdrawFromAave(amountNeeded)` is called → `aaveWETHGateway.withdrawETH(...)` reverts.
8. `completeWithdrawal` reverts; user cannot retrieve their ETH.