Audit Report

## Title
Missing Try/Catch on `_withdrawFromAave()` Causes Temporary Fund Freeze During Aave Pool Pause - (`contracts/LRTWithdrawalManager.sol`)

## Summary

`_processWithdrawalCompletion()` calls `_withdrawFromAave()` at line 724 without any error handling. When the Aave v3 pool is paused, the underlying `aaveWETHGateway.withdrawETH()` call reverts, causing all `completeWithdrawal()` calls that require Aave liquidity to revert. Because rsETH is already burned in the prior `unlockQueue()` step (line 305), affected users cannot recover their rsETH and cannot claim their ETH for the duration of the pause.

## Finding Description

The ETH withdrawal lifecycle splits across two transactions:

1. **`unlockQueue()`** (lines 301–317): burns rsETH from the contract (`burnFrom` at line 305), redeems ETH from the vault, then attempts to deposit to Aave using a `try/catch` (lines 311–316). If the Aave deposit fails, funds remain in the contract and the function continues normally.

2. **`completeWithdrawal()` → `_processWithdrawalCompletion()`** (lines 699–738): if the contract's native ETH balance is below `request.expectedAssetAmount`, it calls `_withdrawFromAave(amountNeeded)` at line 724 with no error handling.

`_withdrawFromAave()` (lines 905–921) calls `aaveWETHGateway.withdrawETH(aavePool, withdrawnAmount, address(this))` at line 917 directly. When the Aave v3 pool is paused, this external call reverts unconditionally. There is no `try/catch` and no fallback path. The entire `completeWithdrawal()` transaction reverts.

The asymmetry is explicit: the deposit side (line 311) uses `try this.depositToAaveExternal(...) {} catch (bytes memory reason) { emit AaveDepositFailed(...); }`, while the withdrawal side (line 724) uses a bare `_withdrawFromAave(amountNeeded)` call. The same defensive pattern was deliberately applied to deposits but omitted for withdrawals.

The `emergencyWithdrawFromAave()` escape hatch (lines 551–563) also calls `_withdrawFromAave()` at line 560 and would equally revert while the pool is paused, eliminating the operator's ability to unblock the situation during the pause.

## Impact Explanation

**Temporary freezing of funds (Medium).** Users whose ETH withdrawal requests were unlocked (rsETH already burned) while ETH was held in Aave cannot call `completeWithdrawal()` for the duration of the Aave pool pause. Their rsETH is gone and cannot be re-minted; the ETH is inaccessible until the pool is unpaused. This directly matches the "Temporary freezing of funds" impact class.

## Likelihood Explanation

The Aave v3 guardian has paused pools on mainnet in response to real security incidents. The Aave integration is an explicit, enabled feature of this protocol (`isAaveIntegrationEnabled`). Any user whose withdrawal was unlocked while ETH was deposited to Aave is affected for the full duration of the pause. No attacker action is required — the condition arises from normal Aave guardian operations. The affected user is an ordinary withdrawer calling a public function.

## Recommendation

Apply the same `try/catch` pattern used for deposits to the `_withdrawFromAave` call in `_processWithdrawalCompletion()`. If the Aave withdrawal fails, the function should skip it and revert with `InsufficientLiquidityForWithdrawal` only if the contract balance is still insufficient:

```diff
 if (isAaveIntegrationEnabled && asset == LRTConstants.ETH_TOKEN) {
     uint256 contractBalance = address(this).balance;
     if (contractBalance < request.expectedAssetAmount) {
         uint256 amountNeeded = request.expectedAssetAmount - contractBalance;
-        _withdrawFromAave(amountNeeded);
+        try this.withdrawFromAaveExternal(amountNeeded) { } catch { }
         uint256 balanceAfter = address(this).balance;
         if (balanceAfter < request.expectedAssetAmount) {
             revert InsufficientLiquidityForWithdrawal();
         }
     }
 }
```

This mirrors the `depositToAaveExternal` pattern and ensures a paused Aave pool causes a clean, retryable revert rather than a state where the user's rsETH is burned but ETH is permanently inaccessible during the pause.

## Proof of Concept

1. Deploy with Aave integration enabled; ETH is deposited to Aave via `unlockQueue()` (`totalETHDepositedToAave > 0`).
2. Operator calls `unlockQueue(ETH_TOKEN, ...)` — rsETH is burned at line 305, withdrawal requests are unlocked.
3. Aave guardian pauses the Aave v3 pool (standard mainnet-exercised action).
4. User calls `completeWithdrawal(ETH_TOKEN, ...)`.
5. `_processWithdrawalCompletion()` evaluates `address(this).balance < request.expectedAssetAmount` → true (ETH is in Aave).
6. `_withdrawFromAave(amountNeeded)` is called at line 724.
7. `aaveWETHGateway.withdrawETH(aavePool, ...)` at line 917 reverts because the pool is paused.
8. The entire transaction reverts. The user's rsETH is already burned (step 2) and cannot be recovered. ETH remains locked in Aave until the pool is unpaused.

Foundry fork test: fork mainnet at a block where the Aave v3 pool is paused (or mock `aaveWETHGateway.withdrawETH` to revert), set `isAaveIntegrationEnabled = true`, seed `totalETHDepositedToAave`, call `unlockQueue` then `completeWithdrawal`, and assert the transaction reverts while the user's rsETH balance remains zero.