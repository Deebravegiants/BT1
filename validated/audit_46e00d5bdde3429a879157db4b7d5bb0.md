### Title
Uninitialized `maxFeeMintAmountPerDay` Causes DoS on `updateRSETHPrice()` When Rewards Accrue — (`contracts/LRTOracle.sol`)

### Summary
When `maxFeeMintAmountPerDay` is 0 (its default uninitialized value) and ETH rewards have accrued (`totalETHInProtocol > previousTVL`), every call to `updateRSETHPrice()` permanently reverts with `DailyFeeMintLimitExceeded`, freezing the oracle price and blocking all downstream operations that depend on a fresh price until an admin intervenes.

### Finding Description

`_checkAndUpdateDailyFeeMintLimit` is called unconditionally inside `_updateRsETHPrice()` whenever `protocolFeeInETH > 0`: [1](#0-0) 

The guard inside that function is: [2](#0-1) 

When `maxFeeMintAmountPerDay == 0` (the Solidity default for an unset `uint256`) and `feeAmount > 0`, the condition `0 + feeAmount > 0` is always `true`, so the function always reverts. There is no bypass path: both `updateRSETHPrice()` (public) and `updateRSETHPriceAsManager()` (manager-only) call the same `_updateRsETHPrice()` internal, so neither can succeed. [3](#0-2) 

The `reinitialize` function, which is the upgrade-time setup entry point, only sets `feePeriodStartTime` — it never initialises `maxFeeMintAmountPerDay`: [4](#0-3) 

`maxFeeMintAmountPerDay` can only be set via `setMaxFeeMintAmountPerDay()`, which is a separate, manually-invoked manager call: [5](#0-4) 

If this call is omitted (or if the value is later reset to 0), the moment any staking rewards push `totalETHInProtocol` above `previousTVL`, the oracle update path is bricked.

### Impact Explanation

**Medium — Temporary freezing of oracle price updates.**

`rsETHPrice` is never updated, so all callers that read the stored price (deposit minting, withdrawal calculations) operate on a stale value. The freeze persists until an LRT Manager calls `setMaxFeeMintAmountPerDay` with a non-zero value. Because the fix requires a privileged transaction, the duration of the freeze is indeterminate. The impact does **not** reach "Critical / Permanent" because the admin retains the ability to unblock the system without an upgrade.

### Likelihood Explanation

Moderate. The `reinitialize` function does not set `maxFeeMintAmountPerDay`, so any deployment or upgrade that omits the separate `setMaxFeeMintAmountPerDay` call leaves the contract in the broken state. Staking rewards accrue continuously, so the first oracle update after rewards arrive will trigger the revert.

### Recommendation

1. Set `maxFeeMintAmountPerDay` inside `reinitialize` (or require it as a parameter).
2. Alternatively, treat `maxFeeMintAmountPerDay == 0` as "unlimited" inside `_checkAndUpdateDailyFeeMintLimit`, consistent with how `remainingDailyFeeMintLimit()` already handles the zero case: [6](#0-5) 

A one-line guard at the top of `_checkAndUpdateDailyFeeMintLimit` — `if (maxFeeMintAmountPerDay == 0) return;` — would make the zero value mean "no cap" and eliminate the DoS.

### Proof of Concept

```solidity
// Preconditions:
//   maxFeeMintAmountPerDay == 0  (never set after deployment/upgrade)
//   protocolFeeInBPS > 0
//   totalETHInProtocol > previousTVL  (rewards accrued)

// Step 1: deploy LRTOracle, call reinitialize() — maxFeeMintAmountPerDay stays 0
// Step 2: simulate ETH rewards so totalETHInProtocol > rsethSupply * rsETHPrice
// Step 3: call updateRSETHPrice()
//   → _updateRsETHPrice()
//   → protocolFeeInETH = rewardAmount * protocolFeeInBPS / 10000  > 0
//   → rsethAmountToMintAsProtocolFee > 0
//   → _checkAndUpdateDailyFeeMintLimit(rsethAmountToMintAsProtocolFee)
//   → currentPeriodMintedFeeAmount(0) + feeAmount > maxFeeMintAmountPerDay(0)  → TRUE
//   → revert DailyFeeMintLimitExceeded(feeAmount, 0)   ✓

// Step 4: assert rsETHPrice unchanged
// Step 5: assert every subsequent call also reverts (until setMaxFeeMintAmountPerDay is called)
```

### Citations

**File:** contracts/LRTOracle.sol (L72-79)
```text
    function reinitialize(uint256 _feePeriodStartTime) external reinitializer(2) onlyLRTManager {
        if (_feePeriodStartTime > block.timestamp || _feePeriodStartTime <= block.timestamp - 1 days) {
            revert PeriodStartTimeShouldBeWithin24Hours();
        }

        feePeriodStartTime = _feePeriodStartTime;
        emit FeePeriodStartTimeSet(_feePeriodStartTime);
    }
```

**File:** contracts/LRTOracle.sol (L87-96)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }

    /// @dev update rsETH price as an manager account
    /// @dev main benefit is to be able to update the price in case of the price going above the threshold
    /// @dev only LRT manager is allowed to call this function
    function updateRSETHPriceAsManager() external onlyLRTManager {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L132-135)
```text
    function setMaxFeeMintAmountPerDay(uint256 _maxFeeMintAmountPerDay) external onlyLRTManager {
        maxFeeMintAmountPerDay = _maxFeeMintAmountPerDay;
        emit MaxFeeMintAmountPerDayUpdated(_maxFeeMintAmountPerDay);
    }
```

**File:** contracts/LRTOracle.sol (L171-171)
```text
        if (maxFeeMintAmountPerDay == 0) return 0;
```

**File:** contracts/LRTOracle.sol (L205-207)
```text
        if (currentPeriodMintedFeeAmount + feeAmount > maxFeeMintAmountPerDay) {
            revert DailyFeeMintLimitExceeded(currentPeriodMintedFeeAmount + feeAmount, maxFeeMintAmountPerDay);
        }
```

**File:** contracts/LRTOracle.sol (L299-303)
```text
        if (protocolFeeInETH > 0) {
            // Calculate rsETH amount to mint as protocol fee
            uint256 rsethAmountToMintAsProtocolFee = protocolFeeInETH.divWad(newRsETHPrice);

            _checkAndUpdateDailyFeeMintLimit(rsethAmountToMintAsProtocolFee);
```
