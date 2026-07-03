### Title
`setPricePercentageLimit` can be set to zero or above 100% disabling rsETH price protection mechanisms - (File: contracts/LRTOracle.sol)

---

### Summary

`setPricePercentageLimit()` in `LRTOracle.sol` has no bounds validation, allowing the admin to set `pricePercentageLimit` to zero or any arbitrarily large value. This silently disables both the upside price-threshold guard (which reverts non-manager callers when the price rises too fast) and the downside auto-pause mechanism (which halts the protocol when the rsETH price drops too far). The default uninitialized value is `0`, meaning both protections are off-by-default until the admin explicitly enables them.

---

### Finding Description

The setter accepts any `uint256` without restriction:

```solidity
// contracts/LRTOracle.sol  lines 121-128
/// @dev PricePercentageLimit for 1% is 1e16
/// @dev Price Percentage Limit for 100% is 1e18
function setPricePercentageLimit(uint256 _pricePercentageLimit) external onlyLRTAdmin {
    pricePercentageLimit = _pricePercentageLimit;
    emit PricePercentageLimitUpdate(_pricePercentageLimit);
}
``` [1](#0-0) 

The NatSpec documents the valid range (1 % = `1e16`, 100 % = `1e18`), but nothing enforces it.

`pricePercentageLimit` gates two critical branches inside `_updateRsETHPrice()`:

**Upside guard** — reverts non-manager callers when the price rises above the threshold:

```solidity
bool isPriceIncreaseOffLimit =
    pricePercentageLimit > 0 && priceDifference > pricePercentageLimit.mulWad(highestRsethPrice);
``` [2](#0-1) 

**Downside auto-pause** — pauses the deposit pool, withdrawal manager, and oracle when the price drops too far:

```solidity
bool isPriceDecreaseOffLimit =
    pricePercentageLimit > 0 && diff > pricePercentageLimit.mulWad(highestRsethPrice);

if (isPriceDecreaseOffLimit) {
    if (!lrtDepositPool.paused()) lrtDepositPool.pause();
    if (!withdrawalManager.paused()) withdrawalManager.pause();
    _pause();
    return;
}
``` [3](#0-2) 

Both branches share the `pricePercentageLimit > 0` short-circuit. Two misconfiguration paths disable them:

| Value set | Effect |
|---|---|
| `0` (default / explicit) | `pricePercentageLimit > 0` is `false` → both guards permanently skipped |
| `> 1e18` (e.g. `2e18` = 200 %) | Downside guard requires a >100 % drop — mathematically impossible; upside guard requires a >100 % rise — practically impossible |

Because `pricePercentageLimit` is a plain `uint256` storage slot, it initializes to `0` and the `initialize()` function never sets it, so the protections are **disabled by default** until the admin explicitly calls `setPricePercentageLimit`.

---

### Impact Explanation

**Downside auto-pause disabled.** If the rsETH price falls sharply (e.g., due to EigenLayer slashing or a price-calculation anomaly) and `pricePercentageLimit` is `0` or `> 1e18`, `_updateRsETHPrice()` will not pause the deposit pool or withdrawal manager. The protocol continues accepting deposits and processing withdrawals at the depressed price. Users who act on stale expectations suffer losses; the protocol fails to deliver its documented safety guarantee.

**Upside guard disabled.** Any unprivileged caller of the public `updateRSETHPrice()` can push the rsETH price to whatever the oracle returns, with no threshold revert. Combined with a misconfigured or drifting oracle, this allows the price to be updated to an extreme value without the manager-only override path being required.

Impact classification: **Low — Contract fails to deliver promised returns** (the auto-pause safety net is silently absent; no direct theft path exists without a separate oracle compromise).

---

### Likelihood Explanation

- `pricePercentageLimit` defaults to `0`; the admin must remember to call `setPricePercentageLimit` after deployment/upgrade. Any deployment that omits this step ships with both protections disabled.
- The precision convention (`1e16` per 1 %) is non-obvious. An admin intending to set 5 % might pass `5` (raw) instead of `5e16`, producing a near-zero limit that is effectively disabled.
- There is no event or revert to signal that the value is out of range, so the misconfiguration is silent.

---

### Recommendation

Add a minimum and maximum bound check inside `setPricePercentageLimit`:

```solidity
uint256 public constant MIN_PRICE_PERCENTAGE_LIMIT = 1e14;  // 0.01%
uint256 public constant MAX_PRICE_PERCENTAGE_LIMIT = 1e18;  // 100%

function setPricePercentageLimit(uint256 _pricePercentageLimit) external onlyLRTAdmin {
    if (_pricePercentageLimit < MIN_PRICE_PERCENTAGE_LIMIT || _pricePercentageLimit > MAX_PRICE_PERCENTAGE_LIMIT) {
        revert InvalidPricePercentageLimit();
    }
    pricePercentageLimit = _pricePercentageLimit;
    emit PricePercentageLimitUpdate(_pricePercentageLimit);
}
```

Additionally, set a safe default value for `pricePercentageLimit` inside `initialize()` so the protection is active from the first block.

---

### Proof of Concept

1. Admin deploys/upgrades `LRTOracle` and never calls `setPricePercentageLimit` (or calls it with `0`). `pricePercentageLimit` remains `0`.
2. An EigenLayer slashing event causes the underlying asset value to drop 15 %. `_getTotalEthInProtocol()` returns a lower value.
3. Any user (or a keeper bot) calls the public `updateRSETHPrice()`.
4. Inside `_updateRsETHPrice()`, `newRsETHPrice < highestRsethPrice`. The downside check evaluates:
   ```solidity
   bool isPriceDecreaseOffLimit = pricePercentageLimit > 0 && ...;
   // → false && ... → false
   ```
5. `isPriceDecreaseOffLimit` is `false`; the auto-pause block is skipped entirely.
6. The deposit pool and withdrawal manager remain open. Users continue depositing and withdrawing at the slashed price without the protocol halting for investigation.
7. The protocol fails to deliver the documented downside-protection guarantee. [4](#0-3) [5](#0-4)

### Citations

**File:** contracts/LRTOracle.sol (L121-128)
```text
    /// @dev set the price percentage limit. Only onlyLRTAdmin is allowed
    /// @dev PricePercentageLimit for 1% is 1e16
    /// @dev Price Percentage Limit for 100% is 1e18
    /// @param _pricePercentageLimit price percentage limit
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
