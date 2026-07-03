Audit Report

## Title
Missing Try/Catch on `_withdrawFromAave` and No Force-Disable Escape Hatch Permanently Blocks ETH Withdrawal Completion When Aave WETH Reserve Is Inactive - (File: `contracts/LRTWithdrawalManager.sol`)

## Summary

When `isAaveIntegrationEnabled` is `true` and ETH has been deposited to Aave, any deactivation of the Aave WETH reserve (`isActive=false`) causes every call to `completeWithdrawal(ETH_TOKEN, ...)` to revert. Unlike the deposit path, the withdrawal path wraps `_withdrawFromAave` in no try/catch. Every admin recovery function (`emergencyWithdrawFromAave`, `setAaveIntegrationEnabled(false)`) also routes through the same failing `_withdrawFromAave` call, leaving all queued ETH withdrawal funds frozen with zero protocol recourse until Aave governance re-activates the reserve.

## Finding Description

**Root cause — asymmetric defensive coding between deposit and withdrawal paths:**

The `unlockQueue` deposit path wraps its Aave interaction in a try/catch, explicitly tolerating Aave unavailability:

```solidity
// L310-317
try this.depositToAaveExternal(assetAmountUnlocked) { }
catch (bytes memory reason) {
    emit AaveDepositFailed(assetAmountUnlocked, reason);
}
```

No equivalent pattern exists on the withdrawal side. In `_processWithdrawalCompletion` (L719-731), when `isAaveIntegrationEnabled && asset == ETH_TOKEN` and the contract's native ETH balance is insufficient, `_withdrawFromAave` is called bare with no try/catch:

```solidity
// L720-731
if (isAaveIntegrationEnabled && asset == LRTConstants.ETH_TOKEN) {
    uint256 contractBalance = address(this).balance;
    if (contractBalance < request.expectedAssetAmount) {
        uint256 amountNeeded = request.expectedAssetAmount - contractBalance;
        _withdrawFromAave(amountNeeded);   // no try/catch
        ...
    }
}
```

`_withdrawFromAave` (L917) calls `aaveWETHGateway.withdrawETH(aavePool, withdrawnAmount, address(this))` with no try/catch. If the Aave WETH reserve is inactive, this call reverts at the Aave pool level, propagating the revert all the way up through `completeWithdrawal`.

**All admin escape hatches are equally broken:**

- `emergencyWithdrawFromAave` (L551-563, `PAUSER_ROLE`): calls `_withdrawFromAave(amount)` directly — same revert path.
- `setAaveIntegrationEnabled(false)` (L486-503, `onlyLRTManager`): calls `_withdrawFromAave(aaveBalance)` at L495 **before** setting `isAaveIntegrationEnabled = false` at L503 — the flag is never cleared.

There is no function in the contract that sets `isAaveIntegrationEnabled = false` without first attempting to drain Aave. Once the reserve is inactive, the protocol is stuck.

**Exploit path:**
1. `isAaveIntegrationEnabled = true`; operator calls `unlockQueue(ETH_TOKEN, ...)` — ETH is redeemed from vault and deposited to Aave via the try/catch-protected path. `address(this).balance == 0`, `aaveAWETH.balanceOf(wm) > 0`.
2. Aave governance sets WETH reserve `isActive = false` (legitimate risk management action).
3. User calls `completeWithdrawal(ETH_TOKEN, "")` — reverts because `_withdrawFromAave` → `aaveWETHGateway.withdrawETH` reverts.
4. `PAUSER_ROLE` calls `emergencyWithdrawFromAave(type(uint256).max)` — same revert.
5. Manager calls `setAaveIntegrationEnabled(false)` — same revert; flag never cleared.
6. No recovery path exists until Aave governance re-activates the reserve.

## Impact Explanation

All queued ETH withdrawal requests where `address(this).balance < request.expectedAssetAmount` become uncompletable for the duration of the Aave reserve deactivation. The funds are not lost (aWETH balances remain), but they are inaccessible to every user in the ETH withdrawal queue simultaneously. This matches **Medium: Temporary freezing of funds**.

## Likelihood Explanation

Aave governance has historically set reserves to `isActive=false` for risk management. The WETH reserve is high-value and unlikely to be deactivated under normal conditions, making this a low-probability event. However, the complete absence of any working recovery path means even a brief deactivation freezes all queued ETH withdrawals with zero protocol recourse. Likelihood: **Low**. Combined with the broad impact across all queued users: **Medium** overall.

## Recommendation

1. **Wrap `_withdrawFromAave` in `_processWithdrawalCompletion` with try/catch**, mirroring the deposit path. On failure, restore state (re-push the nonce, re-increment `unlockedWithdrawalsCount`) and revert with a descriptive error so users can retry later.
2. **Add a force-disable function** (callable by `PAUSER_ROLE` or admin) that sets `isAaveIntegrationEnabled = false` without attempting to withdraw from Aave. This unblocks the withdrawal path immediately; the Aave balance can be recovered separately once the reserve is re-activated.
3. **Check `isActive` via `aaveDataProvider.getReserveConfigurationData`** before any Aave interaction and skip/fallback gracefully if the reserve is inactive.

## Proof of Concept

```solidity
// Fork test on mainnet fork with Aave V3 WETH reserve active.
// 1. Deploy LRTWithdrawalManager with isAaveIntegrationEnabled = true.
// 2. User calls initiateWithdrawal(ETH_TOKEN, rsETHAmount, "").
// 3. Operator calls unlockQueue(ETH_TOKEN, ...) — ETH deposited to Aave (try/catch succeeds).
//    address(withdrawalManager).balance == 0, aaveAWETH.balanceOf(wm) > 0.
// 4. vm.prank(AAVE_ACL_ADMIN);
//    IPoolConfigurator(AAVE_CONFIGURATOR).setReserveActive(WETH, false);
// 5. vm.roll(block.number + withdrawalDelayBlocks + 1);
// 6. vm.expectRevert(); withdrawalManager.completeWithdrawal(ETH_TOKEN, "");
// 7. vm.prank(pauserRole); vm.expectRevert();
//    withdrawalManager.emergencyWithdrawFromAave(type(uint256).max);
// 8. vm.prank(manager); vm.expectRevert();
//    withdrawalManager.setAaveIntegrationEnabled(false);
// All three revert — no recovery path exists.
```