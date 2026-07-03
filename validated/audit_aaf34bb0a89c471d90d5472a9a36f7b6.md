The code is clear enough to render a verdict without additional files. Let me trace the exact path.

### Title
`_checkAndUpdateDailyFeeMintLimit` Missing Zero-Guard Causes Permanent DoS on `updateRSETHPrice` When `maxFeeMintAmountPerDay` Is Uninitialized — (`contracts/LRTOracle.sol`)

---

### Summary

`_checkAndUpdateDailyFeeMintLimit` has no special case for `maxFeeMintAmountPerDay == 0`. Because the variable defaults to zero and is only set by an optional manager call, any invocation of `updateRSETHPrice()` that generates a non-zero protocol fee will permanently revert, freezing `rsETHPrice` at a stale value and causing withdrawing users to receive less ETH than the protocol actually backs.

---

### Finding Description

`maxFeeMintAmountPerDay` is a storage variable that initializes to `0` and is only set via `setMaxFeeMintAmountPerDay`, an optional `onlyLRTManager` call. [1](#0-0) 

When yield accrues (`totalETHInProtocol > previousTVL`) and `protocolFeeInBPS > 0`, `_updateRsETHPrice` computes a positive `rsethAmountToMintAsProtocolFee` and passes it to `_checkAndUpdateDailyFeeMintLimit`: [2](#0-1) 

Inside `_checkAndUpdateDailyFeeMintLimit`, the only guard is:

```solidity
if (currentPeriodMintedFeeAmount + feeAmount > maxFeeMintAmountPerDay) {
    revert DailyFeeMintLimitExceeded(...);
}
``` [3](#0-2) 

With `maxFeeMintAmountPerDay == 0` and any `feeAmount > 0`, the condition reduces to `feeAmount > 0` — always true — so every call reverts.

The `rsETHPrice = newRsETHPrice` assignment at line 313 is never reached: [4](#0-3) 

Notably, the view function `remainingDailyFeeMintLimit()` already handles this case with an early return, but `_checkAndUpdateDailyFeeMintLimit` does not: [5](#0-4) 

`updateRSETHPriceAsManager()` calls the same internal function and is equally blocked: [6](#0-5) 

---

### Impact Explanation

`rsETHPrice` is the exchange rate used to compute how much ETH a withdrawing user receives. While the price is frozen at a stale (lower) value, the actual ETH backing per rsETH continues to grow. Users who withdraw during this window receive fewer ETH than the protocol holds on their behalf. The gap between the stale price and the true backing is effectively unclaimable yield — it cannot be realized by withdrawing users and accumulates silently in the protocol. This matches **High — Theft of unclaimed yield**.

---

### Likelihood Explanation

The preconditions are the default deployment state:
- `maxFeeMintAmountPerDay` is never explicitly required to be set during initialization or `reinitialize`.
- `protocolFeeInBPS > 0` is the normal operating configuration for a fee-bearing protocol.
- Yield accrues automatically as staked assets earn rewards.

No attacker action is required; the broken state is reached as soon as the first yield-bearing `updateRSETHPrice()` call is made after deployment without the manager having called `setMaxFeeMintAmountPerDay`.

---

### Recommendation

Add a zero-limit bypass at the top of `_checkAndUpdateDailyFeeMintLimit`, consistent with the logic already present in `remainingDailyFeeMintLimit()`:

```solidity
function _checkAndUpdateDailyFeeMintLimit(uint256 feeAmount) internal {
+   // 0 means the limit has not been configured; treat as unlimited / fee disabled
+   if (maxFeeMintAmountPerDay == 0) return;

    if (block.timestamp >= feePeriodStartTime + 1 days) { ... }
    if (currentPeriodMintedFeeAmount + feeAmount > maxFeeMintAmountPerDay) {
        revert DailyFeeMintLimitExceeded(...);
    }
    currentPeriodMintedFeeAmount += feeAmount;
}
```

Alternatively, require `maxFeeMintAmountPerDay` to be set to a non-zero value during `reinitialize` so the uninitialized state is impossible in production.

---

### Proof of Concept

```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity 0.8.27;

// Pseudocode unit test (Foundry-style)
function test_updateRSETHPrice_revertsWhenMaxFeeMintAmountPerDayIsZero() public {
    // Preconditions:
    // - lrtOracle.maxFeeMintAmountPerDay() == 0  (never set)
    // - lrtConfig.protocolFeeInBPS() > 0
    // - rsETH totalSupply > 0
    // - feePeriodStartTime set via reinitialize

    assertEq(lrtOracle.maxFeeMintAmountPerDay(), 0);

    // Simulate yield: increase totalAssetDeposits so totalETHInProtocol > previousTVL
    _simulateYield(1 ether);

    // updateRSETHPrice must revert with DailyFeeMintLimitExceeded
    vm.expectRevert(
        abi.encodeWithSelector(ILRTOracle.DailyFeeMintLimitExceeded.selector)
    );
    lrtOracle.updateRSETHPrice();

    // rsETHPrice is unchanged (stale)
    assertEq(lrtOracle.rsETHPrice(), previousPrice);
}
```

The revert path is: `updateRSETHPrice` → `_updateRsETHPrice` → `protocolFeeInETH > 0` → `_checkAndUpdateDailyFeeMintLimit(rsethAmountToMintAsProtocolFee)` → `0 + rsethAmountToMintAsProtocolFee > 0` → `revert DailyFeeMintLimitExceeded`. [7](#0-6)

### Citations

**File:** contracts/LRTOracle.sol (L35-35)
```text
    uint256 public maxFeeMintAmountPerDay;
```

**File:** contracts/LRTOracle.sol (L94-96)
```text
    function updateRSETHPriceAsManager() external onlyLRTManager {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L171-171)
```text
        if (maxFeeMintAmountPerDay == 0) return 0;
```

**File:** contracts/LRTOracle.sol (L197-210)
```text
    function _checkAndUpdateDailyFeeMintLimit(uint256 feeAmount) internal {
        // Reset the period if it's unset or a day has passed
        if (block.timestamp >= feePeriodStartTime + 1 days) {
            currentPeriodMintedFeeAmount = 0;
            feePeriodStartTime = getCurrentPeriodStartTime();
        }

        // Check if minting would exceed the daily limit
        if (currentPeriodMintedFeeAmount + feeAmount > maxFeeMintAmountPerDay) {
            revert DailyFeeMintLimitExceeded(currentPeriodMintedFeeAmount + feeAmount, maxFeeMintAmountPerDay);
        }

        currentPeriodMintedFeeAmount += feeAmount;
    }
```

**File:** contracts/LRTOracle.sol (L299-303)
```text
        if (protocolFeeInETH > 0) {
            // Calculate rsETH amount to mint as protocol fee
            uint256 rsethAmountToMintAsProtocolFee = protocolFeeInETH.divWad(newRsETHPrice);

            _checkAndUpdateDailyFeeMintLimit(rsethAmountToMintAsProtocolFee);
```

**File:** contracts/LRTOracle.sol (L313-313)
```text
        rsETHPrice = newRsETHPrice;
```
