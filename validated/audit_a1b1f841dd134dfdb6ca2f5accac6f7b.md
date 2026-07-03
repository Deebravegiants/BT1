The code confirms the claim. Key findings:

- `rsETHPrice` is declared as `uint256 public override rsETHPrice;` at line 28 of `LRTOracle.sol` — default value `0`.
- `LRTOracle.initialize()` (lines 64–68) does **not** call `_updateRsETHPrice()`, leaving `rsETHPrice == 0` post-deployment.
- `getRsETHAmountToMint()` at line 520 of `LRTDepositPool.sol` divides by `lrtOracle.rsETHPrice()` with no zero-guard.
- `_beforeDeposit()` (line 665) calls `getRsETHAmountToMint()` unconditionally.
- Both `depositETH()` and `depositAsset()` call `_beforeDeposit()` — all deposits revert until `updateRSETHPrice()` is called.
- `updateRSETHPrice()` is public but never called automatically during initialization.

The impact is concrete (all deposits revert with a division-by-zero panic), reachable by any unprivileged user, and matches the "Temporary freezing of funds" (Medium) allowed impact.

---

Audit Report

## Title
Division by Zero in `getRsETHAmountToMint` Blocks All Deposits When `rsETHPrice` Is Uninitialized — (`contracts/LRTDepositPool.sol`)

## Summary
`LRTDepositPool.getRsETHAmountToMint()` divides by `lrtOracle.rsETHPrice()` without a zero-guard. `rsETHPrice` in `LRTOracle` defaults to `0` and is never set during `initialize()`. Any call to `depositETH()` or `depositAsset()` before `updateRSETHPrice()` has been called will revert with a division-by-zero panic, completely blocking all deposit functionality.

## Finding Description
`LRTOracle` declares `uint256 public override rsETHPrice;` at line 28, which defaults to `0`. The `initialize()` function (lines 64–68) only sets `lrtConfig` and emits an event — it never calls `_updateRsETHPrice()`. The only way `rsETHPrice` becomes non-zero is via `updateRSETHPrice()` (line 87, public) or `updateRSETHPriceAsManager()` (line 94, manager-only), neither of which is called automatically.

`LRTDepositPool.getRsETHAmountToMint()` at line 520 computes:
```solidity
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```
with no check that `lrtOracle.rsETHPrice() != 0`. This function is called unconditionally by `_beforeDeposit()` at line 665, which is called by both `depositETH()` (line 87) and `depositAsset()` (line 111). No caller in this chain checks whether `rsETHPrice` is zero before the division executes.

## Impact Explanation
All deposit paths (`depositETH`, `depositAsset`) are completely blocked from the moment of deployment until `updateRSETHPrice()` is called. This constitutes a **temporary freezing of funds** (Medium): users cannot deposit ETH or LSTs into the protocol, and the core deposit functionality is entirely unavailable during this window.

## Likelihood Explanation
The vulnerable window opens at deployment and closes only when `updateRSETHPrice()` is first called. Since `updateRSETHPrice()` is public, any user can call it to unblock deposits — but the protocol provides no enforcement or guarantee that this happens before deposits are attempted. The scenario is directly reproducible on any fresh deployment or state-resetting upgrade, requiring no privileged access and no attacker action beyond simply attempting a deposit.

## Recommendation
Add a zero-guard in `getRsETHAmountToMint()` before the division:
```solidity
uint256 currentRsETHPrice = lrtOracle.rsETHPrice();
if (currentRsETHPrice == 0) revert RsETHPriceNotInitialized();
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / currentRsETHPrice;
```
Alternatively, call `_updateRsETHPrice()` (or `updateRSETHPrice()`) as part of `LRTOracle.initialize()` so `rsETHPrice` is always non-zero when the contract is live.

## Proof of Concept
1. Deploy `LRTOracle` and `LRTDepositPool` on a local fork. Confirm `rsETHPrice == 0` (Solidity default, `initialize()` does not set it).
2. Do **not** call `updateRSETHPrice()`.
3. Call `depositETH{value: 1 ether}(0, "")` as any EOA.
4. Execution flows: `depositETH` → `_beforeDeposit` (line 665) → `getRsETHAmountToMint` (line 520) → `(amount * assetPrice) / 0` → EVM division-by-zero panic, revert.
5. Repeat for `depositAsset` — same result.
6. Call `updateRSETHPrice()` from any account. Confirm `rsETHPrice == 1 ether` (since `rsethSupply == 0`). Retry deposit — succeeds.

Foundry test sketch:
```solidity
function test_depositRevertsWhenRsETHPriceUninitialized() public {
    // fresh deployment, rsETHPrice == 0
    assertEq(lrtOracle.rsETHPrice(), 0);
    vm.expectRevert(); // division-by-zero panic
    lrtDepositPool.depositETH{value: 1 ether}(0, "");
    // unblock
    lrtOracle.updateRSETHPrice();
    assertEq(lrtOracle.rsETHPrice(), 1 ether);
    // deposit now succeeds
    lrtDepositPool.depositETH{value: 1 ether}(0, "");
}
```