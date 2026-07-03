### Title
`_checkAndUpdateDailyFeeMintLimit` Missing Zero-Guard Causes `updateRSETHPrice()` to Permanently Revert When `maxFeeMintAmountPerDay == 0` and Protocol Fee Is Non-Zero — (`contracts/LRTOracle.sol`)

---

### Summary

When `maxFeeMintAmountPerDay` is zero (the default uninitialized value, or explicitly set by a manager), any call to `updateRSETHPrice()` or `updateRSETHPriceAsManager()` reverts with `DailyFeeMintLimitExceeded` whenever a TVL increase generates a non-zero protocol fee. This freezes `rsETHPrice` at a stale value, causing `LRTWithdrawalManager.unlockQueue()` to compute incorrect payout amounts for all pending withdrawals.

---

### Finding Description

`_checkAndUpdateDailyFeeMintLimit` enforces the daily fee cap unconditionally: [1](#0-0) 

```solidity
if (currentPeriodMintedFeeAmount + feeAmount > maxFeeMintAmountPerDay) {
    revert DailyFeeMintLimitExceeded(currentPeriodMintedFeeAmount + feeAmount, maxFeeMintAmountPerDay);
}
```

When `maxFeeMintAmountPerDay == 0`, this reduces to `feeAmount > 0`, which is true for any non-zero fee. The function reverts unconditionally.

This is called from `_updateRsETHPrice()` whenever `protocolFeeInETH > 0`: [2](#0-1) 

```solidity
if (protocolFeeInETH > 0) {
    uint256 rsethAmountToMintAsProtocolFee = protocolFeeInETH.divWad(newRsETHPrice);
    _checkAndUpdateDailyFeeMintLimit(rsethAmountToMintAsProtocolFee);
```

The inconsistency is visible in `remainingDailyFeeMintLimit()`, which **does** handle the zero case: [3](#0-2) 

```solidity
if (maxFeeMintAmountPerDay == 0) return 0;
```

But `_checkAndUpdateDailyFeeMintLimit` has no equivalent guard. The default storage value of `maxFeeMintAmountPerDay` is `0` — no admin action is required to enter this state. It is the state of the contract from deployment until `setMaxFeeMintAmountPerDay` is explicitly called with a non-zero value. [4](#0-3) 

`setMaxFeeMintAmountPerDay` also allows a manager to reset it to zero at any time: [5](#0-4) 

Both `updateRSETHPrice()` (public) and `updateRSETHPriceAsManager()` (manager-only) call `_updateRsETHPrice()`, so neither path can bypass the revert: [6](#0-5) 

---

### Impact Explanation

`rsETHPrice` is never updated (line 313 is never reached): [7](#0-6) 

`LRTWithdrawalManager.unlockQueue()` reads the stale `rsETHPrice` directly from oracle storage: [8](#0-7) 

This stale price is then used to compute each user's payout: [9](#0-8) 

If `rsETHPrice` is stale-low (TVL grew but price was never updated), users receive less than the current fair value of their rsETH. The condition persists until a manager calls `setMaxFeeMintAmountPerDay` with a non-zero value — making this a **temporary freeze** of accurate price settlement for all queued withdrawals.

---

### Likelihood Explanation

- **Default state triggers it**: `maxFeeMintAmountPerDay` is `0` at deployment. Any protocol with `protocolFeeInBPS > 0` and any TVL growth will hit this immediately after upgrade/deployment, before `setMaxFeeMintAmountPerDay` is called.
- **No attacker required**: This is a logic defect in the default configuration path, not an attack vector requiring external manipulation.
- **Manager reset**: A manager calling `setMaxFeeMintAmountPerDay(0)` (e.g., intending to "disable" the limit) re-triggers the condition.

---

### Recommendation

Add a zero-bypass guard in `_checkAndUpdateDailyFeeMintLimit`, consistent with `remainingDailyFeeMintLimit`:

```solidity
function _checkAndUpdateDailyFeeMintLimit(uint256 feeAmount) internal {
+   if (maxFeeMintAmountPerDay == 0) return; // 0 means no limit / disabled

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

Alternatively, enforce a non-zero value in `setMaxFeeMintAmountPerDay` and set a non-zero default in `reinitialize`.

---

### Proof of Concept

```solidity
// Setup: protocolFeeInBPS = 500 (5%), maxFeeMintAmountPerDay = 0 (default)
// rsethSupply > 0, totalETHInProtocol > previousTVL

// Step 1: Simulate TVL increase (e.g., staking rewards accrue)
// totalETHInProtocol > rsethSupply * rsETHPrice

// Step 2: Call updateRSETHPrice() — public, no role required
vm.expectRevert(
    abi.encodeWithSelector(
        ILRTOracle.DailyFeeMintLimitExceeded.selector,
        rsethAmountToMintAsProtocolFee,
        0
    )
);
lrtOracle.updateRSETHPrice();

// Step 3: Verify rsETHPrice is unchanged (stale)
assertEq(lrtOracle.rsETHPrice(), previousPrice);

// Step 4: unlockQueue() proceeds with stale price, underpaying users
// _calculatePayoutAmount uses stale rsETHPrice → lower payout than fair value
```

### Citations

**File:** contracts/LRTOracle.sol (L35-35)
```text
    uint256 public maxFeeMintAmountPerDay;
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

**File:** contracts/LRTOracle.sol (L132-134)
```text
    function setMaxFeeMintAmountPerDay(uint256 _maxFeeMintAmountPerDay) external onlyLRTManager {
        maxFeeMintAmountPerDay = _maxFeeMintAmountPerDay;
        emit MaxFeeMintAmountPerDayUpdated(_maxFeeMintAmountPerDay);
```

**File:** contracts/LRTOracle.sol (L171-171)
```text
        if (maxFeeMintAmountPerDay == 0) return 0;
```

**File:** contracts/LRTOracle.sol (L204-207)
```text
        // Check if minting would exceed the daily limit
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

**File:** contracts/LRTOracle.sol (L313-313)
```text
        rsETHPrice = newRsETHPrice;
```

**File:** contracts/LRTWithdrawalManager.sol (L833-834)
```text
        uint256 currentReturn = (request.rsETHUnstaked * rsETHPrice) / assetPrice;
        return (request.expectedAssetAmount < currentReturn) ? request.expectedAssetAmount : currentReturn;
```

**File:** contracts/LRTWithdrawalManager.sol (L847-847)
```text
            rsETHPrice: lrtOracle.rsETHPrice(),
```
