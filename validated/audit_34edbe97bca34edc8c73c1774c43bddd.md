Audit Report

## Title
Uninitialized `rsETHPrice` in `LRTOracle` Causes Division-by-Zero on All Deposit Calls - (File: contracts/LRTOracle.sol)

## Summary
`LRTOracle.initialize()` sets only `lrtConfig` and emits an event, leaving `rsETHPrice` at the Solidity default of `0`. Every deposit path in `LRTDepositPool` calls `getRsETHAmountToMint()`, which divides by `lrtOracle.rsETHPrice()`. Until `updateRSETHPrice()` is explicitly called, all deposits revert with a division-by-zero panic. No user funds are lost, but the protocol cannot accept deposits during this window.

## Finding Description
`LRTOracle.initialize()` at lines 64–68 of `contracts/LRTOracle.sol` only assigns `lrtConfig` and emits `UpdatedLRTConfig`; it never assigns `rsETHPrice`. The storage variable declared at line 28 therefore remains `0` after initialization.

`LRTDepositPool.getRsETHAmountToMint()` at line 520 of `contracts/LRTDepositPool.sol` computes:
```solidity
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```
This is called unconditionally from `_beforeDeposit()` (line 665), which is invoked by both `depositETH()` (line 87) and `depositAsset()` (line 111). With `rsETHPrice == 0`, the EVM raises a division-by-zero panic and reverts every deposit.

`_updateRsETHPrice()` at lines 218–222 does set `rsETHPrice = 1 ether` when `rsethSupply == 0`, but only when explicitly triggered. `updateRSETHPrice()` at line 87–89 is `public whenNotPaused`, so any caller can invoke it — but until someone does, the division-by-zero is live. No existing guard in the deposit path checks for a zero `rsETHPrice` before dividing.

## Impact Explanation
Between contract deployment (or any proxy upgrade that resets storage) and the first call to `updateRSETHPrice()`, every call to `depositETH()` or `depositAsset()` reverts. No deposited funds are at risk because the revert prevents any state change, but the protocol fails to deliver its core promised service. This matches the allowed impact: **Low — Contract fails to deliver promised returns, but doesn't lose value.**

## Likelihood Explanation
The window is present on every fresh deployment or storage-resetting upgrade. Because `updateRSETHPrice()` is permissionless, any user who encounters the revert can self-remediate immediately by calling it directly. The window is short in practice but is a real, reachable failure mode for any depositor who acts before the price is seeded. No special privileges or attacker capability are required to trigger it.

## Recommendation
Initialize `rsETHPrice` (and `highestRsethPrice`) to `1 ether` inside `LRTOracle.initialize()`, mirroring the logic already present in `_updateRsETHPrice()` for the zero-supply case:

```solidity
function initialize(address lrtConfigAddr) external initializer {
    UtilLib.checkNonZeroAddress(lrtConfigAddr);
    lrtConfig = ILRTConfig(lrtConfigAddr);
+   rsETHPrice = 1 ether;
+   highestRsethPrice = 1 ether;
    emit UpdatedLRTConfig(lrtConfigAddr);
}
```

## Proof of Concept
1. Deploy `LRTOracle` proxy and call `initialize(lrtConfigAddr)`. `rsETHPrice` is `0`.
2. Do **not** call `updateRSETHPrice()`.
3. Call `LRTDepositPool.depositETH{value: 1 ether}(0, "")`.
4. Execution reaches `getRsETHAmountToMint()` → `(1e18 * assetPrice) / 0` → EVM division-by-zero panic → revert.
5. Call `updateRSETHPrice()` (permissionless, no role required). `rsETHPrice` is now `1 ether`.
6. Repeat step 3 — deposit succeeds.

A Foundry test can reproduce this by deploying the proxy, skipping the `updateRSETHPrice()` call, asserting that `depositETH` reverts with a `Panic(0x12)` error, then calling `updateRSETHPrice()` and asserting the subsequent deposit succeeds.