Audit Report

## Title
`_checkAndUpdateDailyFeeMintLimit` Always Reverts When `maxFeeMintAmountPerDay = 0` and Protocol Fee Is Non-Zero — (`contracts/LRTOracle.sol`)

## Summary

When `maxFeeMintAmountPerDay` is at its default value of `0` (never set in `initialize()` or `reinitialize()`) and `protocolFeeInBPS > 0`, any TVL increase causes `_updateRsETHPrice()` to compute a non-zero `rsethAmountToMintAsProtocolFee` and pass it to `_checkAndUpdateDailyFeeMintLimit`. The guard `0 + feeAmount > 0` is always `true`, causing a `DailyFeeMintLimitExceeded` revert on every invocation. Protocol fees are permanently uncollectable and `rsETHPrice` becomes permanently stale until an admin reconfigures `maxFeeMintAmountPerDay`.

## Finding Description

**Root cause — no zero-limit bypass in `_checkAndUpdateDailyFeeMintLimit`:**

```solidity
// contracts/LRTOracle.sol L205-207
if (currentPeriodMintedFeeAmount + feeAmount > maxFeeMintAmountPerDay) {
    revert DailyFeeMintLimitExceeded(currentPeriodMintedFeeAmount + feeAmount, maxFeeMintAmountPerDay);
}
```

When `maxFeeMintAmountPerDay = 0` and `feeAmount > 0`, the condition evaluates to `feeAmount > 0` → always `true` → always reverts. The 24-hour period reset at L199-202 resets `currentPeriodMintedFeeAmount` to `0` each day, but this does not help: the same `0 + feeAmount > 0` condition fires again on the very next call.

**Default state is broken:** `initialize()` (L64-68) sets no value for `maxFeeMintAmountPerDay`, leaving it at the Solidity default of `0`. `reinitialize()` (L72-79) also does not set it. The only way to set it is via `setMaxFeeMintAmountPerDay` (L132-135), which accepts `0` without validation.

**`remainingDailyFeeMintLimit()` treats `0` as valid (L171)** — returning `0` rather than reverting — confirming the protocol considers `0` a valid configuration, but the write path does not mirror this handling.

**Fee computation path (L243-247, L299-303):** When `totalETHInProtocol > previousTVL` and `protocolFeeInBPS > 0`, `protocolFeeInETH` is non-zero. `rsethAmountToMintAsProtocolFee = protocolFeeInETH.divWad(newRsETHPrice)` is non-zero, and `_checkAndUpdateDailyFeeMintLimit(rsethAmountToMintAsProtocolFee)` is called — triggering the revert.

**Both public entry points are blocked:** `updateRSETHPrice()` (L87-89) and `updateRSETHPriceAsManager()` (L94-96) both call `_updateRsETHPrice()`, so neither can succeed.

**Stale price impact on deposits:** `getRsETHAmountToMint` in `LRTDepositPool.sol` (L520) reads `lrtOracle.rsETHPrice()` — the stored stale value — so depositors receive rsETH at an incorrect exchange rate for the entire blocked period, diluting existing holders.

## Impact Explanation

Protocol fees (yield accruing to the treasury) are permanently uncollectable: every call to update the price reverts, `rsETHPrice` is never updated, and the fee mint never executes. This matches **Medium — Permanent freezing of unclaimed yield**. The secondary effect — depositors minting rsETH at a stale (under-valued) price — dilutes existing rsETH holders for the entire blocked period.

## Likelihood Explanation

`maxFeeMintAmountPerDay = 0` is the **default state** after deployment; no initializer sets it. `protocolFeeInBPS > 0` is the normal operating state for a fee-collecting protocol. Any deposit after the last price update increases `totalETHInProtocol`, which is routine. All three conditions co-exist naturally in normal protocol operation without any deliberate misconfiguration. Any unprivileged user can call the public `updateRSETHPrice()` to trigger the revert once these conditions hold.

## Recommendation

Add a zero-limit bypass at the top of `_checkAndUpdateDailyFeeMintLimit`:

```solidity
function _checkAndUpdateDailyFeeMintLimit(uint256 feeAmount) internal {
    if (maxFeeMintAmountPerDay == 0) return; // fee minting disabled; skip limit check

    if (block.timestamp >= feePeriodStartTime + 1 days) {
        currentPeriodMintedFeeAmount = 0;
        feePeriodStartTime = getCurrentPeriodStartTime();
    }

    if (currentPeriodMintedFeeAmount + feeAmount > maxFeeMintAmountPerDay) {
        revert DailyFeeMintLimitExceeded(currentPeriodMintedFeeAmount + feeAmount, maxFeeMintAmountPerDay);
    }

    currentPeriodMintedFeeAmount += feeAmount;
}
```

Alternatively, add a validation in `setMaxFeeMintAmountPerDay` that prevents setting `0` when `protocolFeeInBPS > 0`, and enforce a non-zero default in `initialize()`.

## Proof of Concept

```solidity
// Preconditions:
// - maxFeeMintAmountPerDay = 0 (default after initialize(), never set)
// - protocolFeeInBPS = 100 (1%, set by admin as normal operation)
// - rsETH totalSupply > 0, rsETHPrice = 1e18
// - One deposit of 1 ETH → totalETHInProtocol increases by 1e18

// Step 1: Confirm default state
assertEq(lrtOracle.maxFeeMintAmountPerDay(), 0);

// Step 2: Any user calls updateRSETHPrice() — reverts
vm.expectRevert(
    abi.encodeWithSelector(
        LRTOracle.DailyFeeMintLimitExceeded.selector,
        rsethAmountToMintAsProtocolFee, // > 0
        0                               // maxFeeMintAmountPerDay
    )
);
lrtOracle.updateRSETHPrice();

// Step 3: Price is unchanged (stale)
assertEq(lrtOracle.rsETHPrice(), previousPrice);

// Step 4: Manager call also fails
vm.prank(manager);
vm.expectRevert(...);
lrtOracle.updateRSETHPriceAsManager();

// Step 5: Wait 24 hours — period resets but same revert fires again
vm.warp(block.timestamp + 1 days + 1);
vm.expectRevert(...);
lrtOracle.updateRSETHPrice(); // still reverts: 0 + feeAmount > 0
```