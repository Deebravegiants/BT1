### Title
Unbounded `setPricePercentageLimit` Silently Disables Both Upside and Downside Price-Protection Guards - (File: contracts/LRTOracle.sol)

### Summary
`LRTOracle.setPricePercentageLimit` accepts any `uint256` value with no lower or upper bound check. Setting it to `0` short-circuits both the upside-deviation gate and the downside auto-pause guard in `_updateRsETHPrice`, permanently disabling the only on-chain safety mechanism that protects depositors from a manipulated or slashed rsETH price.

### Finding Description
`LRTOracle` maintains a dual price-protection mechanism inside `_updateRsETHPrice`:

**Upside guard** (lines 256–257): if the new rsETH price exceeds `highestRsethPrice` by more than `pricePercentageLimit`, non-manager callers revert with `PriceAboveDailyThreshold`.

**Downside guard** (lines 273–274): if the new rsETH price falls below `highestRsethPrice` by more than `pricePercentageLimit`, the deposit pool, withdrawal manager, and oracle are all paused.

Both guards share the same short-circuit condition:

```solidity
pricePercentageLimit > 0 && ...
```

The setter that controls this critical parameter is:

```solidity
function setPricePercentageLimit(uint256 _pricePercentageLimit) external onlyLRTAdmin {
    pricePercentageLimit = _pricePercentageLimit;   // no bounds check
    emit PricePercentageLimitUpdate(_pricePercentageLimit);
}
```

There is no minimum or maximum validation. Passing `0` makes `pricePercentageLimit > 0` permanently false, so both guards are silently disabled for every subsequent call to `updateRSETHPrice()` (public) and `updateRSETHPriceAsManager()`. Passing an astronomically large value (e.g. `type(uint256).max`) makes `pricePercentageLimit.mulWad(highestRsethPrice)` overflow-safe via OZ `mulDiv` but produces a threshold that can never be exceeded, achieving the same effect.

The same pattern exists for `setMaxFeeMintAmountPerDay` (lines 132–135): setting it to `0` causes `_checkAndUpdateDailyFeeMintLimit` to revert with `DailyFeeMintLimitExceeded` whenever `protocolFeeInETH > 0`, permanently stalling oracle updates during any reward-accruing period.

### Impact Explanation
With `pricePercentageLimit = 0`:
- The downside auto-pause never fires. A slashing event or oracle manipulation that drives rsETH price far below its historical peak will not trigger the emergency pause, leaving the deposit pool and withdrawal manager open. Users continue to deposit and withdraw at a stale or manipulated price, suffering direct economic loss.
- The upside gate never fires. Any price spike — including one caused by a faulty oracle — is accepted by any public caller without restriction.

With `maxFeeMintAmountPerDay = 0`: every call to `updateRSETHPrice()` reverts when TVL has grown, freezing the rsETH price at its last recorded value and halting fee accrual until a manager corrects the setting.

Both scenarios match **Medium – Temporary freezing of funds / Permanent freezing of unclaimed yield** from the allowed impact scope.

### Likelihood Explanation
The setter is restricted to `onlyLRTAdmin` / `onlyLRTManager`, so exploitation requires an admin or manager to supply an out-of-range value — either through a miscalculation (e.g. confusing the 1e18-precision scale with a raw BPS value) or a deployment/upgrade script error. The original Nouns Builder report was accepted at Medium on exactly this basis: low likelihood of accidental misconfiguration, high impact once it occurs.

### Recommendation
Add explicit range checks in both setters and in any `initialize`/`reinitialize` path that touches these variables:

```solidity
// pricePercentageLimit: enforce 0.01% (1e14) ≤ limit ≤ 100% (1e18)
function setPricePercentageLimit(uint256 _pricePercentageLimit) external onlyLRTAdmin {
    if (_pricePercentageLimit == 0 || _pricePercentageLimit > 1e18)
        revert InvalidPricePercentageLimit();
    pricePercentageLimit = _pricePercentageLimit;
    emit PricePercentageLimitUpdate(_pricePercentageLimit);
}

// maxFeeMintAmountPerDay: enforce a non-zero, protocol-reasonable ceiling
function setMaxFeeMintAmountPerDay(uint256 _maxFeeMintAmountPerDay) external onlyLRTManager {
    if (_maxFeeMintAmountPerDay == 0) revert InvalidMaxFeeMintAmount();
    maxFeeMintAmountPerDay = _maxFeeMintAmountPerDay;
    emit MaxFeeMintAmountPerDayUpdated(_maxFeeMintAmountPerDay);
}
```

Apply the same checks in any future `reinitialize` that sets these fields.

### Proof of Concept

1. Admin calls `setPricePercentageLimit(0)`.
2. A slashing event reduces the underlying stETH/ETHx value, causing `_getTotalEthInProtocol()` to return a value that yields `newRsETHPrice < highestRsethPrice`.
3. Inside `_updateRsETHPrice`, the downside check evaluates:
   ```solidity
   bool isPriceDecreaseOffLimit =
       pricePercentageLimit > 0 &&   // FALSE — short-circuits here
       diff > pricePercentageLimit.mulWad(highestRsethPrice);
   ```
4. `isPriceDecreaseOffLimit` is `false`; the auto-pause block is skipped entirely.
5. `rsETHPrice` is updated to the depressed value; the deposit pool and withdrawal manager remain open.
6. Users who call `LRTDepositPool.depositAsset` or `LRTWithdrawalManager.initiateWithdrawal` now interact at the incorrect price, suffering economic loss that the guard was designed to prevent.

Relevant code references: [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

### Citations

**File:** contracts/LRTOracle.sol (L125-128)
```text
    function setPricePercentageLimit(uint256 _pricePercentageLimit) external onlyLRTAdmin {
        pricePercentageLimit = _pricePercentageLimit;
        emit PricePercentageLimitUpdate(_pricePercentageLimit);
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

**File:** contracts/LRTOracle.sol (L252-266)
```text
        if (newRsETHPrice > highestRsethPrice) {
            // check if the price is above the threshold
            uint256 priceDifference = newRsETHPrice - highestRsethPrice;
            // pricePercentageLimit is in 1e18 precision (100% = 1e18, 1% = 1e16)
            bool isPriceIncreaseOffLimit =
                pricePercentageLimit > 0 && priceDifference > pricePercentageLimit.mulWad(highestRsethPrice);

            // check if the price difference is above the threshold
            if (isPriceIncreaseOffLimit) {
                // if sender has a manager role, this doesn't revert.
                // if not, it reverts as price went above the threshold
                if (!IAccessControl(address(lrtConfig)).hasRole(LRTConstants.MANAGER, msg.sender)) {
                    revert PriceAboveDailyThreshold();
                }
            }
```

**File:** contracts/LRTOracle.sol (L270-282)
```text
        if (newRsETHPrice < highestRsethPrice) {
            uint256 diff = highestRsethPrice - newRsETHPrice;
            // normalizing to 1e18
            bool isPriceDecreaseOffLimit =
                pricePercentageLimit > 0 && diff > pricePercentageLimit.mulWad(highestRsethPrice);

            // if price decrease is off limit, pause the protocol (unless it's already paused)
            if (isPriceDecreaseOffLimit) {
                if (!lrtDepositPool.paused()) lrtDepositPool.pause();
                if (!withdrawalManager.paused()) withdrawalManager.pause();
                _pause();
                return;
            }
```
