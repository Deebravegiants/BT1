### Title
Missing Negative Price Guard in `ChainlinkPriceOracle.getAssetPrice()` Enables Inflated rsETH Minting — (File: contracts/oracles/ChainlinkPriceOracle.sol)

---

### Summary

`ChainlinkPriceOracle.getAssetPrice()` casts the raw `int256` Chainlink answer directly to `uint256` without first checking that the value is positive. A negative return from the feed wraps to a near-`type(uint256).max` value, producing a wildly inflated asset price. The same codebase contains a second Chainlink wrapper (`ChainlinkOracleForRSETHPoolCollateral`) that correctly guards against this with `if (ethPrice <= 0) revert InvalidPrice()`. The missing check is the direct analog of the removed `require(x != MIN_64x64)` in `unsafe_abs`.

---

### Finding Description

`ChainlinkPriceOracle.getAssetPrice()` reads the raw Chainlink answer and immediately casts it:

```solidity
(, int256 price,,,) = priceFeed.latestRoundData();
return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
``` [1](#0-0) 

There is no guard of the form `require(price > 0)`. If `price` is `-1`, then `uint256(-1)` = `2^256 - 1`, and the returned "price" becomes astronomically large.

The sibling oracle in the same repository does include the guard:

```solidity
if (ethPrice <= 0) revert InvalidPrice();
``` [2](#0-1) 

The inflated price flows directly into deposit minting:

```solidity
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
``` [3](#0-2) 

and into TVL accounting used to update the rsETH price:

```solidity
totalETHInProtocol += totalAssetAmt.mulWad(assetER);
``` [4](#0-3) 

---

### Impact Explanation

If Chainlink returns a negative `int256` answer (possible during circuit-breaker events, feed misconfiguration, or extreme market conditions), `uint256(price)` wraps to a value near `type(uint256).max`. A depositor calling `depositAsset()` would receive an amount of rsETH proportional to this inflated price — effectively minting rsETH backed by near-zero real collateral. This constitutes direct theft of existing depositors' funds, as the newly minted rsETH dilutes the backing of all outstanding rsETH.

**Impact: Critical — direct theft of user funds.**

---

### Likelihood Explanation

Chainlink's `latestRoundData()` returns `int256`, which is signed by design. While mainstream LST/ETH feeds do not normally return negative values, the type contract permits it, and defensive validation is standard practice (as demonstrated by the sibling oracle in this codebase). The missing check is a code-level omission, not a theoretical edge case. The `updatePriceOracleForValidated()` sanity check only runs at oracle registration time and does not protect against a price that turns negative after registration. [5](#0-4) 

**Likelihood: Low** (requires Chainlink to return a non-positive answer), but the code-level root cause is entirely within the protocol's own contract.

---

### Recommendation

Add a positivity guard in `ChainlinkPriceOracle.getAssetPrice()` before the cast, mirroring the pattern already used in `ChainlinkOracleForRSETHPoolCollateral`:

```solidity
(, int256 price,,,) = priceFeed.latestRoundData();
require(price > 0, "Invalid price");
return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
``` [6](#0-5) 

---

### Proof of Concept

1. Chainlink feed for a supported LST returns `price = -1` (e.g., due to a circuit-breaker or feed error).
2. `ChainlinkPriceOracle.getAssetPrice(lstAddress)` computes `uint256(-1) * 1e18 / decimals_factor` ≈ `type(uint256).max`.
3. Attacker calls `LRTDepositPool.depositAsset(lstAddress, 1 wei, 0)`.
4. `getRsETHAmountToMint` returns `(1 * type(uint256).max) / rsETHPrice` — an astronomically large rsETH amount.
5. Protocol mints that rsETH to the attacker, who then redeems it against the real ETH backing of all other depositors. [6](#0-5) [7](#0-6)

### Citations

**File:** contracts/oracles/ChainlinkPriceOracle.sol (L49-55)
```text
    function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
        AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);

        (, int256 price,,,) = priceFeed.latestRoundData();

        return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
    }
```

**File:** contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol (L32-32)
```text
        if (ethPrice <= 0) revert InvalidPrice();
```

**File:** contracts/LRTDepositPool.sol (L506-521)
```text
    function getRsETHAmountToMint(
        address asset,
        uint256 amount
    )
        public
        view
        override
        returns (uint256 rsethAmountToMint)
    {
        // setup oracle contract
        address lrtOracleAddress = lrtConfig.getContract(LRTConstants.LRT_ORACLE);
        ILRTOracle lrtOracle = ILRTOracle(lrtOracleAddress);

        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L101-107)
```text
    function updatePriceOracleForValidated(address asset, address priceOracle) external onlyLRTAdmin {
        // Sanity check: oracle price must have precision between 1e16 and 1e19
        uint256 price = IPriceFetcher(priceOracle).getAssetPrice(asset);
        if (price > 1e19 || price < 1e16) {
            revert InvalidPriceOracle();
        }
        updatePriceOracleFor(asset, priceOracle);
```

**File:** contracts/LRTOracle.sol (L343-343)
```text
            totalETHInProtocol += totalAssetAmt.mulWad(assetER);
```
