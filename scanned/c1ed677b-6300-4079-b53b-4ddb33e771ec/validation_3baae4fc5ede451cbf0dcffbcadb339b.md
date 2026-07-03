### Title
`LRTOracle.setMaxFeeMintAmountPerDay` lacks zero-value validation, causing `updateRSETHPrice()` to permanently revert when protocol fees are due — (File: contracts/LRTOracle.sol)

---

### Summary

`setMaxFeeMintAmountPerDay` in `LRTOracle.sol` accepts any `uint256` value, including 0, with no lower-bound guard. When set to 0, every subsequent call to `updateRSETHPrice()` reverts with `DailyFeeMintLimitExceeded` the moment the protocol has earned any fee (i.e., TVL increased). This permanently blocks the rsETH price oracle update and freezes all unclaimed protocol yield until the manager manually corrects the value.

---

### Finding Description

`setMaxFeeMintAmountPerDay` stores the caller-supplied value directly with no validation: [1](#0-0) 

When `maxFeeMintAmountPerDay` is 0, the internal guard `_checkAndUpdateDailyFeeMintLimit` evaluates:

```
currentPeriodMintedFeeAmount + feeAmount > maxFeeMintAmountPerDay
```

as `feeAmount > 0`, which is true whenever the protocol has earned any fee. This causes a revert: [2](#0-1) 

The revert propagates up through `_updateRsETHPrice()`: [3](#0-2) 

Both the public `updateRSETHPrice()` and the manager-only `updateRSETHPriceAsManager()` call `_updateRsETHPrice()`, so neither path can succeed: [4](#0-3) 

---

### Impact Explanation

- **Unclaimed yield frozen**: Protocol fees (minted as rsETH to the treasury) cannot be minted for as long as `maxFeeMintAmountPerDay == 0`. Every `updateRSETHPrice()` call reverts when `protocolFeeInETH > 0`, so the fee-minting path is completely blocked.
- **Stale rsETH price**: Because `rsETHPrice` is only updated inside `_updateRsETHPrice()`, the stored price drifts from the true NAV. Downstream callers — `LRTDepositPool.getRsETHAmountToMint()` and `LRTWithdrawalManager.getExpectedAssetAmount()` — consume the stale price, causing incorrect mint/withdrawal amounts for all users.

**Impact class**: Medium — Permanent freezing of unclaimed yield (protocol fee cannot be minted); additionally, the stale price constitutes a contract failing to deliver promised returns.

---

### Likelihood Explanation

The LRT manager role is expected to tune `maxFeeMintAmountPerDay` over time (e.g., to adjust for protocol growth). There is no on-chain guard preventing an accidental `setMaxFeeMintAmountPerDay(0)` call — for example, when a manager intends to "disable" fee minting temporarily or makes a unit-conversion error. The absence of any validation makes this a realistic misconfiguration path.

---

### Recommendation

Add a non-zero lower-bound check in `setMaxFeeMintAmountPerDay`:

```solidity
function setMaxFeeMintAmountPerDay(uint256 _maxFeeMintAmountPerDay) external onlyLRTManager {
    if (_maxFeeMintAmountPerDay == 0) revert InvalidMaxFeeMintAmount();
    maxFeeMintAmountPerDay = _maxFeeMintAmountPerDay;
    emit MaxFeeMintAmountPerDayUpdated(_maxFeeMintAmountPerDay);
}
```

If the intent is to allow disabling fee minting, add a separate boolean flag rather than overloading the zero value.

---

### Proof of Concept

1. LRT manager calls `setMaxFeeMintAmountPerDay(0)`.
2. Protocol earns staking rewards → `totalETHInProtocol > previousTVL`.
3. Anyone calls `updateRSETHPrice()`.
4. Inside `_updateRsETHPrice()`: `protocolFeeInETH > 0` → `rsethAmountToMintAsProtocolFee > 0`.
5. `_checkAndUpdateDailyFeeMintLimit(rsethAmountToMintAsProtocolFee)` evaluates `0 + rsethAmountToMintAsProtocolFee > 0` → **reverts with `DailyFeeMintLimitExceeded`**.
6. `updateRSETHPrice()` reverts. `rsETHPrice` stays stale. Protocol fees are never minted.
7. `updateRSETHPriceAsManager()` also reverts for the same reason — no escape path exists until the manager sets a non-zero value. [1](#0-0) [5](#0-4) [6](#0-5)

### Citations

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

**File:** contracts/LRTOracle.sol (L299-311)
```text
        if (protocolFeeInETH > 0) {
            // Calculate rsETH amount to mint as protocol fee
            uint256 rsethAmountToMintAsProtocolFee = protocolFeeInETH.divWad(newRsETHPrice);

            _checkAndUpdateDailyFeeMintLimit(rsethAmountToMintAsProtocolFee);
            if (rsethAmountToMintAsProtocolFee > 0) {
                address treasury = lrtConfig.getContract(LRTConstants.PROTOCOL_TREASURY);
                IRSETH(rsETHTokenAddress).mint(treasury, rsethAmountToMintAsProtocolFee);
                emit FeeMinted(treasury, rsethAmountToMintAsProtocolFee);
            }
        } else {
            _checkAndUpdateDailyFeeMintLimit(0);
        }
```
