### Title
`LRTOracle._updateRsETHPrice()` Does Not Validate `newRsETHPrice` Against a Minimum Price — (File: `contracts/LRTOracle.sol`)

---

### Summary

`LRTOracle._updateRsETHPrice()` computes a new rsETH/ETH exchange rate and stores it in `rsETHPrice` without validating it against any minimum price floor. The only downside protection present is entirely conditional on `pricePercentageLimit > 0`, a variable that defaults to `0` and is never set in `initialize()`. This mirrors the GDACurve pattern exactly: a separate validation path (`updatePriceOracleForValidated`) enforces price bounds, but the live price-update path (`_updateRsETHPrice`) does not.

---

### Finding Description

`LRTOracle._updateRsETHPrice()` is the core function that recomputes and stores the rsETH/ETH exchange rate used for all minting and withdrawal accounting across the protocol. [1](#0-0) 

```solidity
uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);
```

The only downside protection is: [2](#0-1) 

```solidity
if (newRsETHPrice < highestRsethPrice) {
    uint256 diff = highestRsethPrice - newRsETHPrice;
    bool isPriceDecreaseOffLimit =
        pricePercentageLimit > 0 && diff > pricePercentageLimit.mulWad(highestRsethPrice);
    if (isPriceDecreaseOffLimit) {
        // pause and return
    }
}
```

`pricePercentageLimit` is declared as a plain `uint256` storage variable: [3](#0-2) 

and is **never set** in `initialize()`: [4](#0-3) 

It can only be set by admin via `setPricePercentageLimit()`: [5](#0-4) 

When `pricePercentageLimit == 0` (the default), `isPriceDecreaseOffLimit` is always `false` regardless of how far the price drops, and `rsETHPrice` is unconditionally written to `newRsETHPrice` at line 313: [6](#0-5) 

By contrast, `updatePriceOracleForValidated` — the "validated" oracle-registration path — does enforce a price range check (1e16 to 1e19): [7](#0-6) 

This is the exact structural analog to the GDACurve bug: a validation function exists, but the live update path does not call it.

The entry point is the **public, permissionless** `updateRSETHPrice()`: [8](#0-7) 

Any external caller can trigger the price update.

The computed `newRsETHPrice` feeds directly into rsETH minting: [9](#0-8) 

```solidity
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```

If `rsETHPrice` is driven to a very small value, this division yields a disproportionately large rsETH mint amount for any depositor.

---

### Impact Explanation

If `pricePercentageLimit` is 0 (the default deployment state) and the protocol's TVL drops significantly — due to EigenLayer slashing, a bug in TVL accounting via `_getTotalEthInProtocol()`, or a supported asset oracle returning a low price — `newRsETHPrice` can be written to `rsETHPrice` at an arbitrarily low value with no floor protection. Any depositor who calls `depositETH` or `depositAsset` while `rsETHPrice` is near-zero receives a massively inflated rsETH amount relative to their deposit, diluting all existing rsETH holders and allowing the new depositor to claim a disproportionate share of the protocol's underlying assets upon withdrawal.

**Impact class**: Low — contract fails to deliver promised returns to existing rsETH holders (dilution without recourse). Escalates toward Medium/Critical if the TVL drop is caused by an accounting bug rather than genuine slashing, since in that case the underlying assets still exist and can be drained.

---

### Likelihood Explanation

`pricePercentageLimit` defaults to 0 and requires an explicit admin call to set. Until it is set, there is zero downside price protection. The trigger (TVL drop) can arise from EigenLayer slashing events, oracle price drops for supported LSTs, or accounting bugs in `_getTotalEthInProtocol()`. The public `updateRSETHPrice()` function means any actor can crystallize the low price into storage at any time. Likelihood is **Low** for catastrophic slashing scenarios but **Medium** for partial slashing or oracle-driven TVL underestimation while `pricePercentageLimit` remains unset.

---

### Recommendation

Add an absolute minimum price check inside `_updateRsETHPrice()` before writing `rsETHPrice`, analogous to the `MIN_PRICE` check recommended for GDACurve:

```solidity
uint256 constant MIN_RSETH_PRICE = 1 ether; // rsETH should never trade below 1 ETH backing

// After computing newRsETHPrice:
if (newRsETHPrice < MIN_RSETH_PRICE) {
    // pause and return, or revert
    if (!lrtDepositPool.paused()) lrtDepositPool.pause();
    if (!withdrawalManager.paused()) withdrawalManager.pause();
    _pause();
    return;
}
```

Additionally, `initialize()` should set a non-zero default for `pricePercentageLimit` so that downside protection is active from deployment without requiring a separate admin transaction.

---

### Proof of Concept

1. Protocol is deployed. `pricePercentageLimit` is `0` (default, never set in `initialize()`).
2. EigenLayer slashing event reduces the ETH value held by `NodeDelegator` contracts.
3. `_getTotalEthInProtocol()` returns a significantly reduced value.
4. Anyone calls `updateRSETHPrice()`.
5. `newRsETHPrice = (reducedTVL).divWad(rsethSupply)` — e.g., drops from `1.05e18` to `0.1e18`.
6. `isPriceDecreaseOffLimit = (0 > 0) && ...` → `false`. No pause, no revert.
7. `rsETHPrice = 0.1e18` is written to storage.
8. Attacker calls `depositETH{value: 1 ether}(0, "")`.
9. `rsethAmountToMint = (1e18 * 1e18) / 0.1e18 = 10e18` — attacker receives 10 rsETH for 1 ETH.
10. Attacker's rsETH now represents a claim on 10× the ETH they deposited, at the expense of existing holders. [2](#0-1) [6](#0-5) [9](#0-8)

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

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L101-108)
```text
    function updatePriceOracleForValidated(address asset, address priceOracle) external onlyLRTAdmin {
        // Sanity check: oracle price must have precision between 1e16 and 1e19
        uint256 price = IPriceFetcher(priceOracle).getAssetPrice(asset);
        if (price > 1e19 || price < 1e16) {
            revert InvalidPriceOracle();
        }
        updatePriceOracleFor(asset, priceOracle);
    }
```

**File:** contracts/LRTOracle.sol (L125-128)
```text
    function setPricePercentageLimit(uint256 _pricePercentageLimit) external onlyLRTAdmin {
        pricePercentageLimit = _pricePercentageLimit;
        emit PricePercentageLimitUpdate(_pricePercentageLimit);
    }
```

**File:** contracts/LRTOracle.sol (L249-250)
```text
        // compute new rsETH price based on total ETH minus fee
        uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);
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

**File:** contracts/LRTOracle.sol (L313-313)
```text
        rsETHPrice = newRsETHPrice;
```

**File:** contracts/LRTDepositPool.sol (L519-520)
```text
        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```
