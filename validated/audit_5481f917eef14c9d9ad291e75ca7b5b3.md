### Title
`pricePercentageLimit` Defaults to Zero, Completely Disabling the Price-Deviation Circuit Breaker — (File: contracts/LRTOracle.sol)

---

### Summary
`LRTOracle` contains a price-deviation circuit breaker that is supposed to auto-pause the deposit pool and withdrawal manager when the rsETH price drops too far. The guard parameter `pricePercentageLimit` is never initialized and defaults to `0`, which short-circuits both the upside revert and the downside auto-pause to `false`. The result is that the circuit breaker is completely inoperative from deployment, directly analogous to the PBKDF2 finding where a security parameter is set to an insufficient value that renders the protection ineffective.

---

### Finding Description

In `LRTOracle._updateRsETHPrice()`, both circuit-breaker conditions are gated by `pricePercentageLimit > 0`:

```solidity
bool isPriceIncreaseOffLimit =
    pricePercentageLimit > 0 && priceDifference > pricePercentageLimit.mulWad(highestRsethPrice);
``` [1](#0-0) 

```solidity
bool isPriceDecreaseOffLimit =
    pricePercentageLimit > 0 && diff > pricePercentageLimit.mulWad(highestRsethPrice);
``` [2](#0-1) 

`pricePercentageLimit` is declared as a plain `uint256` storage variable:

```solidity
uint256 public pricePercentageLimit;
``` [3](#0-2) 

Neither `initialize()` nor `reinitialize()` sets it, so it remains `0` after deployment: [4](#0-3) [5](#0-4) 

The setter has no lower-bound validation, so it can also be reset to `0` at any time:

```solidity
function setPricePercentageLimit(uint256 _pricePercentageLimit) external onlyLRTAdmin {
    pricePercentageLimit = _pricePercentageLimit;
    emit PricePercentageLimitUpdate(_pricePercentageLimit);
}
``` [6](#0-5) 

With `pricePercentageLimit == 0`:
- `isPriceIncreaseOffLimit` is always `false` → the `PriceAboveDailyThreshold` revert never fires.
- `isPriceDecreaseOffLimit` is always `false` → the auto-pause of `LRTDepositPool` and `LRTWithdrawalManager` never fires. [7](#0-6) 

---

### Impact Explanation

The downside circuit breaker is the critical safety mechanism. When a validator slashing event reduces the total ETH in the protocol, `_updateRsETHPrice()` computes a lower `newRsETHPrice`. With `pricePercentageLimit == 0`, `isPriceDecreaseOffLimit` is always `false`, so the auto-pause of the deposit pool and withdrawal manager is never triggered: [8](#0-7) 

The deposit pool and withdrawal manager remain active, allowing users to continue depositing and withdrawing at the incorrect post-slashing price. Early withdrawers receive more than their fair share of the remaining assets, diluting remaining holders. In a severe slashing scenario this can cascade into protocol insolvency.

**Impact: Medium — Temporary freezing of funds** (the protocol should have paused but did not, enabling continued operation at an incorrect exchange rate).

---

### Likelihood Explanation

`updateRSETHPrice()` is a `public` function callable by any address: [9](#0-8) 

The default value of `pricePercentageLimit` is `0`, so the circuit breaker is disabled from the moment of deployment without any admin action. Validator slashing in EigenLayer is a realistic, documented event (equivocation, inactivity penalties). The combination of a disabled circuit breaker and a slashing event creates a realistic path to harm.

**Likelihood: Low** — Requires a genuine slashing event, but the circuit breaker being disabled by default makes harm more likely when such an event occurs.

---

### Recommendation

1. Initialize `pricePercentageLimit` to a meaningful non-zero value (e.g., `1e16` for 1%) inside `initialize()`.
2. Add a non-zero lower-bound check in `setPricePercentageLimit()`:
   ```solidity
   if (_pricePercentageLimit == 0) revert InvalidPricePercentageLimit();
   ```
3. Consider adding an upper-bound check (e.g., `<= 1e18`) to prevent the limit from being set so high that the circuit breaker never triggers.

---

### Proof of Concept

1. `LRTOracle` is deployed; `pricePercentageLimit` is `0` (default).
2. A validator slashing event reduces total ETH in the protocol by 10%.
3. Any external caller invokes `updateRSETHPrice()`.
4. `_updateRsETHPrice()` computes `newRsETHPrice = 0.9 × highestRsethPrice`.
5. `isPriceDecreaseOffLimit = (0 > 0) && ...` evaluates to `false`.
6. The auto-pause block is skipped; `LRTDepositPool` and `LRTWithdrawalManager` remain unpaused.
7. Users continue to withdraw rsETH at the lower, post-slashing exchange rate, diluting remaining holders. [10](#0-9)

### Citations

**File:** contracts/LRTOracle.sol (L29-29)
```text
    uint256 public pricePercentageLimit;
```

**File:** contracts/LRTOracle.sol (L64-68)
```text
    function initialize(address lrtConfigAddr) external initializer {
        UtilLib.checkNonZeroAddress(lrtConfigAddr);
        lrtConfig = ILRTConfig(lrtConfigAddr);
        emit UpdatedLRTConfig(lrtConfigAddr);
    }
```

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

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L125-128)
```text
    function setPricePercentageLimit(uint256 _pricePercentageLimit) external onlyLRTAdmin {
        pricePercentageLimit = _pricePercentageLimit;
        emit PricePercentageLimitUpdate(_pricePercentageLimit);
    }
```

**File:** contracts/LRTOracle.sol (L256-257)
```text
            bool isPriceIncreaseOffLimit =
                pricePercentageLimit > 0 && priceDifference > pricePercentageLimit.mulWad(highestRsethPrice);
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
