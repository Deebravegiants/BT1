### Title
Unbounded `pricePercentageLimit` in `LRTOracle` Disables Both Upside and Downside Price-Protection Guards When Set to Zero — (File: `contracts/LRTOracle.sol`)

---

### Summary

`LRTOracle.setPricePercentageLimit()` accepts any value, including 0, with no lower or upper bound validation. Because `pricePercentageLimit` is also never initialized in `initialize()`, it defaults to 0 from the moment of deployment. When the value is 0, both the upside price-threshold revert and the downside auto-pause mechanism are silently bypassed inside `_updateRsETHPrice()`, which is a **public** function callable by anyone.

---

### Finding Description

`setPricePercentageLimit()` writes the caller-supplied value directly to storage with no validation:

```solidity
function setPricePercentageLimit(uint256 _pricePercentageLimit) external onlyLRTAdmin {
    pricePercentageLimit = _pricePercentageLimit;
    emit PricePercentageLimitUpdate(_pricePercentageLimit);
}
``` [1](#0-0) 

The `initialize()` function never sets `pricePercentageLimit`, so it starts at the Solidity default of `0`:

```solidity
function initialize(address lrtConfigAddr) external initializer {
    UtilLib.checkNonZeroAddress(lrtConfigAddr);
    lrtConfig = ILRTConfig(lrtConfigAddr);
    emit UpdatedLRTConfig(lrtConfigAddr);
}
``` [2](#0-1) 

Inside `_updateRsETHPrice()`, both the upside and downside guards are gated on `pricePercentageLimit > 0`:

```solidity
bool isPriceIncreaseOffLimit =
    pricePercentageLimit > 0 && priceDifference > pricePercentageLimit.mulWad(highestRsethPrice);
```

```solidity
bool isPriceDecreaseOffLimit =
    pricePercentageLimit > 0 && diff > pricePercentageLimit.mulWad(highestRsethPrice);
``` [3](#0-2) [4](#0-3) 

When `pricePercentageLimit == 0`, both expressions short-circuit to `false`, so:

- **Upside**: any non-manager caller can push an arbitrarily large price increase through the public `updateRSETHPrice()` without reverting.
- **Downside**: a significant price drop never triggers the auto-pause of `LRTDepositPool` and `LRTWithdrawalManager`.

`updateRSETHPrice()` is unrestricted:

```solidity
function updateRSETHPrice() public whenNotPaused {
    _updateRsETHPrice();
}
``` [5](#0-4) 

The downside auto-pause path that is bypassed:

```solidity
if (isPriceDecreaseOffLimit) {
    if (!lrtDepositPool.paused()) lrtDepositPool.pause();
    if (!withdrawalManager.paused()) withdrawalManager.pause();
    _pause();
    return;
}
``` [6](#0-5) 

---

### Impact Explanation

With `pricePercentageLimit = 0` (the default state from deployment), the downside auto-pause is permanently disabled. If the rsETH price drops significantly — for example, due to an EigenLayer slashing event — `updateRSETHPrice()` will accept the new lower price without pausing the protocol. Users can then deposit at the depressed price, receiving more rsETH per ETH than the protocol's accounting supports. When the price recovers, those users profit at the expense of existing rsETH holders whose share value is diluted. This matches the **Low** impact class: *contract fails to deliver promised returns* (existing holders receive less yield than entitled to).

---

### Likelihood Explanation

The likelihood is **medium**. The vulnerable state (`pricePercentageLimit == 0`) is the **default** from deployment — no admin error is required. The protection is absent until an admin explicitly calls `setPricePercentageLimit` with a non-zero value. Additionally, an admin who later calls `setPricePercentageLimit(0)` — perhaps intending to "disable the limit" — silently re-enters the vulnerable state, because the function accepts 0 without complaint. The analog from the reference report is exact: a parameter with no lower-bound check that, when set to 0, silently disables a critical protocol mechanism.

---

### Recommendation

1. Add a lower bound (e.g., `>= 1e14`, representing 0.01%) and an upper bound (`<= 1e18`, representing 100%) inside `setPricePercentageLimit()`:

```solidity
function setPricePercentageLimit(uint256 _pricePercentageLimit) external onlyLRTAdmin {
    if (_pricePercentageLimit == 0 || _pricePercentageLimit > 1e18) revert InvalidPricePercentageLimit();
    pricePercentageLimit = _pricePercentageLimit;
    emit PricePercentageLimitUpdate(_pricePercentageLimit);
}
```

2. Initialize `pricePercentageLimit` to a sensible default (e.g., `5e16` = 5%) inside `initialize()` so the protection is active from the first price update.

---

### Proof of Concept

1. `LRTOracle` is deployed. `pricePercentageLimit` is `0` (never initialized).
2. An EigenLayer slashing event reduces the total ETH in the protocol by 30%, causing `newRsETHPrice` to be 30% below `highestRsethPrice`.
3. Any external caller invokes `updateRSETHPrice()` (public, no role required).
4. Inside `_updateRsETHPrice()`: `isPriceDecreaseOffLimit = (0 > 0) && ...` → `false`.
5. The auto-pause block is skipped; `LRTDepositPool` and `LRTWithdrawalManager` remain unpaused.
6. `rsETHPrice` is updated to the slashed value.
7. A depositor calls `LRTDepositPool.depositAsset()` at the depressed price, minting more rsETH per ETH than the protocol's true backing supports.
8. When the price recovers (e.g., slashing is resolved), the depositor's rsETH is worth more than their deposit, diluting all pre-existing rsETH holders.

### Citations

**File:** contracts/LRTOracle.sol (L64-68)
```text
    function initialize(address lrtConfigAddr) external initializer {
        UtilLib.checkNonZeroAddress(lrtConfigAddr);
        lrtConfig = ILRTConfig(lrtConfigAddr);
        emit UpdatedLRTConfig(lrtConfigAddr);
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
