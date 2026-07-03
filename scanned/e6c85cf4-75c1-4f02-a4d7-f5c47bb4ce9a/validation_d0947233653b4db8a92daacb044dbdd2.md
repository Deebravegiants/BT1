### Title
Stale `rsETHPrice` After Asset Oracle Address Change Allows Excess rsETH Minting - (`contracts/LRTOracle.sol`)

---

### Summary

`LRTOracle.updatePriceOracleFor()` replaces an asset's price oracle address without first calling `updateRSETHPrice()` to sync the cached `rsETHPrice` storage variable. After the oracle swap, `getAssetPrice(asset)` immediately returns the new oracle's live price, while `rsETHPrice` still reflects the old oracle's prices. `LRTDepositPool.getRsETHAmountToMint()` divides the live asset price by the stale `rsETHPrice`, so any depositor who transacts in the window between the oracle change and the next `updateRSETHPrice()` call receives a mis-priced rsETH amount.

---

### Finding Description

`LRTOracle` stores the rsETH/ETH exchange rate as a cached storage variable `rsETHPrice` (line 28). This value is only updated when `_updateRsETHPrice()` is explicitly called (line 313). The asset-level oracle address is changed by `updatePriceOracleFor()` (lines 113–118) or `updatePriceOracleForValidated()` (lines 101–108), neither of which calls `_updateRsETHPrice()` first.

```solidity
// LRTOracle.sol lines 113-118
function updatePriceOracleFor(address asset, address priceOracle) public onlyLRTAdmin {
    if (lrtConfig.isSupportedAsset(asset)) {
        UtilLib.checkNonZeroAddress(priceOracle);
    }
    assetPriceOracle[asset] = priceOracle;   // oracle swapped; rsETHPrice NOT synced
    emit AssetPriceOracleUpdate(asset, priceOracle);
}
```

After the swap, `getAssetPrice(asset)` reads live from the new oracle:

```solidity
// LRTOracle.sol line 157
return IPriceFetcher(assetPriceOracle[asset]).getAssetPrice(asset);
```

But `LRTDepositPool.getRsETHAmountToMint()` divides by the stale cached value:

```solidity
// LRTDepositPool.sol line 520
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```

**Concrete desync scenario:**

1. stETH oracle currently returns 1.05 ETH/stETH. `rsETHPrice` is cached at `P_old`, computed using that price.
2. Admin calls `updatePriceOracleFor(stETH, newOracle)`. The new oracle returns 1.10 ETH/stETH.
3. `rsETHPrice` is still `P_old` (should now be `P_new > P_old` because the protocol's total ETH value increased).
4. A depositor calls `depositAsset(stETH, amount, ...)`. They receive `(amount × 1.10) / P_old` rsETH.
5. The correct amount (with a synced price) would be `(amount × 1.10) / P_new`, which is smaller.
6. The depositor receives excess rsETH, diluting all existing rsETH holders.

The same desync applies in reverse for `LRTWithdrawalManager._createUnlockParams()`, which also reads `lrtOracle.rsETHPrice()` directly.

---

### Impact Explanation

Existing rsETH holders suffer dilution: the excess rsETH minted to the attacker represents a proportional reduction in the backing per rsETH share. This is a theft of accrued yield from all current holders. The magnitude scales with (a) the price delta between old and new oracle and (b) the weight of the affected asset in total protocol TVL. For a dominant asset like stETH, the impact can be material.

**Impact classification:** High — theft of unclaimed yield (dilution of existing rsETH holders' backing).

---

### Likelihood Explanation

Oracle address changes are routine admin operations (e.g., migrating from one Chainlink feed to another, or switching from `ChainlinkPriceOracle` to a new adapter). The window between `updatePriceOracleFor()` and the next `updateRSETHPrice()` call is publicly observable on-chain. A MEV bot or attacker watching the mempool can sandwich the oracle-change transaction with a large deposit, exploiting the stale price in the same block. No special permissions are required for the deposit itself.

---

### Recommendation

Call `_updateRsETHPrice()` (or `updateRSETHPrice()`) inside `updatePriceOracleFor()` before replacing the oracle address, analogous to the fix recommended in M-4 (`checkHatToggle()` before `changeHatToggle()`):

```solidity
function updatePriceOracleFor(address asset, address priceOracle) public onlyLRTAdmin {
    if (lrtConfig.isSupportedAsset(asset)) {
        UtilLib.checkNonZeroAddress(priceOracle);
    }
    _updateRsETHPrice();          // sync cached price before oracle swap
    assetPriceOracle[asset] = priceOracle;
    emit AssetPriceOracleUpdate(asset, priceOracle);
}
```

Apply the same fix to `updatePriceOracleForValidated()`.

---

### Proof of Concept

1. Protocol state: stETH oracle returns 1.05 ETH/stETH; `rsETHPrice` = 1.05e18 (1:1 for simplicity, 100% stETH TVL).
2. Admin broadcasts `updatePriceOracleFor(stETH, newOracle)` where `newOracle.getAssetPrice(stETH)` returns 1.10e18.
3. Attacker front-runs or immediately follows with `depositAsset(stETH, 1e18, 0, "")`.
4. `getRsETHAmountToMint` computes: `(1e18 × 1.10e18) / 1.05e18 ≈ 1.0476e18` rsETH.
5. Correct amount (after syncing): `(1e18 × 1.10e18) / 1.10e18 = 1.0e18` rsETH.
6. Attacker receives ~4.76% excess rsETH, diluting all existing holders by that proportion.

**Key file references:** [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

### Citations

**File:** contracts/LRTOracle.sol (L28-28)
```text
    uint256 public override rsETHPrice;
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

**File:** contracts/LRTOracle.sol (L113-118)
```text
    function updatePriceOracleFor(address asset, address priceOracle) public onlyLRTAdmin {
        if (lrtConfig.isSupportedAsset(asset)) {
            UtilLib.checkNonZeroAddress(priceOracle);
        }
        assetPriceOracle[asset] = priceOracle;
        emit AssetPriceOracleUpdate(asset, priceOracle);
```

**File:** contracts/LRTOracle.sol (L311-313)
```text
        }

        rsETHPrice = newRsETHPrice;
```

**File:** contracts/LRTDepositPool.sol (L515-521)
```text
        // setup oracle contract
        address lrtOracleAddress = lrtConfig.getContract(LRTConstants.LRT_ORACLE);
        ILRTOracle lrtOracle = ILRTOracle(lrtOracleAddress);

        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
    }
```
