### Title
Price Protection Checks Silently Bypassed When `pricePercentageLimit` Is Zero — (`contracts/LRTOracle.sol`)

---

### Summary

`LRTOracle._updateRsETHPrice()` uses the compound condition `pricePercentageLimit > 0 && …` to gate both the upside price-increase guard and the downside auto-pause trigger. When `pricePercentageLimit` is `0` — its default storage value and a value the admin can freely set — the short-circuit makes both guards permanently `false`, silently disabling all price-deviation protection. This is structurally identical to the reported `attribute.epoch > 0 && attribute.epoch < block.timestamp - maxAttributeAge` pattern: a null/unset sentinel causes the entire safety check to be skipped.

---

### Finding Description

In `_updateRsETHPrice()`, two critical safety checks share the same flawed guard:

**Upside guard** (lines 256–257):
```solidity
bool isPriceIncreaseOffLimit =
    pricePercentageLimit > 0 && priceDifference > pricePercentageLimit.mulWad(highestRsethPrice);
``` [1](#0-0) 

**Downside guard** (lines 273–274):
```solidity
bool isPriceDecreaseOffLimit =
    pricePercentageLimit > 0 && diff > pricePercentageLimit.mulWad(highestRsethPrice);
``` [2](#0-1) 

When `pricePercentageLimit == 0`:

- `isPriceIncreaseOffLimit` is always `false` → the `PriceAboveDailyThreshold` revert is never reached, so **any unprivileged caller** can push `rsETHPrice` to any value the oracle supports without restriction.
- `isPriceDecreaseOffLimit` is always `false` → the auto-pause block (lines 278–281) is never reached, so **a catastrophic price drop never triggers the protocol pause**.

`pricePercentageLimit` is a plain storage variable initialized to `0` by default: [3](#0-2) 

`setPricePercentageLimit` accepts any value including `0` with no validation: [4](#0-3) 

`updateRSETHPrice()` is a public, permissionless function: [5](#0-4) 

---

### Impact Explanation

**Downside — auto-pause bypass (High: theft of unclaimed yield / temporary fund freeze):**

When `pricePercentageLimit == 0`, a significant rsETH price drop (e.g., caused by EigenLayer slashing, a NodeDelegator accounting error, or a temporary oracle deviation) does not trigger the intended protocol pause:

```solidity
if (isPriceDecreaseOffLimit) {
    if (!lrtDepositPool.paused()) lrtDepositPool.pause();
    if (!withdrawalManager.paused()) withdrawalManager.pause();
    _pause();
    return;
}
``` [6](#0-5) 

The protocol continues accepting deposits at the depressed `rsETHPrice`. Because `getRsETHAmountToMint` divides by `rsETHPrice`:

```solidity
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
``` [7](#0-6) 

a lower `rsETHPrice` mints proportionally more rsETH per unit of deposited asset. When the price recovers, these over-minted shares dilute existing holders, constituting theft of unclaimed yield.

**Upside — role bypass (Medium: auth bypass):**

When `pricePercentageLimit == 0`, the `PriceAboveDailyThreshold` revert that restricts large price increases to managers is never reached: [8](#0-7) 

Any unprivileged EOA can call `updateRSETHPrice()` and commit an arbitrarily large price increase to storage, bypassing the manager-only gate.

---

### Likelihood Explanation

`pricePercentageLimit` is `0` by default on every fresh deployment and after any admin call to `setPricePercentageLimit(0)`. There is no constructor or initializer that sets a non-zero value, and no validation prevents resetting it to `0`. The window during which the protection is absent is therefore the entire period from deployment until the admin explicitly configures the limit — and any subsequent period after it is reset. This is a realistic, non-adversarial condition.

---

### Recommendation

Treat `pricePercentageLimit == 0` as "limit not configured" and either revert or skip the price update, mirroring the fix in the referenced report:

```solidity
// Before (bypassed when pricePercentageLimit == 0):
bool isPriceDecreaseOffLimit =
    pricePercentageLimit > 0 && diff > pricePercentageLimit.mulWad(highestRsethPrice);

// After (treat zero limit as "always off-limit" or revert):
if (pricePercentageLimit == 0) revert PricePercentageLimitNotSet();
bool isPriceDecreaseOffLimit = diff > pricePercentageLimit.mulWad(highestRsethPrice);
```

Apply the same fix to the upside guard. Additionally, add a non-zero validation to `setPricePercentageLimit` and set a safe default in the initializer.

---

### Proof of Concept

1. Deploy `LRTOracle` without calling `setPricePercentageLimit` (or call `setPricePercentageLimit(0)`). `pricePercentageLimit` is `0`.
2. A slashing event reduces the ETH value held by a `NodeDelegator`, causing `_getTotalEthInProtocol()` to return a value significantly lower than `previousTVL`.
3. Any unprivileged address calls `updateRSETHPrice()`.
4. Inside `_updateRsETHPrice()`, `newRsETHPrice < highestRsethPrice` is true and `diff` is large, but `isPriceDecreaseOffLimit = (0 > 0) && … = false`. The auto-pause block is skipped entirely.
5. `rsETHPrice` is updated to the depressed value and the function returns normally.
6. An attacker immediately calls `LRTDepositPool.depositAsset()` or `depositETH()`. Because `rsETHPrice` is now lower, `getRsETHAmountToMint` mints more rsETH per deposited asset than the attacker's fair share.
7. When the price recovers (e.g., slashing resolved, oracle corrected), the attacker's over-minted rsETH redeems for more underlying than was deposited, extracting yield from existing holders.

### Citations

**File:** contracts/LRTOracle.sol (L29-29)
```text
    uint256 public pricePercentageLimit;
```

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L125-127)
```text
    function setPricePercentageLimit(uint256 _pricePercentageLimit) external onlyLRTAdmin {
        pricePercentageLimit = _pricePercentageLimit;
        emit PricePercentageLimitUpdate(_pricePercentageLimit);
```

**File:** contracts/LRTOracle.sol (L256-257)
```text
            bool isPriceIncreaseOffLimit =
                pricePercentageLimit > 0 && priceDifference > pricePercentageLimit.mulWad(highestRsethPrice);
```

**File:** contracts/LRTOracle.sol (L260-265)
```text
            if (isPriceIncreaseOffLimit) {
                // if sender has a manager role, this doesn't revert.
                // if not, it reverts as price went above the threshold
                if (!IAccessControl(address(lrtConfig)).hasRole(LRTConstants.MANAGER, msg.sender)) {
                    revert PriceAboveDailyThreshold();
                }
```

**File:** contracts/LRTOracle.sol (L273-274)
```text
            bool isPriceDecreaseOffLimit =
                pricePercentageLimit > 0 && diff > pricePercentageLimit.mulWad(highestRsethPrice);
```

**File:** contracts/LRTOracle.sol (L277-282)
```text
            if (isPriceDecreaseOffLimit) {
                if (!lrtDepositPool.paused()) lrtDepositPool.pause();
                if (!withdrawalManager.paused()) withdrawalManager.pause();
                _pause();
                return;
            }
```

**File:** contracts/LRTDepositPool.sol (L520-520)
```text
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```
