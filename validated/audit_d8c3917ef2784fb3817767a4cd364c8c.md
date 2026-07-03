### Title
Missing Zero-Price Check in `SfrxETHPriceOracle.getAssetPrice()` Enables Division-by-Zero DoS and Zero-Mint Fund Loss in `LRTDepositPool` - (File: contracts/oracles/SfrxETHPriceOracle.sol)

---

### Summary

`SfrxETHPriceOracle.getAssetPrice()` returns the result of `ISfrxETH.pricePerShare()` directly with no zero-value guard. If `pricePerShare()` ever returns `0`, the raw zero propagates into `LRTDepositPool` where it is used both as a divisor (causing a division-by-zero revert, i.e., DoS) and as a multiplicand (causing `getRsETHAmountToMint` to return `0`, meaning a depositor's sfrxETH is accepted but `0` rsETH is minted in return).

---

### Finding Description

`SfrxETHPriceOracle.getAssetPrice()` is a thin wrapper that calls `pricePerShare()` on the sfrxETH contract and returns the result verbatim:

```solidity
// contracts/oracles/SfrxETHPriceOracle.sol L35-41
function getAssetPrice(address asset) external view returns (uint256) {
    if (asset != sfrxETHContractAddress) {
        revert InvalidAsset();
    }
    return ISfrxETH(sfrxETHContractAddress).pricePerShare();
}
```

There is no `require(price > 0)` or equivalent guard. [1](#0-0) 

`LRTOracle.getAssetPrice()` delegates directly to this oracle without adding any zero check of its own:

```solidity
// contracts/LRTOracle.sol L156-158
function getAssetPrice(address asset) public view onlySupportedOracle(asset) returns (uint256) {
    return IPriceFetcher(assetPriceOracle[asset]).getAssetPrice(asset);
}
``` [2](#0-1) 

The zero then reaches two dangerous sites in `LRTDepositPool`:

**Site 1 — Division by zero (DoS):**
```solidity
// contracts/LRTDepositPool.sol L541
return ethPricePerUint * ethAmountToSend / lrtOracle.getAssetPrice(toAsset);
```
If `toAsset` is sfrxETH and `getAssetPrice` returns `0`, Solidity 0.8 reverts with a division-by-zero panic. [3](#0-2) 

**Site 2 — Zero rsETH minted (fund loss):**
```solidity
// contracts/LRTDepositPool.sol L520
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```
If `getAssetPrice(sfrxETH)` returns `0`, the numerator collapses to `0` and `rsethAmountToMint = 0`. A depositor's sfrxETH is transferred in, but `0` rsETH is minted back. [4](#0-3) 

Note that `updatePriceOracleForValidated()` does perform a one-time sanity check at oracle registration (`price > 1e16`), but this check is not repeated on every call and does not protect against a price that drifts to `0` after registration. Furthermore, `updatePriceOracleFor()` (also admin-callable) performs **no** price validation at all. [5](#0-4) 

By contrast, `ChainlinkOracleForRSETHPoolCollateral.getRate()` correctly guards against a zero/negative price with `if (ethPrice <= 0) revert InvalidPrice()`, demonstrating the pattern the project already uses elsewhere but omitted in `SfrxETHPriceOracle`. [6](#0-5) 

---

### Impact Explanation

- **DoS path**: Any call to `LRTDepositPool.getSwapETHToAssetReturnAmount(sfrxETH, amount)` reverts with a division-by-zero panic, freezing the ETH-to-sfrxETH swap quoting path.
- **Fund-loss path**: A depositor calling the sfrxETH deposit path receives `0` rsETH while their sfrxETH is retained by the pool — a direct loss of deposited principal.

Mapped to the allowed scope: **Medium — Temporary freezing of funds** (DoS path) and potentially **Critical — Direct theft of user funds** (zero-mint path, depending on whether the deposit function enforces a non-zero rsETH minimum).

---

### Likelihood Explanation

`pricePerShare()` on the live sfrxETH contract is extremely unlikely to return `0` under normal operation. However:
- The missing guard is a code-level defect that violates the defensive-programming contract the project applies to every other oracle adapter.
- A future upgrade to the sfrxETH contract, a temporary edge-case during initialization, or a misconfigured oracle address could surface the zero value.
- The impact when triggered is immediate and requires no attacker — any depositor or swap caller triggers it passively.

Likelihood: **Low**. Impact: **Medium–Critical**. Overall: **Medium**.

---

### Recommendation

Add a zero-price guard inside `SfrxETHPriceOracle.getAssetPrice()`, mirroring the pattern already used in `ChainlinkOracleForRSETHPoolCollateral`:

```solidity
function getAssetPrice(address asset) external view returns (uint256) {
    if (asset != sfrxETHContractAddress) revert InvalidAsset();
    uint256 price = ISfrxETH(sfrxETHContractAddress).pricePerShare();
    if (price == 0) revert InvalidPrice();
    return price;
}
```

Additionally, add a post-call zero check in `LRTOracle.getAssetPrice()` as a belt-and-suspenders defence for all oracle adapters:

```solidity
function getAssetPrice(address asset) public view onlySupportedOracle(asset) returns (uint256) {
    uint256 price = IPriceFetcher(assetPriceOracle[asset]).getAssetPrice(asset);
    if (price == 0) revert InvalidAssetPrice();
    return price;
}
```

---

### Proof of Concept

1. Assume `pricePerShare()` on the sfrxETH contract returns `0` (e.g., edge-case, upgrade, or misconfiguration).
2. Any caller invokes `LRTDepositPool.getSwapETHToAssetReturnAmount(sfrxETH, 1 ether)`.
3. Execution reaches `LRTOracle.getAssetPrice(sfrxETH)` → `SfrxETHPriceOracle.getAssetPrice(sfrxETH)` → returns `0`.
4. `LRTDepositPool` executes `1e18 * 1 ether / 0` → Solidity 0.8 panic revert. All callers of this function are DoS'd.
5. Separately, a depositor calls the sfrxETH deposit path. `getRsETHAmountToMint(sfrxETH, amount)` computes `(amount * 0) / rsETHPrice = 0`. The deposit proceeds, sfrxETH is transferred in, and `0` rsETH is minted to the depositor.

### Citations

**File:** contracts/oracles/SfrxETHPriceOracle.sol (L35-41)
```text
    function getAssetPrice(address asset) external view returns (uint256) {
        if (asset != sfrxETHContractAddress) {
            revert InvalidAsset();
        }

        return ISfrxETH(sfrxETHContractAddress).pricePerShare();
    }
```

**File:** contracts/LRTOracle.sol (L101-118)
```text
    function updatePriceOracleForValidated(address asset, address priceOracle) external onlyLRTAdmin {
        // Sanity check: oracle price must have precision between 1e16 and 1e19
        uint256 price = IPriceFetcher(priceOracle).getAssetPrice(asset);
        if (price > 1e19 || price < 1e16) {
            revert InvalidPriceOracle();
        }
        updatePriceOracleFor(asset, priceOracle);
    }

    /// @dev add/update the price oracle of any asset
    /// @dev only onlyLRTAdmin is allowed
    /// @param asset asset address for which oracle price needs to be added/updated
    function updatePriceOracleFor(address asset, address priceOracle) public onlyLRTAdmin {
        if (lrtConfig.isSupportedAsset(asset)) {
            UtilLib.checkNonZeroAddress(priceOracle);
        }
        assetPriceOracle[asset] = priceOracle;
        emit AssetPriceOracleUpdate(asset, priceOracle);
```

**File:** contracts/LRTOracle.sol (L156-158)
```text
    function getAssetPrice(address asset) public view onlySupportedOracle(asset) returns (uint256) {
        return IPriceFetcher(assetPriceOracle[asset]).getAssetPrice(asset);
    }
```

**File:** contracts/LRTDepositPool.sol (L519-521)
```text
        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
    }
```

**File:** contracts/LRTDepositPool.sol (L539-541)
```text
        uint256 ethPricePerUint = 1e18;

        return ethPricePerUint * ethAmountToSend / lrtOracle.getAssetPrice(toAsset);
```

**File:** contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol (L30-33)
```text
        if (answeredInRound < roundID) revert StalePrice();
        if (timestamp == 0) revert IncompleteRound();
        if (ethPrice <= 0) revert InvalidPrice();

```
