### Title
`LRTOracle` Price Update Blocked for Non-Manager Callers When Rapid Appreciation Exceeds `pricePercentageLimit`, Causing Stale Rate Used to Mint Excess wrsETH — (File: `contracts/LRTOracle.sol`)

---

### Summary

`LRTOracle._updateRsETHPrice()` enforces an upside price-change guard: if the newly computed rsETH price exceeds `highestRsethPrice` by more than `pricePercentageLimit`, the public `updateRSETHPrice()` call reverts with `PriceAboveDailyThreshold` for any non-manager caller. Only the manager can bypass this via `updateRSETHPriceAsManager()`. During any window of rapid legitimate price appreciation (e.g., a large EigenLayer reward distribution), the stored `rsETHPrice` becomes stale. L2 pools (`RSETHPoolV3`) read this stale (lower) rate to compute how much wrsETH to mint per deposited ETH, causing new depositors to receive excess wrsETH at the expense of existing holders.

---

### Finding Description

In `LRTOracle._updateRsETHPrice()`, after computing `newRsETHPrice`, the following guard is applied:

```solidity
// contracts/LRTOracle.sol lines 252-266
if (newRsETHPrice > highestRsethPrice) {
    uint256 priceDifference = newRsETHPrice - highestRsethPrice;
    bool isPriceIncreaseOffLimit =
        pricePercentageLimit > 0 && priceDifference > pricePercentageLimit.mulWad(highestRsethPrice);

    if (isPriceIncreaseOffLimit) {
        if (!IAccessControl(address(lrtConfig)).hasRole(LRTConstants.MANAGER, msg.sender)) {
            revert PriceAboveDailyThreshold();
        }
    }
}
``` [1](#0-0) 

When this reverts, `rsETHPrice` is **not updated** — it remains at the previous (lower) value. The public entry point `updateRSETHPrice()` is gated by `whenNotPaused` only; any EOA or keeper bot can call it, but they will receive a revert whenever the price appreciation exceeds the configured limit. [2](#0-1) 

The only escape hatch is `updateRSETHPriceAsManager()`, callable exclusively by the `MANAGER` role.

The stale `rsETHPrice` is then read by the cross-chain rate provider chain:

- `RSETHRateProvider.getLatestRate()` → `ILRTOracle(rsETHPriceOracle).rsETHPrice()` (stale value)
- `RSETHMultiChainRateProvider.getLatestRate()` → same stale value [3](#0-2) [4](#0-3) 

On L2, `RSETHPoolV3.getRate()` calls `IOracle(rsETHOracle).getRate()`, which resolves to the stale rate broadcast from L1. [5](#0-4) 

The deposit pricing formula is:

```solidity
// contracts/pools/RSETHPoolV3.sol lines 303-307
uint256 rsETHToETHrate = getRate();          // stale, lower than actual
rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
``` [6](#0-5) 

A stale (lower) `rsETHToETHrate` inflates `rsETHAmount`, so new depositors receive more wrsETH than the true exchange rate warrants, diluting existing holders.

---

### Impact Explanation

**Impact: Medium — Temporary freezing of oracle updates / theft of unclaimed yield from existing rsETH holders.**

While the oracle is stale:
1. The public `updateRSETHPrice()` is permanently reverting — the oracle fails to deliver its promised function.
2. Any new L2 deposits processed against the stale (lower) rate mint excess wrsETH. When the oracle is eventually corrected, those excess tokens represent a permanent dilution of existing holders' accrued yield.

---

### Likelihood Explanation

**Likelihood: Low-Medium.**

- EigenLayer reward distributions or a sudden large TVL increase can cause the rsETH price to jump by more than `pricePercentageLimit` in a single update cycle.
- The `pricePercentageLimit` is a configurable parameter; a conservatively small value (e.g., 0.5% = `5e15`) makes this scenario more likely during normal reward accrual.
- The window of staleness lasts until the manager manually calls `updateRSETHPriceAsManager()`. Any L2 deposits processed during this window are affected.
- No attacker action is required; the condition arises from normal protocol operation.

---

### Recommendation

1. **Emit an event and skip the update gracefully** instead of reverting when the price increase exceeds the limit for non-manager callers. This allows the oracle to remain live (at the previous price) without silently blocking all public update attempts.
2. **Separate the guard from the revert path**: log the anomaly, allow the price to be set to `highestRsethPrice + pricePercentageLimit * highestRsethPrice` as a capped value, and require manager confirmation only for the uncapped portion.
3. **Add an on-chain staleness check** in `RSETHRateProvider.getLatestRate()` that reverts or returns a sentinel if `rsETHPrice` has not been updated within a configurable heartbeat window, preventing L2 pools from consuming a stale rate.

---

### Proof of Concept

1. Protocol has `highestRsethPrice = 1.05e18`, `pricePercentageLimit = 1e16` (1%).
2. EigenLayer distributes a large reward batch; `_getTotalEthInProtocol()` returns a value that yields `newRsETHPrice = 1.062e18` (a 1.14% increase — above the 1% limit).
3. A keeper bot calls `updateRSETHPrice()`. The check at line 257 evaluates `isPriceIncreaseOffLimit = true`. Since the bot is not the manager, the call reverts with `PriceAboveDailyThreshold`. `rsETHPrice` remains at `1.05e18`.
4. The manager is slow to respond (e.g., 30 minutes).
5. During this window, `RSETHRateProvider` broadcasts the stale `1.05e18` rate to L2 via LayerZero.
6. A depositor on L2 sends 1 ETH. `RSETHPoolV3.viewSwapRsETHAmountAndFee(1e18)` computes `rsETHAmount = 1e18 * 1e18 / 1.05e18 ≈ 0.952 wrsETH` instead of the correct `1e18 / 1.062e18 ≈ 0.942 wrsETH`.
7. The depositor receives ~0.010 excess wrsETH per ETH — yield stolen from existing holders.
8. Manager eventually calls `updateRSETHPriceAsManager()`; oracle corrects, but the excess wrsETH already minted is permanent. [7](#0-6) [8](#0-7)

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

**File:** contracts/cross-chain/RSETHRateProvider.sol (L27-29)
```text
    function getLatestRate() public view override returns (uint256) {
        return ILRTOracle(rsETHPriceOracle).rsETHPrice();
    }
```

**File:** contracts/cross-chain/RSETHMultiChainRateProvider.sol (L26-28)
```text
    function getLatestRate() public view override returns (uint256) {
        return ILRTOracle(rsETHPriceOracle).rsETHPrice();
    }
```

**File:** contracts/pools/RSETHPoolV3.sol (L235-237)
```text
    function getRate() public view returns (uint256) {
        return IOracle(rsETHOracle).getRate();
    }
```

**File:** contracts/pools/RSETHPoolV3.sol (L299-308)
```text
    function viewSwapRsETHAmountAndFee(uint256 amount) public view returns (uint256 rsETHAmount, uint256 fee) {
        fee = amount * feeBps / 10_000;
        uint256 amountAfterFee = amount - fee;

        // rate of rsETH in ETH
        uint256 rsETHToETHrate = getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
    }
```
